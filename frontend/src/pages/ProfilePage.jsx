import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { normalizeProfile } from '../lib/profile'

const PROGRAMMING = ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'SQL', 'R', 'PHP', 'Swift', 'Kotlin', 'Ruby']
const FRAMEWORKS = ['React', 'Node.js', 'Vue.js', 'Angular', 'Django', 'Flask', 'FastAPI', 'Spring', 'Express', 'ASP.NET Core', 'Next.js']
const TOOLS = ['AWS', 'Google Cloud', 'Azure', 'Docker', 'Kubernetes', 'Linux', 'Git', 'GitHub Actions', 'Jenkins', 'Terraform', 'Ansible', 'PostgreSQL', 'MongoDB', 'Redis', 'Firebase']
const SOFT_SKILLS = ['Communication', 'Leadership', 'Problem Solving', 'Teamwork', 'Critical Thinking', 'Time Management']

function SkillToggle({ label, options, selected, onChange }) {
  const toggle = (s) => onChange(selected.includes(s) ? selected.filter(x => x !== s) : [...selected, s])
  return (
    <div className="mb-6">
      <h4 className="text-[10px] text-[#8fb298] font-[var(--mono)] uppercase tracking-wider mb-3">{label}</h4>
      <div className="flex flex-wrap gap-2">
        {options.map(s => (
          <button key={s} onClick={() => toggle(s)}
            className={`px-3 py-1.5 border text-xs font-[var(--mono)] transition-all ${selected.includes(s) ? 'border-[var(--green)] bg-[var(--green)] text-black font-bold shadow-[0_0_8px_rgba(73,239,131,0.3)]' : 'border-[var(--border)] bg-transparent text-[#8fb298] hover:border-[var(--green)] hover:text-[var(--green)]'}`}>
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] text-[#8fb298] font-[var(--mono)] uppercase tracking-wider">{label}</label>
      {children}
    </div>
  )
}

const inputCls = "bg-[#07120a] border border-[var(--border)] text-[var(--text)] p-2.5 text-sm focus:border-[var(--green)] outline-none font-[var(--mono)] w-full"
const selectCls = inputCls

function ProfilePage({ profile, onProfileSaved }) {
  const [form, setForm] = useState(normalizeProfile(profile?.prediction_profile))
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => setForm(normalizeProfile(profile?.prediction_profile)), [profile])

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }))
  const numSet = (k) => (e) => set(k, Number(e.target.value))

  const handleSave = async () => {
    setError('')
    const payload = { cgpa: form.cgpa, graduation_year: form.graduation_year, prediction_profile: form }
    try {
      const savedProfile = profile ? await api.updateProfile(payload) : await api.createProfile(payload)
      onProfileSaved(savedProfile)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch {
      setError('Profile could not be saved. Please try again.')
    }
  }

  return (
    <section className="content">
      <div className="welcome-row mb-8">
        <div>
          <p className="eyebrow green">SYSTEM CALIBRATION</p>
          <h1>Student Profile Node</h1>
          <p className="subtle">All fields feed directly into Career, Placement & Readiness predictions.</p>
        </div>
      </div>

      <div className="space-y-6">

        {/* CAREER MODEL FEATURES */}
        <article className="panel">
          <h2 className="text-sm text-[var(--mint)] font-[var(--mono)] uppercase tracking-wider mb-6 border-b border-[var(--border)] pb-3">Career Model Features</h2>
          <SkillToggle label="Programming Languages" options={PROGRAMMING} selected={form.programming_skills} onChange={v => set('programming_skills', v)} />
          <SkillToggle label="Frameworks & Libraries" options={FRAMEWORKS} selected={form.framework_skills} onChange={v => set('framework_skills', v)} />
          <SkillToggle label="Cloud, DevOps & Databases (Tools)" options={TOOLS} selected={form.tool_skills} onChange={v => set('tool_skills', v)} />
          <SkillToggle label="Soft Skills" options={SOFT_SKILLS} selected={form.soft_skills} onChange={v => set('soft_skills', v)} />

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-2">
            <Field label="Years Coding (Total)">
              <input type="number" min="0" value={form.years_code} onChange={numSet('years_code')} className={inputCls} />
            </Field>
            <Field label="Years Coding (Professional)">
              <input type="number" min="0" value={form.years_code_pro} onChange={numSet('years_code_pro')} className={inputCls} />
            </Field>
            <Field label="Education Level (0-5)">
              <input type="number" min="0" max="5" value={form.ed_level} onChange={numSet('ed_level')} className={inputCls} />
            </Field>
            <Field label="Work Experience (roles)">
              <input type="number" min="0" max="5" value={form.work_exp_count} onChange={numSet('work_exp_count')} className={inputCls} />
            </Field>
            <Field label="Is Developer (0/1)">
              <select value={form.is_developer} onChange={(e) => set('is_developer', Number(e.target.value))} className={selectCls}>
                <option value={1}>Yes (1)</option>
                <option value={0}>No (0)</option>
              </select>
            </Field>
            <Field label="Remote Preference">
              <select value={form.remote_pref} onChange={(e) => set('remote_pref', Number(e.target.value))} className={selectCls}>
                <option value={0}>On-site (0)</option>
                <option value={1}>Hybrid (1)</option>
                <option value={2}>Remote (2)</option>
              </select>
            </Field>
          </div>
        </article>

        {/* PLACEMENT FEATURES */}
        <article className="panel">
          <h2 className="text-sm text-[var(--mint)] font-[var(--mono)] uppercase tracking-wider mb-6 border-b border-[var(--border)] pb-3">Placement Prediction Features</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Field label="Age"><input type="number" min="18" max="35" value={form.age} onChange={numSet('age')} className={inputCls} /></Field>
            <Field label="Gender">
              <select value={form.gender} onChange={e => set('gender', e.target.value)} className={selectCls}>
                <option>Male</option><option>Female</option><option>Other</option>
              </select>
            </Field>
            <Field label="CGPA (0-10)"><input type="number" min="0" max="10" step="0.1" value={form.cgpa} onChange={numSet('cgpa')} className={inputCls} /></Field>
            <Field label="Branch">
              <select value={form.branch} onChange={e => set('branch', e.target.value)} className={selectCls}>
                {['Computer Science', 'IT', 'ECE', 'EEE', 'Mechanical', 'Civil', 'Other'].map(b => <option key={b}>{b}</option>)}
              </select>
            </Field>
            <Field label="College Tier (1-3)">
              <select value={form.college_tier} onChange={e => set('college_tier', Number(e.target.value))} className={selectCls}>
                <option value={1}>Tier 1 (Top)</option><option value={2}>Tier 2 (Mid)</option><option value={3}>Tier 3</option>
              </select>
            </Field>
            <Field label="Internships"><input type="number" min="0" value={form.num_internships} onChange={numSet('num_internships')} className={inputCls} /></Field>
            <Field label="Projects"><input type="number" min="0" value={form.num_projects} onChange={numSet('num_projects')} className={inputCls} /></Field>
            <Field label="Certifications"><input type="number" min="0" value={form.certifications_count} onChange={numSet('certifications_count')} className={inputCls} /></Field>
            <Field label="Coding Skill (0-100)"><input type="number" min="0" max="100" value={form.coding_skill_score} onChange={numSet('coding_skill_score')} className={inputCls} /></Field>
            <Field label="Aptitude Score (0-100)"><input type="number" min="0" max="100" value={form.aptitude_score} onChange={numSet('aptitude_score')} className={inputCls} /></Field>
            <Field label="Communication (0-100)"><input type="number" min="0" max="100" value={form.communication_skill_score} onChange={numSet('communication_skill_score')} className={inputCls} /></Field>
            <Field label="Logical Reasoning (0-100)"><input type="number" min="0" max="100" value={form.logical_reasoning_score} onChange={numSet('logical_reasoning_score')} className={inputCls} /></Field>
            <Field label="Hackathons"><input type="number" min="0" value={form.hackathon_participation} onChange={numSet('hackathon_participation')} className={inputCls} /></Field>
            <Field label="GitHub Repos"><input type="number" min="0" value={form.github_repos} onChange={numSet('github_repos')} className={inputCls} /></Field>
            <Field label="LinkedIn Connections"><input type="number" min="0" value={form.linkedin_connections} onChange={numSet('linkedin_connections')} className={inputCls} /></Field>
            <Field label="Mock Interview (0-100)"><input type="number" min="0" max="100" value={form.mock_interview_score} onChange={numSet('mock_interview_score')} className={inputCls} /></Field>
            <Field label="Attendance %"><input type="number" min="0" max="100" value={form.attendance_percentage} onChange={numSet('attendance_percentage')} className={inputCls} /></Field>
            <Field label="Backlogs"><input type="number" min="0" value={form.backlogs} onChange={numSet('backlogs')} className={inputCls} /></Field>
            <Field label="Extracurricular (0-100)"><input type="number" min="0" max="100" value={form.extracurricular_score} onChange={numSet('extracurricular_score')} className={inputCls} /></Field>
            <Field label="Leadership Score (0-100)"><input type="number" min="0" max="100" value={form.leadership_score} onChange={numSet('leadership_score')} className={inputCls} /></Field>
            <Field label="Volunteer Experience">
              <select value={form.volunteer_experience} onChange={e => set('volunteer_experience', e.target.value)} className={selectCls}>
                <option>No</option><option>Yes</option>
              </select>
            </Field>
            <Field label="Sleep Hours / Day"><input type="number" min="0" max="12" value={form.sleep_hours} onChange={numSet('sleep_hours')} className={inputCls} /></Field>
            <Field label="Study Hours / Day"><input type="number" min="0" max="16" value={form.study_hours_per_day} onChange={numSet('study_hours_per_day')} className={inputCls} /></Field>
            <Field label="Graduation Year"><input type="number" min="2020" max="2030" value={form.graduation_year} onChange={numSet('graduation_year')} className={inputCls} /></Field>
          </div>
        </article>

        {/* SAVE */}
        <div className="flex justify-end">
          {error && <p className="mr-auto text-red-400 text-xs font-[var(--mono)]">{error}</p>}
          <button className="primary-action px-10" onClick={handleSave}>
            {saved ? '✓ PROFILE SAVED' : 'SAVE PROFILE DATA →'}
          </button>
        </div>
      </div>
    </section>
  )
}

export default ProfilePage
