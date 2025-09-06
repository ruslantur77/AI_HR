import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom' // ✅ исправлено
import './index.css'
import App from './App.jsx'
import Screening from './pages/Screening.jsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/screening', element: <Screening /> }
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
)