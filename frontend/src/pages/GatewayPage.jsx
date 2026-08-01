import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function GatewayPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const timer = window.setTimeout(() => navigate('/dashboard', { replace: true }), 2400)
    return () => window.clearTimeout(timer)
  }, [navigate])

  return <div className="matrix-door" aria-label="Entering Matrix dashboard"><div className="door door-left"><span>MATR</span></div><div className="door door-right"><span>IX</span></div><p>INITIALIZING CAREER MAINFRAME</p></div>
}

export default GatewayPage
