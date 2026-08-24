const TOKEN_KEY = 'matrix_token'
const USER_KEY = 'matrix_user'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function getToken() { return localStorage.getItem(TOKEN_KEY) }
export function getUser() { try { return JSON.parse(localStorage.getItem(USER_KEY)) } catch { return null } }
export function isLoggedIn() { return !!getToken() }

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export async function getCurrentUser() {
  const token = getToken()
  if (!token) return null

  const res = await fetch(`${BASE_URL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    if (res.status === 401 || res.status === 403) logout()
    throw new Error('Unable to restore your authenticated session')
  }
  const user = await res.json()
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  return user
}

export async function login(email, password) {
  // Never retain a previous user's identity while a new login is in progress.
  logout()
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)

  const res = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Login failed')
  }

  const { access_token } = await res.json()
  localStorage.setItem(TOKEN_KEY, access_token)

  // Fetch user info
  try {
    return await getCurrentUser()
  } catch (error) {
    logout()
    throw error
  }
}

export async function register(email, username, full_name, password) {
  const res = await fetch(`${BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, full_name, password }),
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Registration failed')
  }

  return login(email, password)
}
