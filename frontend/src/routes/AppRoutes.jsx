import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import GatewayPage from '../pages/GatewayPage'
import LoginPage from '../pages/LoginPage'
import MainApp from '../pages/MainApp'
import { isLoggedIn } from '../lib/auth'

function RequireAuth({ children }) {
  return isLoggedIn() ? children : <Navigate to="/login" replace />
}

function LoginRoute() {
  const navigate = useNavigate()
  if (isLoggedIn()) return <Navigate to="/dashboard" replace />
  return <LoginPage onLogin={() => navigate('/gateway')} />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route path="/gateway" element={<RequireAuth><GatewayPage /></RequireAuth>} />
      <Route path="/dashboard" element={<RequireAuth><MainApp /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default AppRoutes
