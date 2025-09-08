import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from '../api/axios';
import './Result.css';

export default function Result() {
  const { state } = useLocation();         
  const interviewId = state?.interviewId;

  const [feedback, setFeedback] = useState(null); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!interviewId) {
      setError(true);
      setLoading(false);
      return;
    }

    axios
      .get(`/api/interview/${interviewId}`)
      .then(({ data }) => setFeedback(data.feedback_candidate))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [interviewId]);

  /* ---------- рендер ---------- */
  if (error)
    return (
      <>
        <main className="result">
          <div className="result__card">
            <h1 className="result__title">Ошибка</h1>
            <p className="result__subtitle">Не удалось загрузить результат собеседования.</p>
          </div>
        </main>
      </>
    );

  return (
    <>
      <main className="result">
        <div className="result__card">
          <h1 className="result__title">Собеседование окончено</h1>
          <p className="result__subtitle">
            {loading ? 'Идёт обработка вашего ответа...' : 'Мы свяжемся с вами в ближайшее время.'}
          </p>

          <div className="result__block">
            <h2 className="result__label">Комментарий AI HR:</h2>

            {loading ? (
              <p className="result__text">Обрабатывается...</p>
            ) : (
              <p className="result__feedback">{feedback || '—'}</p>
            )}
          </div>
        </div>
      </main>
    </>
  );
}