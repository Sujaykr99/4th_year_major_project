function Meter({ value, tone = 'green' }) {
  return (
    <div className="meter" aria-label={`${value}% complete`}>
      <span className={`meter-fill ${tone}`} style={{ width: `${value}%` }} />
    </div>
  )
}

export default Meter
