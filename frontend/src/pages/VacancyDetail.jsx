import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import './VacancyDetail.css';

export default function VacancyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [vacancy, setVacancy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [aiText, setAiText] = useState('');   // текст для модалки
  const [showAi, setShowAi] = useState(false); // видимость модалки

  const openAiFeedback = (feedback) => {
  setAiText(feedback || '—');
  setShowAi(true);
  };

  const [showForm, setShowForm] = useState(false);
  const [candidateData, setCandidateData] = useState({
    full_name: '',
    email: '',
    file: null,
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    axios
      .get(`/api/vacancy/${id}`)
      .then(({ data }) => setVacancy(data))
      .catch(err => {
        console.error(err);
        setError('Не удалось загрузить вакансию');
      })
      .finally(() => setLoading(false));
  }, [id]);

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
  const downloadResume = async (resume_id) => {
    if (!resume_id) return alert('Файл не загружен');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/api/resume/${resume_id}/download`, {
        responseType: 'blob',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });


      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      const disposition = response.headers['content-disposition'];
      let fileName = 'resume.pdf';
      if (disposition) {
        const match = disposition.match(/filename="?(.+)"?/);
        if (match?.[1]) {
          fileName = match[1];
        }
      }

      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Не удалось скачать файл');
    }
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (files) {
      setCandidateData((prev) => ({ ...prev, file: files[0] }));
    } else {
      setCandidateData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!candidateData.full_name || !candidateData.email || !candidateData.file) {
      return alert('Заполните все поля');
    }

    const formData = new FormData();
    formData.append('full_name', candidateData.full_name);
    formData.append('email', candidateData.email);
    formData.append('vacancy_id', id);
    formData.append('file', candidateData.file);

    try {
      setSubmitting(true);
      await axios.post(`/api/resume`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setShowForm(false);
      setCandidateData({ full_name: '', email: '', file: null });
      const { data } = await axios.get(`/api/vacancy/${id}`);
      setVacancy(data);
    } catch (err) {
      console.error(err);
      alert('Ошибка при добавлении кандидата');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <main className="vacancy-detail">


        {loading ? (
          <p>Загрузка...</p>
        ) : vacancy ? (
          <div className="vacancy-detail__card">
            <button
              className="btn-back"
              onClick={() => navigate('/vacancies')}
            >
              ×
            </button>
            <h1 className="vacancy-detail__title">{vacancy.title}</h1>
            <p className="vacancy-detail__desc">{vacancy.description}</p>

            <h2 className="vacancy-detail__subtitle">Кандидаты</h2>

            {vacancy.resumes?.length ? (
              <ul className="vacancy-detail__list">
                {vacancy.resumes.map((r) => (
                  <li key={r.id} className="vacancy-detail__item">
                    <div className="vacancy-detail__row vacancy-detail__actions">
                      <span className="vacancy-detail__fio">
                        {r.candidate.full_name} ({r.candidate.email})
                      </span>
                      
                      <div className="vacancy-detail__btns">
                      <button
                        className="vacancy-detail__btn-resume"
                        onClick={() => downloadResume(r.id)}
                      >
                        ⬇ Резюме
                      </button>
                      <button
                        className="vacancy-detail__btn-ai"
                        onClick={() => openAiFeedback(r.interview?.feedback_candidate)}
                        disabled={!r.interview?.feedback_candidate}
                        title={!r.interview?.feedback_candidate ? 'Отзыв пока не сформирован' : ''}
                      >
                        Итог AI
                      </button>
                    </div>
                      
                    </div>

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

            <button
              className="btn-add-candidate"
              onClick={() => setShowForm(true)}
            >
              Добавить кандидата
            </button>

            {showForm && (
              <div className="modal-overlay" onClick={() => setShowForm(false)}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <h3>Добавить нового кандидата</h3>
                  <form onSubmit={handleSubmit} className="modal-form">
                    <label>
                      ФИО:
                      <input
                        type="text"
                        name="full_name"
                        value={candidateData.full_name}
                        onChange={handleChange}
                        required
                      />
                    </label>
                    <label>
                      Почта:
                      <input
                        type="email"
                        name="email"
                        value={candidateData.email}
                        onChange={handleChange}
                        required
                      />
                    </label>
                    <label>
                      Резюме:
                      <input
                        style={{ visibility: 'hidden' }}
                        type="file"
                        name="file"
                        onChange={handleChange}
                        accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.rtf"
                        required
                      />
                      <div
                        className="drop-area"
                        onClick={(e) => e.currentTarget.previousElementSibling.click()}
                      >
                        <svg className="upload-icon" viewBox="0 0 24 24">
                          <path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2v-2h14v2H5z" />
                        </svg>

                        {/* до выбора */}
                        {!candidateData.file && (
                          <>
                            <span className="drop-title">Перетащите файл сюда</span>
                            <span className="drop-hint">или нажмите для выбора</span>
                            <span className="drop-formats">PDF, DOC, DOCX, PNG, JPG, RTF</span>
                          </>
                        )}

                        {/* после выбора */}
                        {candidateData.file && (
                          <>
                            <span className="drop-title">Файл выбран</span>
                            <span className="drop-hint">{candidateData.file.name}</span>
                          </>
                        )}
                      </div>
                    </label>
                    <div className="modal-buttons">
                      <button type="submit" disabled={submitting}>
                        {submitting ? 'Отправка...' : 'Создать'}
                      </button>
                      <button type="button" onClick={() => setShowForm(false)}>
                        Отмена
                      </button>
                    </div>
                  </form>
                </div>
              </div>
              
            )}
            {showAi && (
              <div className="modal-overlay" onClick={() => setShowAi(false)}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <h3>Итог AI HR</h3>
                  <pre className="ai-feedback">{aiText}</pre>
                  <button className="btn-close" onClick={() => setShowAi(false)}>Закрыть</button>
                </div>
              </div>
            )}
          </div>
          
        ) : (
          <p>{error || 'Вакансия не найдена'}</p>
        )}
      </main>
    </>
  );
}
