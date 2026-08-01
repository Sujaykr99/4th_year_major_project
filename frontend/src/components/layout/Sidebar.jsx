import { navItems } from '../../data/dashboardData'

function Sidebar({ activeNav, isOpen, onToggle, onChangeNav, onNotice }) {
  const selectNav = (label) => {
    onChangeNav(label)
    if (!isOpen) onToggle()
  }

  return (
    <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <div className="brand">
        <span className="brand-mark">M</span>
        <span className="brand-name">MATRIX</span><i>_</i>
        <button className="sidebar-toggle" onClick={onToggle} aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}>{isOpen ? '‹' : '›'}</button>
      </div>
      <div className="student-card"><div className="avatar">AR</div><div><span className="eyebrow">STUDENT PROFILE</span><strong>Alex Rivera</strong><small>Computer Science · Year 3</small></div></div>
      <nav className="side-nav" aria-label="Main navigation">
        {navItems.map(([label, icon]) => <button key={label} className={activeNav === label ? 'nav-active' : ''} onClick={() => selectNav(label)}><span className="nav-icon">{icon}</span><span className="nav-label">{label}</span></button>)}
      </nav>
      <div className="sidebar-footer"><p><b className="pulse" /> ENGINE ONLINE</p><button className="text-button" onClick={() => onNotice('SESSION SIGN-OUT REQUESTED')}>↪ Sign out</button></div>
    </aside>
  )
}

export default Sidebar
