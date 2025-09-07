import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from '../api/axios';
import Header from '../components/Header';
import './VacancyDetail.css';

export default function VacancyDetail() {
  const { id } = useParams();
  const [vacancy, setVacancy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  /* ---------- реальный запрос ---------- */
  // useEffect(() => {
  //   axios
  //     .get(`/api/vacancy/${id}`)
  //     .then(({ data }) => setVacancy(data))
  //     .catch(err => {
  //       console.error(err);
  //       setError('Не удалось загрузить вакансию');
  //     })
  //     .finally(() => setLoading(false));
  // }, [id]);

  /* ---------- заглушка (закомментирована) ---------- */

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
    setTimeout(() => { setVacancy(fakeDB[id] || null); setLoading(false); }, 300);
  }, [id]);


  /* ---------- вспомогательные функции ---------- */
  const downloadResume = (file_path) => {
    if (!file_path) return alert('Файл не загружен');
    window.open(`${import.meta.env.VITE_API_URL}${file_path}`, '_blank');
  };

  const createInterview = async (resumeId) => {
    try {
      // ЗАМЕНИТЕ на реальный вызов когда бэк добавит ручку
      alert(`POST /api/resume/${resumeId}/start – пока заглушка`);
      // Пример:
      // const { data } = await axios.post(`/api/resume/${resumeId}/start`);
      // обновляем vacancy чтобы кнопка стала disabled
      // setVacancy(prev => ({...prev, resumes: prev.resumes.map(r => r.id === resumeId ? {...r, interview: data} : r)}));
    } catch (e) {
      alert('Ошибка при создании собеседования');
    }
  };

  /* ---------- рендер ---------- */
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
                {vacancy.resumes.map((r) => (
                  <li key={r.id} className="vacancy-detail__item">
                    {/* строка 1: ФИО + кнопки */}
                    <div className="vacancy-detail__row vacancy-detail__actions">
                      <span className="vacancy-detail__fio">
                        {r.candidate.full_name} ({r.candidate.email})
                      </span>

                      <div className="vacancy-detail__btns">
                        <button
                          className="vacancy-detail__btn-resume"
                          onClick={() => downloadResume(r.file_path)}
                        >
                          ⬇ Резюме
                        </button>

                        <button
                          className="vacancy-detail__btn-interview"
                          onClick={() => createInterview(r.id)}
                          disabled={!!r.interview}
                        >
                          {r.interview ? 'Интервью создано' : 'Создать собеседование'}
                        </button>
                      </div>
                    </div>

                    {/* строка 2: статусы */}
                    <div className="vacancy-detail__row">
                      <span className={`status status--${r.auto_screening_status}`}>
                        Авто-скрининг: {r.auto_screening_status}
                      </span>

                      {r.interview ? (
                        <span className={`status status--${r.interview.result}`}>
                          Собеседование: {r.interview.result}
                        </span>
                      ) : (
                        <span className="status status--none">Собеседование: —</span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>Кандидатов пока нет</p>
            )}
          </div>
        ) : (
          <p>{error || 'Вакансия не найдена'}</p>
        )}
      </main>
    </>
  );
}