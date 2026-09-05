import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardLayout from '../layouts/DashboardLayout'
import DashboardContent from '../components/dashboard/DashboardContent'
import PredictionPage from './PredictionPage'
import ProfilePage from './ProfilePage'
import RoadmapPage from './RoadmapPage'
import { getCurrentUser, logout } from '../lib/auth'
import { api } from '../lib/api'

const PAGES = ['Dashboard', 'Prediction', 'Profile', 'Roadmap']

function MainApp() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeNav, setActiveNav] = useState('Dashboard')
  const [notice, setNotice] = useState('SYSTEM READY')
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [predictionProfile, setPredictionProfile] = useState(null)
  const [latestPrediction, setLatestPrediction] = useState(null)
  const [sessionError, setSessionError] = useState('')

  useEffect(() => {
    let active = true
    const loadCurrentUserData = async () => {
      try {
        const currentUser = await getCurrentUser()
        if (!active) return
        setUser(currentUser)
        try {
          const currentProfile = await api.getProfile()
          if (active) setProfile(currentProfile)
        } catch {
          if (active) setProfile(null)
        }
        try {
          const predProfile = await api.getPredictionProfile()
          if (active) setPredictionProfile(predProfile)
        } catch {
          if (active) setPredictionProfile(null)
        }
        try {
          const latestPred = await api.getLatestPrediction()
          if (active) setLatestPrediction(latestPred)
        } catch {
          if (active) setLatestPrediction(null)
        }
      } catch (error) {
        if (active) setSessionError(error.message)
      }
    }
    loadCurrentUserData()
    return () => { active = false }
  }, [])

  const handleLogout = () => {
    logout()
    setUser(null)
    setProfile(null)
    setPredictionProfile(null)
    setLatestPrediction(null)
    navigate('/login', { replace: true })
  }

  return (
    <DashboardLayout
      activeNav={activeNav}
      isSidebarOpen={sidebarOpen}
      onToggleSidebar={() => setSidebarOpen(o => !o)}
      onChangeNav={setActiveNav}
      onNotice={setNotice}
      user={user}
      onLogout={handleLogout}
    >
      {sessionError && <section className="content"><p className="text-red-400 font-[var(--mono)] text-sm">{sessionError}</p></section>}
      {!sessionError && activeNav === 'Dashboard' && <DashboardContent setActiveNav={setActiveNav} notice={notice} user={user} profile={profile?.prediction_profile} latestPrediction={latestPrediction} />}
      {!sessionError && activeNav === 'Prediction' && <PredictionPage setActiveNav={setActiveNav} profile={predictionProfile} />}
      {!sessionError && activeNav === 'Profile' && (
        <ProfilePage
          profile={profile}
          onProfileSaved={(saved) => {
            setProfile(saved)
            setPredictionProfile(saved)
          }}
          setActiveNav={setActiveNav}
        />
      )}
      {!sessionError && activeNav === 'Roadmap' && <RoadmapPage />}
      {!PAGES.includes(activeNav) && (
        <section className="content flex items-center justify-center min-h-[50vh]">
          <div className="text-[var(--mint)] font-[var(--mono)] text-xl border border-[var(--border)] p-10 bg-black/50 backdrop-blur">
            <span className="text-[var(--green)] animate-pulse mr-4">{'>'}</span>
            NODE [{activeNav.toUpperCase()}] OFFLINE
          </div>
        </section>
      )}
    </DashboardLayout>
  )
}

export default MainApp
