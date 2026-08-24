import { useEffect, useState } from 'react'
import { api } from '../lib/api'

function RoadmapPage() {
  const [activeStep, setActiveStep] = useState(0)
  const [roadmap, setRoadmap] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [hasPrediction, setHasPrediction] = useState(false)
  const [predictedRole, setPredictedRole] = useState('')

  // Load latest roadmap on mount
  useEffect(() => {
    const loadRoadmap = async () => {
      setLoading(true)
      try {
        const data = await api.getLatestRoadmap()
        setRoadmap(data)
        setHasPrediction(true)
        setPredictedRole(data.target_role)
      } catch (err) {
        // No roadmap found, check if there's a prediction
        try {
          const pred = await api.getLatestPrediction()
          setHasPrediction(true)
          setPredictedRole(pred.predicted_role)
        } catch {
          // No prediction either
          setHasPrediction(false)
        }
      } finally {
        setLoading(false)
      }
    }
    loadRoadmap()
  }, [])

  const handleGenerateRoadmap = async () => {
    setGenerating(true)
    setError('')
    try {
      const data = await api.generateRoadmapAuto()
      setRoadmap(data)
      setHasPrediction(true)
      setPredictedRole(data.target_role)
    } catch (err) {
      setError(err.message || 'Failed to generate roadmap.')
    } finally {
      setGenerating(false)
    }
  }

  const roadmapSteps = (roadmap?.items || []).map((item) => ({
    id: `${roadmap.id}-${item.step}`,
    title: item.title,
    duration: `${item.duration_weeks} week${item.duration_weeks === 1 ? '' : 's'}`,
    status: item.status,
    tasks: [item.description],
    resources: (item.resources || []).map((link) => ({ type: item.category, title: link, link })),
  }))

  if (loading) return (
    <section className="content">
      <div className="welcome-row mb-8"><div><p className="eyebrow green">EXECUTION PLAN</p><h1>Skill Acquisition Roadmap</h1><p className="subtle">Loading your roadmap...</p></div></div>
      <div className="panel py-16 text-center text-[#8fb298] font-[var(--mono)] text-sm">Loading...</div>
    </section>
  )

  // No prediction - show message to generate prediction first
  if (!roadmap && !hasPrediction) return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div>
          <p className="eyebrow green">EXECUTION PLAN</p>
          <h1>Skill Acquisition Roadmap</h1>
          <p className="subtle">No roadmap available.</p>
        </div>
      </div>
      <div className="panel py-16 text-center text-[#8fb298] font-[var(--mono)] text-sm">
        Generate your career prediction first.
      </div>
    </section>
  )

  // Has prediction but no roadmap - show generate button
  if (!roadmap && hasPrediction) return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div>
          <p className="eyebrow green">EXECUTION PLAN</p>
          <h1>Skill Acquisition Roadmap</h1>
          <p className="subtle">Target node: {predictedRole}. Ready to generate your personalized roadmap.</p>
        </div>
      </div>
      <div className="panel py-16 text-center">
        <p className="font-[var(--mono)] text-[#8fb298] mb-6">
          Your latest prediction shows <strong className="text-[var(--mint)]">{predictedRole}</strong>.
          Generate a personalized roadmap based on your skill gaps and profile.
        </p>
        {error && <p className="text-red-400 text-xs font-[var(--mono)] text-center mb-4">{error}</p>}
        <button
          className="primary-action px-16 py-4 text-base"
          onClick={handleGenerateRoadmap}
          disabled={generating}
          style={{ background: 'var(--green)', color: 'black' }}
        >
          {generating ? 'GENERATING...' : 'GENERATE ROADMAP →'}
        </button>
      </div>
    </section>
  )

  return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div>
          <p className="eyebrow green">EXECUTION PLAN</p>
          <h1>Skill Acquisition Roadmap</h1>
          <p className="subtle">Target node: {roadmap.target_role}. Estimated completion: {roadmap.total_duration_weeks} weeks.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {roadmapSteps.map((step, idx) => (
            <article
              key={step.id}
              className={`panel transition-all ${
                idx === activeStep
                  ? 'border-l-4 border-l-[var(--green)] shadow-[0_0_15px_rgba(73,239,131,0.1)]'
                  : step.status === 'locked'
                    ? 'opacity-60 border-[var(--border)] bg-opacity-20'
                    : 'border-[var(--border)]'
              }`}
            >
              <div className="panel-heading mb-4 border-b border-[var(--border)] pb-4 flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <span className={`w-8 h-8 flex items-center justify-center font-[var(--mono)] border ${idx === activeStep ? 'border-[var(--green)] text-[var(--green)] bg-[#07120a]' : 'border-[var(--border)] text-[#8fb298]'}`}>
                    {idx + 1}
                  </span>
                  <h2 className={`text-xl font-semibold m-0 ${idx === activeStep ? 'text-[var(--mint)]' : 'text-[#8fb298]'}`}>
                    {step.title}
                  </h2>
                </div>
                <span className="font-[var(--mono)] text-xs text-[#8fb298]">{step.duration}</span>
              </div>

              <div className="pl-12">
                <h4 className="text-[10px] text-[#8fb298] font-[var(--mono)] uppercase tracking-wider mb-3">Checklist</h4>
                <ul className="space-y-2 mb-6">
                  {step.tasks.map((task, i) => (
                    <li key={i} className="flex gap-3 text-sm text-[var(--text)]">
                      <input type="checkbox" className="mt-1 accent-[var(--green)] bg-transparent border-[var(--border)]" disabled={step.status === 'locked'} />
                      <span className={step.status === 'locked' ? 'text-[#8fb298]' : ''}>{task}</span>
                    </li>
                  ))}
                </ul>

                <h4 className="text-[10px] text-[#8fb298] font-[var(--mono)] uppercase tracking-wider mb-3">Recommended Resources</h4>
                <div className="flex flex-col gap-2">
                  {step.resources.map((res, i) => (
                    <a key={i} href={res.link} target="_blank" rel="noopener noreferrer" className="text-xs text-[var(--green)] font-[var(--mono)] hover:underline flex items-center gap-2">
                      <span className="px-2 py-1 bg-[#102316] border border-[#1f7134] text-[10px] uppercase">{res.type}</span>
                      {res.title}
                    </a>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>

        <div className="lg:col-span-1 space-y-6">
          <article className="panel">
            <div className="panel-heading mb-6 border-b border-[var(--border)] pb-4">
              <h2 className="text-xl font-semibold m-0 text-[var(--mint)]">Progress Tracker</h2>
            </div>
            <div className="flex flex-col items-center justify-center mb-6">
              <div className="relative w-32 h-32 flex items-center justify-center rounded-full border-4 border-[#16321f]">
                <div className="absolute inset-[-4px] rounded-full border-4 border-transparent border-t-[var(--green)] rotate-45"></div>
                <span className="font-[var(--mono)] text-2xl text-[var(--mint)]">0%</span>
              </div>
              <p className="text-xs text-[#8fb298] font-[var(--mono)] mt-4">0 OF {roadmapSteps.length} TASKS COMPLETE</p>
            </div>

            <button className="primary-action w-full" onClick={() => setActiveStep(prev => Math.min(prev + 1, roadmapSteps.length - 1))}>
              ADVANCE NODE <span>→</span>
            </button>
          </article>
        </div>
      </div>
    </section>
  )
}

export default RoadmapPage
