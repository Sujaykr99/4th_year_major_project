function PanelHeading({ eyebrow, title, code, action }) {
  return (
    <div className="panel-heading">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
      </div>
      {action || <span className="code">{code}</span>}
    </div>
  )
}

export default PanelHeading
