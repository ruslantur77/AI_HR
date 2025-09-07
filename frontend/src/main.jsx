import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom' 
import './index.css'
import App from './App.jsx'
import Screening from './pages/Screening.jsx'
import Result from './pages/Result.jsx'
import Login from './pages/Login';
import Vacancies from './pages/Vacancies.jsx'
import VacancyDetail from './pages/VacancyDetail.jsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/screening', element: <Screening /> },
  {path: "/result",  element: <Result />},
  {path: "/login",  element: <Login />}, 
  {path: "/vacancies",  element: <Vacancies />},
  {path: "/vacancies/:id", element: <VacancyDetail />}
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
)