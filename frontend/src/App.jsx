import { Outlet } from 'react-router-dom';
import './App.css';
import Header from './components/Header.jsx';

function App() {
  return (
    <>
      <Header />
      <Outlet /> {/* ← сюда рендерятся дочерние маршруты */}
    </>
  );
}

export default App;