import Meter from '../common/Meter'
import PanelHeading from '../common/PanelHeading'

function ReadinessPanel({ onOpenRoadmap }) {
  return (
    <article className="panel readiness-panel">
      <PanelHeading eyebrow="PLACEMENT READINESS" title="On track" code="R-21" />
      <div className="readiness-score"><strong>78</strong><span>/100</span></div>
      <Meter value={78} tone="mint" />
      <p>Complete 2 roadmap actions to reach the next level.</p>
      <button className="link-button" onClick={onOpenRoadmap}>OPEN ROADMAP →</button>
    </article>
  )
}

export default ReadinessPanel
