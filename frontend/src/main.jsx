import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom' 
import './index.css'
import App from './App.jsx'
import Screening from './pages/Screening.jsx'
import Result from './pages/Result.jsx'

const router = createBrowserRouter([
  { path: '/', element: <App /> },
  { path: '/screening', element: <Screening /> },
  {path: "/result",  element: <Result />}
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
)