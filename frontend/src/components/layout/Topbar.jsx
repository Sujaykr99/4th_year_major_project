import { useState } from 'react'

function Topbar({ activeNav, onChangeNav, onNotice }) {
  const [query, setQuery] = useState('')

  const runCommand = (event) => {
    event.preventDefault()
    onNotice(query.trim() ? `QUERY COMPLETE: ${query.toUpperCase()}` : 'ENTER A QUERY TO SEARCH YOUR DATA')
    setQuery('')
  }

  return (
    <header className="topbar">
      <button className="mobile-brand" onClick={() => onChangeNav('Dashboard')}>MATRIX_</button>
      <div className="crumb"><span>CAREER INTELLIGENCE</span><b>/</b> {activeNav.toUpperCase()}</div>
      <form className="command-search" onSubmit={runCommand}><span>&gt;</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="SEARCH YOUR DATA" aria-label="Search your data" /></form>
      <button className="icon-button" onClick={() => onNotice('NO NEW NOTIFICATIONS')}>◌<span className="notification-dot" /></button>
    </header>
  )
}

export default Topbar
