import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import './VacancyDetail.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function VacancyDetail() {
  const { id } = useParams();
  const [vacancy, setVacancy] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fakeDB = {
    '1': {
      id: '1',
      title: 'Junior Frontend Developer',
      description: 'Ищем начинающего разработчика с знанием React и базовым опытом TypeScript. Удалёнка, гибкий график.',
      status: 'open',
      resumes: [
        {
          id: 'r1',
          auto_screening_status: 'passed',
          candidate: { full_name: 'Иван Иванов', email: 'ivan@mail.ru' },
        },
        {
          id: 'r2',
          auto_screening_status: 'pending',
          candidate: { full_name: 'Анна Петрова', email: 'anna@mail.ru' },
        },
      ],
    },
    '2': {
      id: '2',
      title: 'Middle Backend (FastAPI)',
      description: 'Опыт коммерческой разработки на Python от 2 лет, знание PostgreSQL, Docker.',
      status: 'open',
      resumes: [
        {
          id: 'r3',
          auto_screening_status: 'rejected',
          candidate: { full_name: 'Сергей Сидоров', email: 'serg@mail.ru' },
        },
      ],
    },
    '3': {
      id: '3',
      title: 'Senior DevOps',
      description: 'Построение CI/CD, Kubernetes, облачные решения (AWS/GCP).',
      status: 'closed',
      resumes: [],
    },
  };

  setTimeout(() => {
    const vacancy = fakeDB[id] || null;
    setVacancy(vacancy);
    setLoading(false);
  }, 300);
    // axios
    //   .get(`${API_URL}/api/vacancy/${id}`)
    //   .then(r => setVacancy(r.data))
    //   .finally(() => setLoading(false));
  }, [id]);

  return (
    <>
      <Header />
      <main className="vacancy-detail">
        {loading ? (
          <p>Загрузка...</p>
        ) : vacancy ? (
          <div className="vacancy-detail__card">
            <h1 className="vacancy-detail__title">{vacancy.title}</h1>
            <p className="vacancy-detail__desc">{vacancy.description}</p>

            <h2 className="vacancy-detail__subtitle">Кандидаты</h2>
            {vacancy.resumes?.length ? (
              <ul className="vacancy-detail__list">
                {vacancy.resumes.map(r => (
                  <li key={r.id} className="vacancy-detail__item">
                    <span>
                      {r.candidate.full_name} ({r.candidate.email})
                    </span>
                    <span className={`status status--${r.auto_screening_status}`}>
                      {r.auto_screening_status}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Кандидатов пока нет</p>
            )}
          </div>
        ) : (
          <p>Не удалось загрузить вакансию</p>
        )}
      </main>
    </>
  );
}