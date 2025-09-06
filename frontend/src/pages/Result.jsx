import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import Header from '../components/Header';
import './Result.css';

export default function Result() {
  const [aiResponse, setAiResponse] = useState(null); // прилетит с сервера
  const [loading, setLoading] = useState(true);     // пока ждём ответ
  const location = useLocation();

  /* ---------- забираем данные, которые можно передать через state ---------- */
  useEffect(() => {
    // если сервер должен отдать JSON по GET /api/interview/result – делаем запрос
    // иначе можно сразу брать location.state?.aiResponse и убирать loading
    fetch(`${import.meta.env.VITE_API_URL}/api/interview/result`)
      .then(res => (res.ok ? res.json() : Promise.reject(res)))
      .then(data => setAiResponse(data))
      .catch(() => setAiResponse(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Header />
      <main className="result">
        <div className="result__card">
          <h1 className="result__title">Собеседование окончено</h1>
          <p className="result__subtitle">
            Мы свяжемся с вами в ближайшее время в случае успешного прохождения.
          </p>

          <div className="result__block">
            <h2 className="result__label">Ответ от AI HR:</h2>
            {loading ? (
              <p>Загрузка...</p>
            ) : (
              <pre className="result__text">
                {aiResponse ? JSON.stringify(aiResponse, null, 2) : '—'}
              </pre>
            )}
          </div>
        </div>
      </main>
    </>
  );
}