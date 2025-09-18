import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from '../api/axios';
import './Vacancies.css';

export default function Vacancies() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ title: '', description: '' });

  useEffect(() => {
    axios
      .get('/api/vacancy/')
      .then(({ data }) => setList(data))
      .catch(() => setError('Не удалось загрузить вакансии'))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!form.title.trim() || !form.description.trim()) return;
    try {
      await axios.post('/api/vacancy/', form);
      const { data } = await axios.get('/api/vacancy/');
      setList(data);
      setForm({ title: '', description: '' });
      setShowModal(false);
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

          <button className="vacancies__add-btn" onClick={() => setShowModal(true)}>
            + Новая вакансия
          </button>
        </div>
      </main>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Новая вакансия</h3>

            <label style={{ color: '#fff', display: 'block', marginBottom: 12 }}>
              Название:
              <input
                style={{ width: '100%',
                   marginTop: 6,
                  borderRadius:6,
                  fontSize:14,
                  fontWeight:500,
                  padding: '8px 10px'
                }}
                value={form.title}
                onChange={e => setForm({ ...form, title: e.target.value })}
              />
            </label>

            <label style={{ color: '#fff', display: 'block', marginBottom: 20 }}>
              Описание:
              <textarea
                style={{
                  width: '100%',
                  marginTop: 6,
                  fontWeight: 500,
                  minHeight:100,
                  borderRadius: 6,
                  resize: 'none',
                  fontSize:14,
                  padding: '8px 10px'
                }}
                value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })}
              />
            </label>

            <div className="modal-buttons">
              <button onClick={handleCreate} style={{ background: '#22c55e', color: '#fff' }}>Создать</button>
              
              <button onClick={() => setShowModal(false)}>Отмена</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}