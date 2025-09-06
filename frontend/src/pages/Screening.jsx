import Header from '../components/Header';
import './Screening.css';

export default function Screening() {
  return (
    <>
      <Header />
      <main className="screening">
        <div className="screening__card">
          <div className="screening__sphere" id="aiSphere" />

          <div className="screening__controls">
            <button className="screening__btn screening__btn--mic">
              Включить микрофон
            </button>
            <button className="screening__btn screening__btn--hangup">
              Завершить звонок
            </button>
          </div>
        </div>
      </main>
    </>
  );
}