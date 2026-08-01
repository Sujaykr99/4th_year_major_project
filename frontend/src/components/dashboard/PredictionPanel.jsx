import Meter from '../common/Meter'
import PanelHeading from '../common/PanelHeading'

function PredictionPanel({ onOpenPrediction }) {
  return (
    <article className="panel primary-panel">
      <PanelHeading eyebrow="LATEST PREDICTION" title="Cloud Architect" code="ID: P-07" />
      <div className="prediction-content">
        <div className="orbit"><i /><i /><b>94<small>%</small></b></div>
        <div>
          <p className="prediction-copy">Your technical profile shows strong alignment with cloud systems, backend development and scalable infrastructure.</p>
          <div className="metric-line"><span>MODEL CONFIDENCE</span><b>94%</b><Meter value={94} /></div>
          <button className="primary-action" onClick={onOpenPrediction}>VIEW FULL PREDICTION <span>→</span></button>
        </div>
      </div>
    </article>
  )
}

export default PredictionPanel
