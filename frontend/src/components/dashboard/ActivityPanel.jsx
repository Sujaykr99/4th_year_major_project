import PanelHeading from '../common/PanelHeading'
import { activities } from '../../data/dashboardData'

function ActivityPanel() {
  return (
    <article className="panel scroll-panel">
      <PanelHeading eyebrow="ACTIVITY STREAM" title="Recent progress" code="LIVE" />
      <div className="scroll-list">
        {activities.map(([title, detail, date]) => <div className="activity" key={title}><i /><div><strong>{title}</strong><span>{detail}</span></div><time>{date}</time></div>)}
      </div>
    </article>
  )
}

export default ActivityPanel
