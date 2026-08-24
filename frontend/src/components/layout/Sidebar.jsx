import { navItems } from '../../data/dashboardData'

function Sidebar({ activeNav, isOpen, onToggle, onChangeNav, onNotice, user, onLogout }) {
  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : user?.username?.slice(0, 2).toUpperCase() || 'MX'

  const displayName = user?.full_name || user?.username || 'User'

  return (
    <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
      <div className="brand">
        <span className="brand-mark">M</span>
        <span className="brand-name">MATRIX</span><i>_</i>
        <button className="sidebar-toggle" onClick={onToggle} aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}>{isOpen ? '‹' : '›'}</button>
      </div>

      <div className="student-card">
        <div className="avatar">{initials}</div>
        <div>
          <span className="eyebrow">STUDENT PROFILE</span>
          <strong>{displayName}</strong>
          <small>{user?.email || 'matrix user'}</small>
        </div>
      </div>

      <nav className="side-nav" aria-label="Main navigation">
        {navItems.map(([label, icon]) => (
          <button key={label} className={activeNav === label ? 'nav-active' : ''} onClick={() => onChangeNav(label)}>
            <span className="nav-icon">{icon}</span>
            <span className="nav-label">{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p><b className="pulse" /> ENGINE ONLINE</p>
        <button className="text-button" onClick={onLogout}>↪ Sign out</button>
      </div>
    </aside>
  )
}

export default Sidebar
