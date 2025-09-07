import axios from 'axios';

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // http://localhost:8000
});

// автоматически цепляем токен
instance.interceptors.request.use(config => {
  const t = localStorage.getItem('token');
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

export default instance;