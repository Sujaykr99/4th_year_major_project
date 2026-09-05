import { getToken } from './auth'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function authHeaders() {
  const token = getToken()
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function post(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text()
    try {
      const data = JSON.parse(text)
      throw new Error(data.detail || data.message || text)
    } catch (e) {
      if (e.message !== text) throw e // rethrow if not JSON parse error
      throw new Error(text)
    }
  }
  return res.json()
}

async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`, { headers: authHeaders() })
  if (!res.ok) {
    const text = await res.text()
    try {
      const data = JSON.parse(text)
      throw new Error(data.detail || data.message || text)
    } catch (e) {
      if (e.message !== text) throw e
      throw new Error(text)
    }
  }
  return res.json()
}

async function put(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export const api = {
  predictBoth: (input) => post('/api/v1/predict/both', input),
  predictCareer: (input) => post('/api/v1/predict/career', input),
  predictPlacement: (input) => post('/api/v1/predict/placement', input),
  predictCareerAuto: () => post('/api/v1/predict/career/auto', {}),
  predictBothAuto: () => post('/api/v1/predict/both/auto', {}),
  getLatestPrediction: () => get('/api/v1/predict/latest'),
  getProfile: () => get('/api/v1/profile/me'),
  getPredictionProfile: () => get('/api/v1/profile/prediction'),
  createProfile: (input) => post('/api/v1/profile/', input),
  updateProfile: (input) => put('/api/v1/profile/me', input),
  getPredictionHistory: () => get('/api/v1/predict/history'),
  getRoadmaps: () => get('/api/v1/roadmap/me'),
  getLatestRoadmap: () => get('/api/v1/roadmap/latest'),
  generateRoadmapAuto: () => post('/api/v1/roadmap/generate-auto', {}),
  getRoadmap: (target_role, current_skills) =>
    post('/api/v1/roadmap/generate', { target_role, current_skills, time_commitment_hours_per_week: 10 }),
}

export default api
