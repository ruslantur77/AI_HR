import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import './Login.css';

const API_URL = import.meta.env.VITE_API_URL;

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const form = new FormData();
      form.append('username', email);
      form.append('password', password);
      const { data } = await axios.post(`${API_URL}/api/auth/login`, form);
      localStorage.setItem('token', data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      navigate('/vacancies');
    } catch {
      setError('Неверный email или пароль');
    }
  };

  return (
    <>
      <Header />
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
          <button className="login__btn">Войти</button>
        </form>
      </main>
    </>
  );
}