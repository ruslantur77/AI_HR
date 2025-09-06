import asyncio
import base64
import json
import logging
import time
from fractions import Fraction
from typing import Set

import httpx
import numpy as np
import torch
import webrtcvad
import websockets
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from av import AudioFrame, AudioResampler
from scipy.signal import resample

from config import config
from llm import get_response, get_system_instruction
from resources.prompts import INTERVIEW

logger = logging.getLogger("webrtc")

pcs: Set[RTCPeerConnection] = set()
relay = MediaRelay()
tts_model, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_tts",
    language="ru",
    speaker="v4_ru",
)  # type: ignore
tts_model.to(torch.device("cuda"))


class AudioProcessor:
    def __init__(self, tts_queue: asyncio.Queue, messages: list):
        self.resampler = AudioResampler(format="s16", layout="mono", rate=16000)
        self.ws: websockets.ClientConnection | None = None
        self.tts_queue = tts_queue
        self.vad = webrtcvad.Vad(2)
        self.silence_frames = 0
        self.max_silence_frames = 50  # 50 * 20мс = 1 сек тишины → конец utterance
        self.text_buffer = []  # Буфер для накопления текста
        self.is_waiting_response = asyncio.Event()
        self.messages = [*messages]

    async def connect_gladia(self):
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.gladia.io/v2/live",
                headers={
                    "Content-Type": "application/json",
                    "X-Gladia-Key": config.GLADIA_API_KEY,
                },
                json={
                    "encoding": "wav/pcm",
                    "sample_rate": 16000,
                    "bit_depth": 16,
                    "channels": 1,
                },
                timeout=30.0,
            )

            if resp.status_code != 201:
                raise RuntimeError(
                    f"Gladia init failed: {resp.status_code} {resp.text}"
                )
            data = resp.json()
            url = data["url"]

        self.ws = await websockets.connect(url)
        asyncio.create_task(self._receive_messages())

    async def _receive_messages(self):
        if not self.ws:
            return
        async for message in self.ws:
            msg = json.loads(message)
            if msg.get("type") == "transcript" and msg.get("data", {}).get("is_final"):
                text = msg["data"]["utterance"]["text"]
                self.text_buffer.append(text)

    async def _send_chunk(self, chunk: np.ndarray):
        if not self.ws:
            await self.connect_gladia()
        if self.is_waiting_response.is_set():
            chunk = np.zeros(320, dtype=np.int16)
        int16_chunk = chunk.astype(np.int16)
        await self.ws.send(  # type: ignore
            json.dumps(
                {
                    "type": "audio_chunk",
                    "data": {
                        "chunk": base64.b64encode(int16_chunk.tobytes()).decode("utf-8")
                    },
                }
            )
        )

    def _is_speech(self, chunk: np.ndarray) -> bool:
        pcm_bytes = chunk.astype(np.int16).tobytes()
        try:
            return self.vad.is_speech(pcm_bytes, 16000)
        except Exception as e:
            logger.error("VAD error: %s", e)
            return False

    async def send_to_tts(self):
        if self.text_buffer:
            self.is_waiting_response.set()
            full_text = " ".join(self.text_buffer)
            logger.info("Final utterance: %s", full_text)

            messages, answer = await get_response(self.messages, full_text, 5000)
            self.messages = messages
            await self.tts_queue.put(synthesize_tts(answer))
            await self.tts_queue.join()
            self.is_waiting_response.clear()
            self.text_buffer.clear()
        self.silence_frames = 0

    async def process(self, track: MediaStreamTrack):
        while True:
            try:
                frame = await track.recv()
                resampled_frames = self.resampler.resample(frame)  # type: ignore
                for resampled_frame in resampled_frames or []:
                    if resampled_frame:
                        audio_samples = resampled_frame.to_ndarray().flatten()

                        if self._is_speech(audio_samples):
                            self.silence_frames = 0
                        else:
                            self.silence_frames += 1
                        await self._send_chunk(audio_samples)

                        if self.is_waiting_response.is_set():
                            continue
                        if self.silence_frames > self.max_silence_frames:
                            asyncio.create_task(self.send_to_tts())

            except Exception as e:
                logger.error("Error processing audio frame: %s", e)
                break


def synthesize_tts(
    text: str,
    target_sample_rate: int = 16000,
) -> np.ndarray:
    print(text)
    audio = tts_model.apply_tts(text=text, speaker="xenia", sample_rate=48000)
    audio_numpy = audio.cpu().numpy().astype("float32")

    num_samples = int(len(audio_numpy) * target_sample_rate / 48000)
    audio_resampled = resample(audio_numpy, num_samples)

    audio_int16 = (audio_resampled * 32767).clip(-32768, 32767).astype("int16")  # type: ignore

    return audio_int16


class TTSAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, tts_queue: asyncio.Queue):
        super().__init__()
        self.tts_queue = tts_queue
        self.buffer = np.zeros(0, dtype=np.int16)
        self.last_pts = 0
        self.sample_rate = 16000
        self.frame_size = 320
        self.start_time = None
        self.tts_started = False

    async def recv(self):
        if self.buffer.size == 0:
            if self.tts_started:
                self.tts_queue.task_done()
                self.tts_started = False
            try:
                self.buffer = await asyncio.wait_for(
                    self.tts_queue.get(), timeout=0.001
                )
                self.tts_started = True
            except asyncio.TimeoutError:
                self.buffer = np.zeros(self.frame_size, dtype=np.int16)
            except Exception as e:
                logger.error("Error in TTS: %s", e)
                self.buffer = np.zeros(self.frame_size, dtype=np.int16)

        frame_data = self.buffer[: self.frame_size]
        self.buffer = self.buffer[self.frame_size :]

        frame_data = frame_data[np.newaxis, :]
        frame = AudioFrame.from_ndarray(frame_data, format="s16", layout="mono")
        frame.sample_rate = self.sample_rate
        frame.pts = self.last_pts
        frame.time_base = Fraction(1, self.sample_rate)
        self.last_pts += frame.samples

        if self.start_time is None:
            self.start_time = time.time()

        expected_time = frame.pts / self.sample_rate
        now = time.time() - self.start_time
        wait = expected_time - now
        if wait > 0:
            await asyncio.sleep(wait)

        return frame


async def create_peer_connection(
    offer_sdp: str, offer_type: str, questions: list[str], welcome_text: str
) -> dict:
    pc = RTCPeerConnection()
    pcs.add(pc)
    tts_queue = asyncio.Queue()

    async def enqueue_text(text, delay):
        await asyncio.sleep(delay)
        await tts_queue.put(synthesize_tts(text))

    asyncio.create_task(enqueue_text(welcome_text, 3))

    tts_track = TTSAudioTrack(tts_queue)
    pc.addTrack(tts_track)

    processor = AudioProcessor(
        tts_queue,
        [
            get_system_instruction(INTERVIEW.format(questions="\n".join(questions))),
            {"role": "hr", "content": welcome_text},
        ],
    )

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            subscribed_track = relay.subscribe(track)
            asyncio.create_task(processor.process(subscribed_track))

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("Connection state is %s", pc.connectionState)
        if pc.connectionState in ("failed", "closed"):
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type=offer_type))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


async def shutdown():
    """
    Закрыть все активные PeerConnections.
    """
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    logger.info("Server shutdown, all peer connections closed.")
