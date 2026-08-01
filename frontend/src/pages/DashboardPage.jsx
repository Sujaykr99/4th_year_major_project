import { useState } from 'react'
import ActivityPanel from '../components/dashboard/ActivityPanel'
import PredictionPanel from '../components/dashboard/PredictionPanel'
import ReadinessPanel from '../components/dashboard/ReadinessPanel'
import RoadmapPanel from '../components/dashboard/RoadmapPanel'
import SkillSignalsPanel from '../components/dashboard/SkillSignalsPanel'
import StatsGrid from '../components/dashboard/StatsGrid'
import DashboardLayout from '../layouts/DashboardLayout'

function DashboardPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeNav, setActiveNav] = useState('Dashboard')
  const [activeTab, setActiveTab] = useState('Overview')
  const [notice, setNotice] = useState('SYSTEM READY')

  return (
    <DashboardLayout
      activeNav={activeNav}
      isSidebarOpen={sidebarOpen}
      onToggleSidebar={() => setSidebarOpen((open) => !open)}
      onChangeNav={setActiveNav}
      onNotice={setNotice}
    >
      <section className="content">
        <div className="welcome-row"><div><p className="eyebrow green">GOOD EVENING, ALEX</p><h1>Your career command center.</h1><p className="subtle">A clearer path starts with the data you already have.</p></div><div className="system-status"><b className="pulse" /> {notice}</div></div>
        <div className="tabs" role="tablist">{['Overview', 'Skill matrix', 'Career paths'].map((tab) => <button key={tab} onClick={() => setActiveTab(tab)} className={activeTab === tab ? 'selected' : ''}>{tab}</button>)}</div>
        <StatsGrid />
        <section className="dashboard-grid">
          <PredictionPanel onOpenPrediction={() => setActiveNav('Prediction')} />
          <ReadinessPanel onOpenRoadmap={() => setActiveNav('Roadmap')} />
          <SkillSignalsPanel />
          <ActivityPanel />
          <RoadmapPanel onOpenRoadmap={() => setActiveNav('Roadmap')} />
        </section>
      </section>
    </DashboardLayout>
  )
}

export default DashboardPage
