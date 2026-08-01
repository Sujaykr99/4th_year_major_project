import Meter from '../common/Meter'

function StatsGrid() {
  return (
    <section className="stat-grid">
      <article className="stat-card"><span className="eyebrow">ACADEMIC SCORE</span><strong>3.84 <em>/ 4.00</em></strong><Meter value={84} /></article>
      <article className="stat-card"><span className="eyebrow">SKILL NODES</span><strong>24 <em>ACTIVE</em></strong><div className="skill-dots">{Array.from({ length: 12 }, (_, index) => <i key={index} className={index < 9 ? 'lit' : ''} />)}</div></article>
      <article className="stat-card"><span className="eyebrow">PROFILE COMPLETION</span><strong>82<em>%</em></strong><Meter value={82} tone="mint" /></article>
      <article className="stat-card"><span className="eyebrow">PROJECTS DEPLOYED</span><strong>07 <em>VERIFIED</em></strong><small className="green">+ 1 since last week</small></article>
    </section>
  )
}

export default StatsGrid
