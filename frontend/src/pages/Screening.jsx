import { useEffect, useRef, useState } from 'react';
import Header from '../components/Header';
import { startEchoSession } from '../components/hooks/useInterview';
import './Screening.css';

export default function Screening() {
  const [mic, setMic] = useState(true);
  const [status, setStatus] = useState('idle');
  const pcRef = useRef(null);
  const streamRef = useRef(null);
  const remoteAudio = useRef(null);

  useEffect(() => {
    (async () => {
      setStatus('connecting');
      try {
        const {pc, stream} = await startEchoSession();
        pcRef.current = pc;
        streamRef.current = stream;

        // Добавим отладочную информацию
        console.log('Stream tracks:', stream.getTracks());
        console.log('Audio tracks:', stream.getAudioTracks());
        
        /* синхронизируем начальный статус микрофона */
        const audioTracks = stream.getAudioTracks();
        if (audioTracks.length > 0) {
          setMic(audioTracks[0].enabled);
          console.log('Initial mic state:', audioTracks[0].enabled);
        }

        pc.ontrack = e => { 
          remoteAudio.current.srcObject = e.streams[0]; 
        };
        setStatus('active');
      } catch (e) {
        console.error('Error in useEffect:', e);
        setStatus('error');
      }
    })();
    
    return () => {
      streamRef.current?.getTracks().forEach(t => t.stop());
      pcRef.current?.close();
    };
  }, []);

  const toggleMic = () => {
    console.log('Toggle mic called, current state:', mic);
    
    const stream = streamRef.current;
    if (!stream) {
      console.error('No stream available');
      return;
    }
    
    const audioTracks = stream.getAudioTracks();
    console.log('Available audio tracks:', audioTracks);
    
    if (audioTracks.length === 0) {
      console.error('No audio tracks found');
      return;
    }
    
    const audioTrack = audioTracks[0];
    const newState = !audioTrack.enabled;
    
    console.log('Changing mic state from', audioTrack.enabled, 'to', newState);
    
    try {
      audioTrack.enabled = newState;
      setMic(newState);
      console.log('Mic state changed successfully');
    } catch (error) {
      console.error('Error changing mic state:', error);
    }
  };

  const hangUp = () => { window.location.href = '/'; };

  // визуализация уровня
  useEffect(() => {
    if (status !== 'active') return;
    const ctx = new AudioContext();
    const analyser = ctx.createAnalyser();
    const src = ctx.createMediaStreamSource(streamRef.current);
    src.connect(analyser);
    
    const tick = () => {
      const data = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(data);
      const avg = data.reduce((a,b) => a+b) / data.length;
      const sph = document.getElementById('aiSphere');
      if (sph) sph.style.transform = `scale(${1 + avg/512})`;
      requestAnimationFrame(tick);
    };
    
    tick(); 
    return () => ctx.close();
  }, [status]);

  return (
    <>
      <Header />
      <main className="screening">
        <div className="screening__card">
          <div className="screening__sphere" id="aiSphere" />
          <audio ref={remoteAudio} autoPlay style={{display: 'none'}} />

          <div className="screening__controls">
            <button 
              className={`screening__btn ${mic ? 'screening__btn--mic' : 'screening__btn--mic-off'}`}
              onClick={toggleMic} 
              disabled={status !== 'active'}
            >
              {mic ? 'Выключить микрофон' : 'Включить микрофон'}
            </button>
            
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
          
          {/* Добавим отладочную информацию */}
          <div style={{color: 'white', fontSize: '12px', marginTop: '10px'}}>
            Отладка: mic = {mic.toString()}, status = {status}
          </div>
        </div>
      </main>
    </>
  );
}