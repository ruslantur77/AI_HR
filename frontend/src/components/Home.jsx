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
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('checking'); // checking | ok | error | finished
  const [feedback, setFeedback] = useState(null);
  const interviewId = searchParams.get('interview_id');

  useEffect(() => {
    if (!interviewId) return setStatus('ok');
    if (!interviewId) {
      setError(true);
      setLoading(false);
      return;
    }

    axios
      .get(`/api/interview/${interviewId}`)
      .then(({ data }) => {
        if (data.result !== 'pending') {
          // формируем красивый текст
          const label = RESULT_LABEL[data.result] || data.result;
          const feedback_data = data.feedback_candidate
            ? `Комментарий: ${data.feedback_candidate}`
            : '';
          setFeedback(`Результат: ${label}\n${feedback_data}`);
          return setStatus('finished');
        }
        setStatus('ok');
      })
      .catch(() => setStatus('error')).finally(() => setLoading(false));

  }, [interviewId]);

  if (status === 'checking')
    return <p className="home__msg">Проверка ссылки...</p>;
  if (status === 'error')
    return <p className="home__msg">Неверная или просроченная ссылка</p>;
  if (status === 'finished')
    return (
      <>
        {loading ? (
          <p className="loading-text">Идёт обработка вашего ответа...</p>
        ) : (
          <main className="result">
            <div className="result__card">
              <h1 className="result__title">Собеседование окончено</h1>
              <div className="result__block">
                <h2 className="result__label">Комментарий AI HR:</h2>
                <p className="result__feedback">{feedback || '—'}</p>
              </div>
            </div>
          </main>
        )}
      </>
    );


  return (
    <main className="home">
      <h1 className="home__title">Собеседование с AI HR</h1>
      <AiButton interviewId={interviewId} />
    </main>
  );
}