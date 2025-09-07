import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import './Vacancies.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function Vacancies() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

useEffect(() => {
      setTimeout(() => {
    setList([
      {
        id: '1',
        title: 'Junior Frontend Developer',
        status: 'open',
      },
      {
        id: '2',
        title: 'Middle Backend (FastAPI)',
        status: 'open',
      },
      {
        id: '3',
        title: 'Senior DevOps',
        status: 'closed',
      },
    ]);
    setLoading(false);
  }, 500);
//   ЗАПРОС!!!!!!!!!!!!!!!!!!!!!!!!!!!
//   axios
//     .get(`${API_URL}/api/vacancy/`)
//     .then(r => {
//       console.log('vacancy response:', r.data); // <-- посмотрите в консоль
//       // если данные завернуты в объект, например { data: [...] }
//       const payload = Array.isArray(r.data) ? r.data : r.data?.data || [];
//       setList(payload);
//     })
//     .finally(() => setLoading(false));
}, []);

  return (
    <>
      <Header />
      <main className="vacancies">
        <div className="vacancies__card">
          <h1 className="vacancies__title">Список вакансий</h1>

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
        </div>
      </main>
    </>
  );
}