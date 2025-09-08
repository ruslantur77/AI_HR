import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import AiButton from './AiButton';
import './Home.css';

const RESULT_LABEL = {
  passed: 'пройдено ✅',
  rejected: 'не пройдено ❌',
  pending: 'в процессе',
};

export default function Home() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking'); // checking | ok | error | finished
  const [resultText, setResultText] = useState('');
  const interviewId = searchParams.get('interview_id');

  useEffect(() => {
    if (!interviewId) return setStatus('ok');

    axios
      .get(`/api/interview/${interviewId}`)
      .then(({ data }) => {
        if (data.result !== 'pending') {
          // формируем красивый текст
          const label = RESULT_LABEL[data.result] || data.result;
          const feedback = data.feedback_candidate
            ? ` Комментарий: ${data.feedback_candidate}`
            : '';
          setResultText(`Результат: ${label}.${feedback}`);
          return setStatus('finished');
        }
        setStatus('ok');
      })
      .catch(() => setStatus('error'));
  }, [interviewId]);

  if (status === 'checking')
    return <p className="home__msg">Проверка ссылки...</p>;
  if (status === 'error')
    return <p className="home__msg">Неверная или просроченная ссылка</p>;
  if (status === 'finished')
    return (
      <div className="home__finished">
        <p className="home__msg">Вы уже проходили собеседование.</p>
        <p className="home__result">{resultText}</p>
      </div>
    );

  return (
    <main className="home">
      <h1 className="home__title">Собеседование с AI HR</h1>
      <AiButton interviewId={interviewId} />
    </main>
  );
}