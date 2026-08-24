import './LoginPage.css'
import { useState } from 'react'
import { login, register } from '../lib/auth'

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState('login')  // 'login' | 'register'
  const [fields, setFields] = useState({ email: '', password: '', username: '', full_name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (k) => (e) => setFields(p => ({ ...p, [k]: e.target.value }))

  const codeColumns = Array.from({ length: 20 }, (_, i) => (
    <span key={i} style={{ '--column': i, '--delay': `${-(i * 0.73)}s` }}>
      {i % 2 ? '010011\nMODEL\n100101\nPATH\n011010\nDATA\n101001\nNODE' : 'CAREER\n011010\nSIGNAL\n110101\nFUTURE\n001101\nSKILLS'}
    </span>
  ))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (mode === 'login') {
        await login(fields.email, fields.password)
      } else {
        await register(fields.email, fields.username, fields.full_name, fields.password)
      }
      onLogin()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="login-page">
      <div className="matrix-rain" aria-hidden="true">{codeColumns}</div>
      <div className="matrix-grid" aria-hidden="true" />

      <section className="login-card" aria-labelledby="login-title">
        <div className="login-brand"><span>M</span> MATRIX<i>_</i></div>
        <p className="login-kicker">CAREER INTELLIGENCE PLATFORM</p>
        <h1 id="login-title">{mode === 'login' ? 'Welcome back.' : 'Create account.'}</h1>
        <p className="login-intro">
          {mode === 'login' ? 'Sign in to continue building your career path.' : 'Join the Matrix Career Intelligence Platform.'}
        </p>

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <>
              <label htmlFor="full_name">FULL NAME</label>
              <div className="terminal-input">
                <span>&gt;</span>
                <input id="full_name" type="text" placeholder="Alex Rivera" value={fields.full_name} onChange={set('full_name')} required />
              </div>
              <label htmlFor="username">USERNAME</label>
              <div className="terminal-input">
                <span>&gt;</span>
                <input id="username" type="text" placeholder="alexrivera" value={fields.username} onChange={set('username')} required minLength={3} />
              </div>
            </>
          )}

          <label htmlFor="email">EMAIL ADDRESS</label>
          <div className="terminal-input">
            <span>&gt;</span>
            <input id="email" type="email" placeholder="you@example.com" autoComplete="email" value={fields.email} onChange={set('email')} required />
          </div>

          <div className="label-row">
            <label htmlFor="password">PASSWORD</label>
          </div>
          <div className="terminal-input">
            <span>&gt;</span>
            <input id="password" type="password" placeholder="Enter your password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={fields.password} onChange={set('password')} required minLength={8} />
          </div>

          {error && (
            <p style={{ color: '#ef4444', fontFamily: 'var(--mono)', fontSize: '11px', margin: '8px 0', padding: '8px', border: '1px solid #7f1d1d', background: '#450a0a22' }}>
              ✗ {error}
            </p>
          )}

          <button className="login-submit" type="submit" disabled={loading}>
            {loading ? 'CONNECTING...' : mode === 'login' ? 'ACCESS DASHBOARD →' : 'CREATE ACCOUNT →'}
          </button>
        </form>

        <p className="create-account">
          {mode === 'login' ? "New to Matrix? " : "Already have an account? "}
          <button type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
            {mode === 'login' ? 'Create an account' : 'Sign in'}
          </button>
        </p>
        <p className="secure-line"><b /> SECURE SESSION · JWT AUTHENTICATION</p>
      </section>
      <p className="login-footer">MATRIX CAREER INTELLIGENCE <span>v1.0.0</span></p>
    </main>
  )
}

export default LoginPage
