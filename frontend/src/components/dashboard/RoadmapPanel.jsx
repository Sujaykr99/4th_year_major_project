import PanelHeading from '../common/PanelHeading'
import { roadmapItems } from '../../data/dashboardData'

function RoadmapPanel({ onOpenRoadmap }) {
  return (
    <article className="panel roadmap-panel">
      <PanelHeading
        eyebrow="PERSONALIZED ROADMAP"
        title="Continue building momentum"
        action={<button className="more-button" onClick={onOpenRoadmap}>VIEW ALL</button>}
      />
      <div className="scroll-list roadmap-list">
        {roadmapItems.map(([number, title, detail, state]) => <div className={`roadmap-item ${state}`} key={number}><span>{number}</span><div><strong>{title}</strong><p>{detail}</p></div><b>{state === 'active' ? 'CONTINUE →' : state === 'next' ? 'UP NEXT' : 'LOCKED'}</b></div>)}
      </div>
    </article>
  )
}

export default RoadmapPanel
