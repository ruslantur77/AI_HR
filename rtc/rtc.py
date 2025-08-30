import asyncio
import base64
import json
import logging
import time
from fractions import Fraction
from typing import Set

import httpx
import numpy as np
import webrtcvad
import websockets
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
from av import AudioFrame, AudioResampler

from config import config

logger = logging.getLogger("webrtc")

pcs: Set[RTCPeerConnection] = set()
relay = MediaRelay()


class AudioProcessor:
    def __init__(self, tts_queue: asyncio.Queue):
        self.resampler = AudioResampler(format="s16", layout="mono", rate=16000)
        self.ws: websockets.ClientConnection | None = None
        self.tts_queue = tts_queue
        self.vad = webrtcvad.Vad(2)
        self.silence_frames = 0
        self.max_silence_frames = 50  # 50 * 20мс = 1 сек тишины → конец utterance
        self.text_buffer = []  # Буфер для накопления текста

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

                        if self.silence_frames > self.max_silence_frames:
                            if self.text_buffer:
                                full_text = " ".join(self.text_buffer)
                                logger.info("Final utterance: %s", full_text)

                                self.text_buffer.clear()
                            self.silence_frames = 0

            except Exception as e:
                logger.error("Error processing audio frame: %s", e)
                break


async def synthesize_tts(text: str) -> np.ndarray:
    # Пример: генерируем numpy int16 аудио 16kHz
    # Здесь должен быть вызов твоего TTS, возвращающий np.int16
    audio = np.zeros(16000, dtype=np.int16)  # Замените на реальный TTS
    return audio


class TTSAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, tts_queue: asyncio.Queue):
        super().__init__()
        self.tts_queue = tts_queue
        self.buffer = np.zeros(0, dtype=np.int16)
        self.last_pts = 0
        self.tts_queue.put_nowait("")
        self.start_time = time.time()

    async def recv(self):
        # Если буфер пуст, пробуем получить новый текст
        if self.buffer.size == 0:
            try:
                text = await asyncio.wait_for(self.tts_queue.get(), timeout=0.001)
                self.buffer = await synthesize_tts(text)
            except asyncio.TimeoutError:
                self.buffer = np.zeros(320, dtype=np.int16)
            except Exception as e:
                logger.error("Error in TTS: %s", e)
                self.buffer = np.zeros(320, dtype=np.int16)

        frame_data = self.buffer[:320]
        self.buffer = self.buffer[320:]

        frame_data = frame_data[np.newaxis, :]
        frame = AudioFrame.from_ndarray(frame_data, format="s16", layout="mono")
        frame.sample_rate = 16000
        frame.pts = self.last_pts
        frame.time_base = Fraction(1, 16000)
        self.last_pts += frame.samples
        expected_time = frame.pts * frame.time_base
        now = time.time() - self.start_time
        wait = expected_time - now
        if wait > 0:
            await asyncio.sleep(wait)
        return frame


async def create_peer_connection(offer_sdp: str, offer_type: str) -> dict:
    pc = RTCPeerConnection()
    pcs.add(pc)
    tts_queue = asyncio.Queue()

    tts_track = TTSAudioTrack(tts_queue)
    pc.addTrack(tts_track)

    processor = AudioProcessor(tts_queue)

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
