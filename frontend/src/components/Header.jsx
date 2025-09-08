import './Header.css';
import logo from '/src/assets/logo.svg';
import { useLocation, useNavigate } from 'react-router-dom';

export default function Header() {
  const navigate = useNavigate();
  const { pathname, search } = useLocation();   // ← берём и query

  const isPureHome = pathname === '/' && !search; // строго / без ?...
  const isVacancyPage = pathname.startsWith('/vacancies');
  const isResultPage = pathname.startsWith('/result');

  const handleTitleClick = () => {
    if (isVacancyPage) navigate('/login');
    if (isResultPage) navigate('/');
  };

  const clickable = isVacancyPage || isResultPage;

  return (
    <header className="header">
      <h1
        onClick={clickable ? handleTitleClick : undefined}
        style={{ cursor: clickable ? 'pointer' : 'default' }}
      >
        AI HR
      </h1>

      {/* кнопка ТОЛЬКО на чистом / */}
      {isPureHome && (
        <button className="header__hr-btn" onClick={() => navigate('/login')}>
          Вход для HR
        </button>
      )}

      <div className="logo">
        <img className="logo-image" src={logo} alt="Logo" />
      </div>
    </header>
  );
}