import { useEffect, useState } from 'react'
import { normalizeProfile } from '../../lib/profile'
import { api } from '../../lib/api'

function DashboardContent({ setActiveNav, notice, profile: savedProfile, latestPrediction }) {
  const profile = normalizeProfile(savedProfile)
  const hasProfile = Boolean(savedProfile)
  const skillCount = profile.programming_skills.length + profile.framework_skills.length + profile.tool_skills.length

  // Use backend's profile_completion field instead of local calculation
  const completion = savedProfile?.profile_completion || 0

  // Load latest prediction if not passed
  const [latestPred, setLatestPred] = useState(latestPrediction)
  const [loadingPred, setLoadingPred] = useState(!latestPrediction)

  useEffect(() => {
    if (latestPrediction) return
    const load = async () => {
      setLoadingPred(true)
      try {
        const data = await api.getLatestPrediction()
        setLatestPred(data)
      } catch {
        // No prediction yet
      } finally {
        setLoadingPred(false)
      }
    }
    load()
  }, [latestPrediction])

  const hasPrediction = Boolean(latestPred)
  const pred = latestPred

  return (
    <section className="content">
      <div className="welcome-row">
        <div>
          <p className="eyebrow green">CAREER INTELLIGENCE</p>
          <h1>Welcome back.</h1>
          <p className="subtle">
            {hasProfile
              ? `Your profile is ${completion}% complete.`
              : 'Complete your profile before running a prediction.'}
            {hasPrediction && ` Latest: ${pred.predicted_role} (${Math.round(pred.confidence * 100)}% confidence)`}
          </p>
        </div>
        <div className="system-status"><b className="pulse" /> {notice}</div>
      </div>

      <div className="tabs" role="tablist">
        <button className="selected">Overview</button>
      </div>

      {/* Quick stats */}
      <div className="stat-grid mb-6">
        <div className="stat-card">
          <span className="eyebrow">CGPA</span>
          <strong>{profile.cgpa || '—'} <em>/ 10.00</em></strong>
          <div className="meter"><span className="meter-fill" style={{ width: `${(profile.cgpa / 10) * 100}%` }} /></div>
        </div>
        <div className="stat-card">
          <span className="eyebrow">SKILL NODES</span>
          <strong>{skillCount} <em>ACTIVE</em></strong>
          <div className="skill-dots">
            {Array.from({ length: Math.min(skillCount, 12) }).map((_, i) => <i key={i} className="lit" />)}
            {Array.from({ length: Math.max(0, 12 - skillCount) }).map((_, i) => <i key={i} />)}
          </div>
        </div>
        <div className="stat-card">
          <span className="eyebrow">PROFILE COMPLETION</span>
          <strong>{completion}<em>%</em></strong>
          <div className="meter"><span className="meter-fill" style={{ width: `${completion}%` }} /></div>
        </div>
        <div className="stat-card">
          <span className="eyebrow">PROJECTS DEPLOYED</span>
          <strong>{String(profile.num_projects || 0).padStart(2, '0')} <em>VERIFIED</em></strong>
          <small className="text-[10px] font-[var(--mono)] text-[#8fb298] mt-2 block">
            + {profile.num_internships || 0} internship{profile.num_internships !== 1 ? 's' : ''}
          </small>
        </div>
      </div>

      {/* Latest Prediction Card */}
      {hasPrediction && (
        <article className="panel primary-panel mb-6" style={{ borderLeft: '4px solid var(--green)' }}>
          <div className="panel-heading">
            <div><span className="eyebrow">LATEST PREDICTION</span><h2 className="mt-2">{pred.predicted_role}</h2></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <span className="eyebrow">CONFIDENCE</span>
              <strong className="text-2xl text-[var(--mint)]">{Math.round(pred.confidence * 100)}%</strong>
            </div>
            <div>
              <span className="eyebrow">READINESS</span>
              <strong className="text-2xl text-[var(--mint)]">{Math.round(pred.placement_readiness_score)}%</strong>
            </div>
            <div>
              <span className="eyebrow">PREDICTED</span>
              <strong className="text-sm text-[var(--text)]">{new Date(pred.created_at).toLocaleDateString()}</strong>
            </div>
          </div>
          <div className="mt-4 flex gap-3">
            <button className="primary-action" onClick={() => setActiveNav('Prediction')}>
              VIEW FULL RESULT <span>→</span>
            </button>
            <button className="primary-action" style={{ background: 'transparent', color: 'var(--green)', border: '1px solid var(--green)' }}
              onClick={() => setActiveNav('Roadmap')}>
              VIEW ROADMAP <span>→</span>
            </button>
          </div>
        </article>
      )}

      {/* CTA Cards */}
      <div className="dashboard-grid">
        <article className="panel primary-panel">
          <div className="panel-heading">
            <div><span className="eyebrow">QUICK ACTIONS</span><h2 className="mt-2">Start your analysis.</h2></div>
          </div>
          <div className="prediction-content">
            <div className="orbit">
              <i /><i />
              <b>{profile.programming_skills.length}<small> langs</small></b>
            </div>
            <div>
              <p className="prediction-copy">
                Fill in your Profile data, then run the Prediction engine to receive your Career sector, Placement probability, and a personalised Readiness score.
              </p>
              <div className="flex flex-col gap-3">
                <button className="primary-action" onClick={() => setActiveNav('Profile')}>
                  EDIT PROFILE <span>→</span>
                </button>
                <button className="primary-action" style={{ background: 'transparent', color: 'var(--green)', border: '1px solid var(--green)' }}
                  onClick={() => {
                    if (hasProfile && completion === 100) {
                      setActiveNav('Prediction')
                    } else {
                      alert('Please complete your profile first.')
                      setActiveNav('Profile')
                    }
                  }}>
                  {hasPrediction ? 'RE-RUN PREDICTION' : 'RUN PREDICTION'} <span>→</span>
                </button>
              </div>
            </div>
          </div>
        </article>

        <article className="panel readiness-panel">
          <span className="eyebrow">READINESS SNAPSHOT</span>
          <div className="readiness-score">
            {hasPrediction ? (
              <>
                <strong>{Math.round(pred.placement_readiness_score)}</strong>
                <span>/ 100</span>
              </>
            ) : (
              <span className="text-[#8fb298]">—</span>
            )}
          </div>
          <p>
            {hasPrediction
              ? `Placement readiness from your latest prediction.`
              : 'Run a prediction to see your placement readiness breakdown.'}
          </p>
          <button className="link-button" onClick={() => setActiveNav('Roadmap')}>
            View Roadmap →
          </button>
        </article>
      </div>
    </section>
  )
}

export default DashboardContent
