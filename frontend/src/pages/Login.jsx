import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import Header from '../components/Header';
import './Login.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const form = new FormData();
      form.append('username', email);
      form.append('password', password);

      const { data } = await axios.post('/api/auth/login', form);

      localStorage.setItem('token', data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      navigate('/vacancies');
    } catch (err) {
      // 422 – валидация, остальное – "неверный логин/пароль"
      const msg =
        err.response?.status === 422
          ? err.response.data.detail.map(d => d.msg).join(', ')
          : 'Неверный email или пароль';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <main className="login">
        <form className="login__card" onSubmit={handleSubmit}>
          <h1 className="login__title">Вход для HR</h1>

          {error && <p className="login__error">{error}</p>}

          <input
            className="login__input"
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          <input
            className="login__input"
            type="password"
            placeholder="Пароль"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
          />

          <button className="login__btn" disabled={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </main>
    </>
  );
}