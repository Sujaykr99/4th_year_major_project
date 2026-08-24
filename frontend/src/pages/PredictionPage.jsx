import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import ArcReactor from '../components/common/ArcReactor'
import api from '../lib/api'

function ScoreBar({ label, value, color = 'var(--green)' }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between text-[10px] font-[var(--mono)] text-[#8fb298] mb-1">
        <span>{label}</span><span style={{ color }}>{Math.round(value)}%</span>
      </div>
      <div className="h-1 bg-[#16321f] overflow-hidden">
        <motion.div initial={{ width: 0 }} animate={{ width: `${value}%` }} transition={{ duration: 1, delay: 0.3 }}
          className="h-full" style={{ background: color, boxShadow: `0 0 8px ${color}66` }} />
      </div>
    </div>
  )
}

function PredictionPage({ setActiveNav, profile: savedProfile }) {
  const [phase, setPhase] = useState('idle')   // idle | loading | results
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Check if profile is complete
  const isProfileComplete = savedProfile && savedProfile.profile_completion === 100
  const completion = savedProfile?.profile_completion || 0

  // Load latest prediction on mount
  useEffect(() => {
    const loadLatest = async () => {
      try {
        const data = await api.getLatestPrediction()
        setResult(data)
        setPhase('results')
      } catch {
        // No prediction yet, stay in idle
      }
    }
    loadLatest()
  }, [])

  const runPrediction = async () => {
    setPhase('loading')
    setError(null)
    try {
      if (!savedProfile) throw new Error('Complete and save your profile before running a prediction.')
      const data = await api.predictBothAuto()
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(err.message || 'Prediction could not be completed.')
      setPhase('idle')
      return
    }
    setPhase('results')
  }

  if (phase === 'idle') return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div>
          <p className="eyebrow green">CAREER INTELLIGENCE</p>
          <h1>Run Prediction Engine</h1>
          <p className="subtle">Analyzes your Profile to predict Career, Placement & Readiness simultaneously.</p>
        </div>
      </div>
      <div className="panel flex flex-col items-center py-24 gap-8">
        {!isProfileComplete && (
          <div className="text-center mb-6">
            <div className="text-red-400 text-xs font-[var(--mono)] text-center mb-4">
              {!savedProfile
                ? 'No profile found. Create your profile first.'
                : `Profile is {completion}% complete. Complete all required fields to enable prediction.`}
            </div>
            <p className="font-[var(--mono)] text-xs text-[#8fb298] text-center max-w-sm mb-6">
              {`Required fields: CGPA, University Tier, Graduation Year, Skills (Programming/Framework/Tool/Soft), Projects, Internships, Hackathons, Certifications`}
            </p>
            <button
              className="primary-action px-16 py-4 text-base"
              onClick={() => setActiveNav('Profile')}
              style={{ background: 'var(--green)', color: 'black' }}
            >
              {!savedProfile ? 'CREATE PROFILE →' : 'COMPLETE PROFILE →'}
            </button>
          </div>
        )}

        {isProfileComplete && (
          <>
            {error && <p className="text-red-400 text-xs font-[var(--mono)] text-center">{error}</p>}
            <p className="font-[var(--mono)] text-xs text-[#8fb298] text-center max-w-sm">
              {`> Profile data loaded (100% complete). Three models will run:\n[1] Career Sector + Role\n[2] Placement Probability\n[3] Readiness Score`}
            </p>
            <button className="primary-action px-16 py-4 text-base" onClick={runPrediction}>
              INITIATE ANALYSIS →
            </button>
          </>
        )}
      </div>
    </section>
  )

  if (phase === 'loading') return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div><p className="eyebrow green">ENGINE ACTIVE</p><h1>Career Trajectory Engine</h1></div>
        <div className="system-status"><b className="pulse" /> PROCESSING</div>
      </div>
      <div className="panel flex flex-col items-center py-10">
        <ArcReactor onComplete={() => {}} />
      </div>
    </section>
  )

  const career = result?.career_prediction
  const placement = result?.placement_prediction
  const isPlaced = placement?.predicted_status === 'Placed'

  return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div><p className="eyebrow green">ANALYSIS COMPLETE</p><h1>Prediction Results</h1></div>
        <button className="primary-action" onClick={runPrediction}>RE-ANALYZE →</button>
      </div>
      {error && <p className="font-[var(--mono)] text-[10px] text-[#8fb298] mb-4">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">

        {/* 1. Career */}
        <motion.article initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}
          className="panel border-l-4 border-l-[var(--green)]">
          <span className="eyebrow green">01 / CAREER ROLE</span>
          <h2 className="text-3xl font-bold text-[var(--mint)] tracking-tight mt-2 mb-1">{career?.role}</h2>
          <p className="code mb-4">SECTOR: {career?.sector}</p>
          <ScoreBar label="Role Confidence" value={(career?.role_confidence || 0) * 100} />
          <ScoreBar label="Sector Confidence" value={(career?.sector_confidence || 0) * 100} color="var(--mint)" />
          <div className="mt-4 border-t border-[var(--border)] pt-4">
            <span className="text-[10px] text-[#8fb298] font-[var(--mono)] uppercase tracking-wider">Other Matches</span>
            {(career?.top_predictions || []).slice(1).map(p => (
              <div key={p.role} className="flex justify-between text-xs font-[var(--mono)] text-[#8fb298] mt-2">
                <span>{p.role}</span><span>{Math.round(p.probability * 100)}%</span>
              </div>
            ))}
          </div>
        </motion.article>

        {/* 2. Placement */}
        <motion.article initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className={`panel border-l-4 ${isPlaced ? 'border-l-[var(--green)]' : 'border-l-red-500'}`}>
          <span className="eyebrow green">02 / PLACEMENT</span>
          <h2 className={`text-3xl font-bold tracking-tight mt-2 mb-1 ${isPlaced ? 'text-[var(--mint)]' : 'text-red-400'}`}>
            {placement?.predicted_status}
          </h2>
          <p className="code mb-4">{placement?.readiness_level?.toUpperCase()} READINESS</p>
          <ScoreBar label="Placement Probability" value={(placement?.placement_probability || 0) * 100} color={isPlaced ? 'var(--green)' : '#ef4444'} />
          <ScoreBar label="Overall Readiness" value={placement?.readiness_score || 0} color="var(--mint)" />
          <div className="mt-4 border-t border-[var(--border)] pt-4 space-y-1">
            {Object.entries(placement?.readiness_breakdown || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between text-[10px] font-[var(--mono)] text-[#8fb298]">
                <span>{k.replace('_', ' ').toUpperCase()}</span><span>{v}%</span>
              </div>
            ))}
          </div>
        </motion.article>

        {/* 3. Skill Gaps + Recommendations */}
        <motion.article initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="panel border-l-4 border-l-yellow-600">
          <span className="eyebrow" style={{ color: '#ca8a04' }}>03 / SKILL GAPS</span>
          <h2 className="text-xl font-bold text-yellow-200 mt-2 mb-4">Action Required</h2>
          <div className="space-y-2 mb-6">
            {Object.entries(career?.skill_gaps || {}).map(([skill, reasons]) => (
              <div key={skill} className="flex gap-3 text-xs font-[var(--mono)] border border-yellow-900/40 p-2 bg-yellow-900/5">
                <span className="text-yellow-500">!</span>
                <div><div className="text-yellow-200">{skill}</div><div className="text-[#8fb298]">{Array.isArray(reasons) ? reasons[0] : reasons}</div></div>
              </div>
            ))}
          </div>
          <div className="border-t border-[var(--border)] pt-4">
            <span className="text-[10px] text-[#8fb298] font-[var(--mono)] uppercase tracking-wider">Recommendations</span>
            <ul className="mt-2 space-y-1">
              {(placement?.recommendations || []).map((r, i) => (
                <li key={i} className="text-xs text-[#8fb298] font-[var(--mono)] flex gap-2"><span className="text-[var(--green)]">›</span>{r}</li>
              ))}
            </ul>
          </div>
        </motion.article>
      </div>

      {/* Go to Roadmap */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
        className="panel flex items-center justify-between">
        <div>
          <p className="eyebrow green">NEXT STEP</p>
          <h3 className="text-xl font-semibold text-[var(--text)] m-0">Generate your personalised roadmap based on these results.</h3>
        </div>
        <button className="primary-action px-10" onClick={() => setActiveNav('Roadmap')}>VIEW ROADMAP →</button>
      </motion.div>
    </section>
  )
}

export default PredictionPage
