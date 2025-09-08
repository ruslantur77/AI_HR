// src/pages/Screening.jsx
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from '../api/axios';          // ваш инстанс с токеном / baseURL
import './Screening.css';

export default function Screening() {
  const { interviewId } = useParams();      // ← из /screening/:interviewId
  const [mic, setMic] = useState(true);
  const [status, setStatus] = useState('idle');
  const [mics, setMics] = useState([]);
  const [selectedMicId, setSelectedMicId] = useState('');

  const pcRef = useRef(null);
  const streamRef = useRef(null);
  const remoteAudio = useRef(null);
  const navigate = useNavigate();

  /* ---------- чистильщик ---------- */
  const stopEverything = () => {
    if (pcRef.current) {
      pcRef.current.getSenders().forEach(s => s.track && s.track.stop());
      pcRef.current.close();
      pcRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    if (remoteAudio.current?.srcObject) {
      remoteAudio.current.srcObject.getTracks().forEach(t => t.stop());
      remoteAudio.current.srcObject = null;
    }
  };

  /* ---------- инициализация WebRTC ---------- */
  useEffect(() => {
    if (!interviewId) {
      setStatus('error');
      return;
    }

    (async () => {
      setStatus('connecting');
      try {
        const pc = new RTCPeerConnection({
          iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        });

        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { sampleRate: 16000, channelCount: 1, echoCancellation: false }
        });
        stream.getTracks().forEach(tr => pc.addTrack(tr, stream));

        await new Promise(res => {
          if (pc.iceGatheringState === 'complete') res();
          else pc.addEventListener('icegatheringstatechange', () => pc.iceGatheringState === 'complete' && res());
        });

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        /* ---- новый энд-поинт из OpenAPI ---- */
        const { data } = await axios.post(
          `/api/interview/rtc/offer/${interviewId}`,
          { sdp: offer.sdp, type: offer.type }
        );

        await pc.setRemoteDescription(data);

        pcRef.current = pc;
        streamRef.current = stream;

        const audioTrack = stream.getAudioTracks()[0];
        if (audioTrack) setMic(audioTrack.enabled);

        pc.ontrack = e => { remoteAudio.current.srcObject = e.streams[0]; };
        setStatus('active');
      } catch (e) {
        console.error('Ошибка установления соединения:', e);
        setStatus('error');
      }
    })();

    return () => stopEverything();
  }, [interviewId]);

  /* ---------- обновление списка микрофонов ---------- */
  const refreshMics = async () => {
    await navigator.mediaDevices.getUserMedia({ audio: true });
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = devices.filter(d => d.kind === 'audioinput');
    setMics(audioInputs);
    if (!selectedMicId && audioInputs.length) setSelectedMicId(audioInputs[0].deviceId);
  };

  /* ---------- смена микрофона ---------- */
  const changeMic = async (e) => {
    const deviceId = e.target.value;
    setSelectedMicId(deviceId);

    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: { exact: deviceId },
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: false
        }
      });
      const newTrack = newStream.getAudioTracks()[0];
      if (!newTrack) return;

      const sender = pcRef.current.getSenders().find(s => s.track && s.track.kind === 'audio');
      if (sender) await sender.replaceTrack(newTrack);

      const oldTrack = streamRef.current.getAudioTracks()[0];
      if (oldTrack) oldTrack.stop();

      streamRef.current = newStream;
      setMic(newTrack.enabled);
    } catch (err) {
      console.error('Ошибка смены микрофона:', err);
    }
  };

  /* ---------- вкл/выкл микрофон ---------- */
  const toggleMic = () => {
    const audioTrack = streamRef.current?.getAudioTracks()[0];
    if (!audioTrack) return;
    const newState = !audioTrack.enabled;
    audioTrack.enabled = newState;
    setMic(newState);
  };

  /* ---------- завершить звонок ---------- */
  const hangUp = () => {
    stopEverything();
    navigate('/result');
  };

  /* ---------- визуализация уровня ---------- */
  useEffect(() => {
    if (status !== 'active') return;
    const ctx = new AudioContext();
    const analyser = ctx.createAnalyser();
    const src = ctx.createMediaStreamSource(streamRef.current);
    src.connect(analyser);

    const tick = () => {
      const data = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(data);
      const avg = data.reduce((a, b) => a + b) / data.length;
      const sph = document.getElementById('aiSphere');
      if (sph) sph.style.transform = `scale(${1 + avg / 512})`;
      requestAnimationFrame(tick);
    };
    tick();
    return () => ctx.close();
  }, [status]);

  /* ---------- рендер ---------- */
  return (
    <>
      <main className="screening">
        <div className="screening__card">
          <div className="screening__sphere" id="aiSphere" />
          <audio ref={remoteAudio} autoPlay style={{ display: 'none' }} />

          <div className="screening__controls">
            {/* выбор микрофона */}
            <div className="mic-select-wrapper">
              <select
                className="screening__select"
                value={selectedMicId}
                onChange={changeMic}
                disabled={status !== 'active'}
              >
                {mics.map(m => (
                  <option key={m.deviceId} value={m.deviceId}>
                    {m.label || 'Микрофон ' + m.deviceId.slice(0, 5)}
                  </option>
                ))}
              </select>
              <button
                className="screening__btn screening__btn--refresh"
                onClick={refreshMics}
                title="Обновить список"
              >
                ⟳
              </button>
            </div>

            {/* кнопка вкл/выкл мик */}
            <button
              className={`screening__btn ${mic ? 'screening__btn--mic' : 'screening__btn--mic-off'}`}
              onClick={toggleMic}
              disabled={status !== 'active'}
            >
              {mic ? 'Выключить микрофон' : 'Включить микрофон'}
            </button>

            {/* кнопка завершить */}
            <button
              className="screening__btn screening__btn--hangup"
              onClick={hangUp}
              disabled={status === 'idle'}
            >
              Завершить звонок
            </button>
          </div>

          <p className="screening__status">
            {status === 'connecting' && 'Подключение...'}
            {status === 'active' && 'Идёт собеседование'}
            {status === 'error' && 'Ошибка подключения'}
          </p>
        </div>
      </main>
    </>
  );
}