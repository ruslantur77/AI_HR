import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import AiButton from './AiButton';
import './Home.css';

export default function Home() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking'); // checking | ok | error | finished
  const interviewId = searchParams.get('interview_id');

  useEffect(() => {
    if (!interviewId) return setStatus('ok'); // просто лендинг

    axios
      .get(`/api/interview/${interviewId}`)
      .then(({ data }) => {
        if (data.result !== 'pending') return setStatus('finished');
        setStatus('ok');
      })
      .catch(() => setStatus('error'));
  }, [interviewId]);

  if (status === 'checking') return <p className="home__msg">Проверка ссылки...</p>;
  if (status === 'error') return <p className="home__msg">Неверная или просроченная ссылка</p>;
  if (status === 'finished')
    return <p className="home__msg">Вы уже проходили собеседование. Результат: {searchParams.get('result') || 'известен HR'}</p>;

  return (
    <main className="home">
      <h1 className="home__title">Собеседование с AI HR</h1>
      <AiButton interviewId={interviewId} />
    </main>
  );
}