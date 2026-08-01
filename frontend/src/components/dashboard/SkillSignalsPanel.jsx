import PanelHeading from '../common/PanelHeading'

function SkillSignalsPanel() {
  return (
    <article className="panel skill-panel">
      <PanelHeading eyebrow="SKILL SIGNALS" title="What to build next" code="S-42" />
      <div className="skill-columns">
        <div><h3>Strong signals</h3>{['Python', 'React', 'Problem solving'].map((skill) => <p key={skill}><b>✓</b>{skill}</p>)}</div>
        <div><h3>Growth area</h3>{['Cloud deployment', 'System design', 'Docker'].map((skill) => <p key={skill}><b>+</b>{skill}</p>)}</div>
      </div>
    </article>
  )
}

export default SkillSignalsPanel
