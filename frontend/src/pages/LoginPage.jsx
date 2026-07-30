import './LoginPage.css'

function LoginPage({ onLogin }) {
  const codeColumns = Array.from({ length: 20 }, (_, index) => (
    <span key={index} style={{ '--column': index, '--delay': `${-(index * 0.73)}s` }}>
      {index % 2 ? '010011\nMODEL\n100101\nPATH\n011010\nDATA\n101001\nNODE' : 'CAREER\n011010\nSIGNAL\n110101\nFUTURE\n001101\nSKILLS'}
    </span>
  ))

  const submitLogin = (event) => {
    event.preventDefault()
    onLogin()
  }

  return (
    <main className="login-page">
      <div className="matrix-rain" aria-hidden="true">{codeColumns}</div>
      <div className="matrix-grid" aria-hidden="true" />

      <section className="login-card" aria-labelledby="login-title">
        <div className="login-brand"><span>M</span> MATRIX<i>_</i></div>
        <p className="login-kicker">CAREER INTELLIGENCE PLATFORM</p>
        <h1 id="login-title">Welcome back.</h1>
        <p className="login-intro">Sign in to continue building your career path.</p>

        <form onSubmit={submitLogin}>
          <label htmlFor="email">EMAIL ADDRESS</label>
          <div className="terminal-input"><span>&gt;</span><input id="email" type="email" placeholder="you@example.com" autoComplete="email" required /></div>

          <div className="label-row"><label htmlFor="password">PASSWORD</label><button type="button">Forgot password?</button></div>
          <div className="terminal-input"><span>&gt;</span><input id="password" type="password" placeholder="Enter your password" autoComplete="current-password" required /></div>

          <div className="login-options"><label className="check-label"><input type="checkbox" /> <span />Remember this device</label></div>
          <button className="login-submit" type="submit">ACCESS DASHBOARD <b>→</b></button>
        </form>

        <p className="create-account">New to Matrix? <button type="button">Create an account</button></p>
        <p className="secure-line"><b /> SECURE SESSION · YOUR DATA STAYS PRIVATE</p>
      </section>
      <p className="login-footer">MATRIX CAREER INTELLIGENCE <span>v0.1.0</span></p>
    </main>
  )
}

export default LoginPage
