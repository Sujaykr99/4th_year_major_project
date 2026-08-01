import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import DashboardPage from '../pages/DashboardPage'
import GatewayPage from '../pages/GatewayPage'
import LoginPage from '../pages/LoginPage'

function LoginRoute() {
  const navigate = useNavigate()
  return <LoginPage onLogin={() => navigate('/gateway')} />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route path="/gateway" element={<GatewayPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default AppRoutes
