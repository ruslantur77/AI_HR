import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import './Vacancies.css';

export default function Vacancies() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

/* ---------- заглушка ---------- */
  useEffect(() => {
    setTimeout(() => {
      setList([
        { id: '1', title: 'Junior Frontend Developer', status: 'open' },
        { id: '2', title: 'Middle Backend (FastAPI)', status: 'open' },
        { id: '3', title: 'Senior DevOps', status: 'closed' },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  useEffect(() => {
    axios
      .get('/api/vacancy/')
      .then(({ data }) => setList(data))
      .catch(err => {
        console.error(err);
        setError('Не удалось загрузить вакансии');
      })
      .finally(() => setLoading(false));
  }, []);


  const createVacancy = async () => {
    const title = prompt('Название вакансии:');
    const desc = prompt('Описание:');
    if (!title || !desc) return;

    try {
      await axios.post('/api/vacancy/', { title, description: desc });
      const { data } = await axios.get('/api/vacancy/');
      setList(data);
    } catch (e) {
      alert('Ошибка при создании: ' + (e.response?.data?.detail?.[0]?.msg || e.message));
    }
  };

  return (
    <>
      <main className="vacancies">
        <div className="vacancies__card">
          <h1 className="vacancies__title">Список вакансий</h1>

          {error && <p className="vacancies__error">{error}</p>}

          {loading ? (
            <p>Загрузка...</p>
          ) : Array.isArray(list) && list.length ? (
            <ul className="vacancies__list">
              {list.map(v => (
                <li key={v.id} className="vacancies__item">
                  <Link className="vacancies__link" to={`/vacancies/${v.id}`}>
                    <span className="vacancies__name">{v.title}</span>
                    <span className="vacancies__status">{v.status}</span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p>Пока нет вакансий</p>
          )}

          <button className="vacancies__add-btn" onClick={createVacancy}>
            + Новая вакансия
          </button>
        </div>
      </main>
    </>
  );
}