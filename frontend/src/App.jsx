import { useEffect, useState } from 'react'
import './App.css'
import LoginPage from './pages/LoginPage'

const navItems = [
  ['Dashboard', '▦'],
  ['Prediction', '◈'],
  ['Profile', '◎'],
  ['Roadmap', '⌘'],
  ['Settings', '⚙'],
]

const activities = [
  ['Prediction analyzed', 'Cloud Architect · 94% confidence', '2 min ago'],
  ['Profile updated', 'Added React and Docker skills', 'Yesterday'],
  ['Roadmap milestone', 'Completed JavaScript foundations', 'Jul 28'],
  ['Assessment saved', 'Logical reasoning · 82%', 'Jul 24'],
]

const roadmap = [
  ['01', 'Build an API', 'Create a small REST API with FastAPI.', 'active'],
  ['02', 'Deploy a project', 'Ship one portfolio project to the cloud.', 'next'],
  ['03', 'Learn system design', 'Practice scalable application patterns.', 'locked'],
]

function Meter({ value, tone = 'green' }) {
  return (
    <div className="meter" aria-label={`${value}% complete`}>
      <span className={`meter-fill ${tone}`} style={{ width: `${value}%` }} />
    </div>
  )
}

function App() {
  const [screen, setScreen] = useState('login')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeNav, setActiveNav] = useState('Dashboard')
  const [activeTab, setActiveTab] = useState('Overview')
  const [query, setQuery] = useState('')
  const [notice, setNotice] = useState('SYSTEM READY')

  const runCommand = (event) => {
    event.preventDefault()
    setNotice(query.trim() ? `QUERY COMPLETE: ${query.toUpperCase()}` : 'ENTER A QUERY TO SEARCH YOUR DATA')
    setQuery('')
  }

  useEffect(() => {
    if (screen !== 'gateway') return undefined
    const timer = window.setTimeout(() => setScreen('dashboard'), 2400)
    return () => window.clearTimeout(timer)
  }, [screen])

  if (screen === 'login') {
    return <LoginPage onLogin={() => setScreen('gateway')} />
  }

  if (screen === 'gateway') {
    return (
      <div className="matrix-door" aria-label="Entering Matrix dashboard">
        <div className="door door-left"><span>MATR</span></div>
        <div className="door door-right"><span>IX</span></div>
        <p>INITIALIZING CAREER MAINFRAME</p>
      </div>
    )
  }

  return (
    <div className={`app-shell ${sidebarOpen ? 'sidebar-open' : 'sidebar-compact'}`}>
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">M</span>
          <span className="brand-name">MATRIX</span><i>_</i>
          <button className="sidebar-toggle" onClick={() => setSidebarOpen((open) => !open)} aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}>{sidebarOpen ? '‹' : '›'}</button>
        </div>
        <div className="student-card">
          <div className="avatar">AR</div>
          <div><span className="eyebrow">STUDENT PROFILE</span><strong>Alex Rivera</strong><small>Computer Science · Year 3</small></div>
        </div>
        <nav className="side-nav" aria-label="Main navigation">
          {navItems.map(([label, icon]) => (
            <button key={label} className={activeNav === label ? 'nav-active' : ''} onClick={() => { setActiveNav(label); setSidebarOpen(true) }}>
              <span className="nav-icon">{icon}</span><span className="nav-label">{label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <p><b className="pulse" /> ENGINE ONLINE</p>
          <button className="text-button" onClick={() => setNotice('SESSION SIGN-OUT REQUESTED')}>↪ Sign out</button>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <button className="mobile-brand" onClick={() => setActiveNav('Dashboard')}>MATRIX_</button>
          <div className="crumb"><span>CAREER INTELLIGENCE</span><b>/</b> {activeNav.toUpperCase()}</div>
          <form className="command-search" onSubmit={runCommand}>
            <span>&gt;</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="SEARCH YOUR DATA" aria-label="Search your data" />
          </form>
          <button className="icon-button" onClick={() => setNotice('NO NEW NOTIFICATIONS')}>◌<span className="notification-dot" /></button>
        </header>

        <section className="content">
          <div className="welcome-row">
            <div><p className="eyebrow green">GOOD EVENING, ALEX</p><h1>Your career command center.</h1><p className="subtle">A clearer path starts with the data you already have.</p></div>
            <div className="system-status"><b className="pulse" /> {notice}</div>
          </div>

          <div className="tabs" role="tablist">
            {['Overview', 'Skill matrix', 'Career paths'].map((tab) => <button key={tab} onClick={() => setActiveTab(tab)} className={activeTab === tab ? 'selected' : ''}>{tab}</button>)}
          </div>

          <section className="stat-grid">
            <article className="stat-card"><span className="eyebrow">ACADEMIC SCORE</span><strong>3.84 <em>/ 4.00</em></strong><Meter value={84} /></article>
            <article className="stat-card"><span className="eyebrow">SKILL NODES</span><strong>24 <em>ACTIVE</em></strong><div className="skill-dots">{Array.from({ length: 12 }, (_, i) => <i key={i} className={i < 9 ? 'lit' : ''} />)}</div></article>
            <article className="stat-card"><span className="eyebrow">PROFILE COMPLETION</span><strong>82<em>%</em></strong><Meter value={82} tone="mint" /></article>
            <article className="stat-card"><span className="eyebrow">PROJECTS DEPLOYED</span><strong>07 <em>VERIFIED</em></strong><small className="green">+ 1 since last week</small></article>
          </section>

          <section className="dashboard-grid">
            <article className="panel primary-panel">
              <div className="panel-heading"><div><span className="eyebrow">LATEST PREDICTION</span><h2>Cloud Architect</h2></div><span className="code">ID: P-07</span></div>
              <div className="prediction-content">
                <div className="orbit"><i /><i /><b>94<small>%</small></b></div>
                <div><p className="prediction-copy">Your technical profile shows strong alignment with cloud systems, backend development and scalable infrastructure.</p><div className="metric-line"><span>MODEL CONFIDENCE</span><b>94%</b><Meter value={94} /></div><button className="primary-action" onClick={() => setActiveNav('Prediction')}>VIEW FULL PREDICTION <span>→</span></button></div>
              </div>
            </article>

            <article className="panel readiness-panel"><div className="panel-heading"><div><span className="eyebrow">PLACEMENT READINESS</span><h2>On track</h2></div><span className="code">R-21</span></div><div className="readiness-score"><strong>78</strong><span>/100</span></div><Meter value={78} tone="mint" /><p>Complete 2 roadmap actions to reach the next level.</p><button className="link-button" onClick={() => setActiveNav('Roadmap')}>OPEN ROADMAP →</button></article>

            <article className="panel skill-panel"><div className="panel-heading"><div><span className="eyebrow">SKILL SIGNALS</span><h2>What to build next</h2></div><span className="code">S-42</span></div><div className="skill-columns"><div><h3>Strong signals</h3>{['Python', 'React', 'Problem solving'].map(x => <p key={x}><b>✓</b>{x}</p>)}</div><div><h3>Growth area</h3>{['Cloud deployment', 'System design', 'Docker'].map(x => <p key={x}><b>+</b>{x}</p>)}</div></div></article>

            <article className="panel scroll-panel"><div className="panel-heading"><div><span className="eyebrow">ACTIVITY STREAM</span><h2>Recent progress</h2></div><span className="code">LIVE</span></div><div className="scroll-list">{activities.map(([title, detail, date]) => <div className="activity" key={title}><i /><div><strong>{title}</strong><span>{detail}</span></div><time>{date}</time></div>)}</div></article>

            <article className="panel roadmap-panel"><div className="panel-heading"><div><span className="eyebrow">PERSONALIZED ROADMAP</span><h2>Continue building momentum</h2></div><button className="more-button" onClick={() => setActiveNav('Roadmap')}>VIEW ALL</button></div><div className="scroll-list roadmap-list">{roadmap.map(([num, title, detail, state]) => <div className={`roadmap-item ${state}`} key={num}><span>{num}</span><div><strong>{title}</strong><p>{detail}</p></div><b>{state === 'active' ? 'CONTINUE →' : state === 'next' ? 'UP NEXT' : 'LOCKED'}</b></div>)}</div></article>
          </section>
        </section>
      </main>
    </div>
  )
}

export default App
