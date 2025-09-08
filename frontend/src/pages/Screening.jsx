// Screening.jsx
import { useEffect, useRef, useState } from 'react';
import { startEchoSession } from '../components/hooks/useInterview';
import './Screening.css';
import { useNavigate } from 'react-router-dom';

export default function Screening() {
  const [mic, setMic] = useState(true);
  const [status, setStatus] = useState('idle');
  const [mics, setMics] = useState([]);               // доступные микрофоны
  const [selectedMicId, setSelectedMicId] = useState(''); // выбранное устройство

  const pcRef = useRef(null);
  const streamRef = useRef(null);
  const remoteAudio = useRef(null);

const stopEverything = () => {
// 1. PeerConnection
if (pcRef.current) {
  pcRef.current.getSenders().forEach(s => s.track && s.track.stop());
  pcRef.current.close();
  pcRef.current = null;
}
// 2. локальные стримы
if (streamRef.current) {
  streamRef.current.getTracks().forEach(t => t.stop());
  streamRef.current = null;
}
// 3. чужие стримы (remote)
if (remoteAudio.current?.srcObject) {
  remoteAudio.current.srcObject.getTracks().forEach(t => t.stop());
  remoteAudio.current.srcObject = null;
}
};

  /* ---------- инициализация звонка ---------- */
  useEffect(() => {
    (async () => {
      setStatus('connecting');
      try {
        const { pc, stream } = await startEchoSession();
        pcRef.current = pc;
        streamRef.current = stream;

        const audioTracks = stream.getAudioTracks();
        if (audioTracks.length) setMic(audioTracks[0].enabled);

        pc.ontrack = e => { remoteAudio.current.srcObject = e.streams[0]; };
        setStatus('active');
      } catch (e) {
        console.error(e);
        setStatus('error');
      }
    })();

    /* ➜ чистильщик при размонтировании компонента */
    return () => stopEverything();
  }, []);

  /* ---------- обновление списка микрофонов ----- */
  const refreshMics = async () => {
    // запрашиваем разрешение, если ещё не было
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

  /* ---------- вкл/выкл мик ---------- */
  const toggleMic = () => {
    const audioTrack = streamRef.current?.getAudioTracks()[0];
    if (!audioTrack) return;
    const newState = !audioTrack.enabled;
    audioTrack.enabled = newState;
    setMic(newState);
  };

  /* ---------- завершить звонок ---------- */
const navigate = useNavigate();

  /* ➜ выход со страницы */
  const hangUp = () => {
    stopEverything(); // сразу глушим всё
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