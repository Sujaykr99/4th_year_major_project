/**
 * Profile defaults for the prediction form. Persisted through the authenticated
 * profile API; never stored under a shared browser key.
 */

export const EMPTY_PROFILE = {
  // --- CAREER MODEL FEATURES ---
  programming_skills: [],       // multi-select
  framework_skills: [],
  tool_skills: [],
  soft_skills: [],
  years_code: 0,
  years_code_pro: 0,
  ed_level: 2,                  // 0-5 (Bachelor=2)
  work_exp_count: 0,
  is_developer: 1,
  remote_pref: 1,               // 0=onsite 1=hybrid 2=remote

  // --- PLACEMENT PREDICTION FEATURES ---
  age: 21,
  gender: 'Male',
  cgpa: 7.5,
  branch: 'Computer Science',
  college_tier: 2,              // 1=top 2=mid 3=other
  num_internships: 0,
  num_projects: 0,
  certifications_count: 0,
  coding_skill_score: 60,
  aptitude_score: 60,
  communication_skill_score: 60,
  logical_reasoning_score: 60,
  hackathon_participation: 0,
  github_repos: 0,
  linkedin_connections: 0,
  mock_interview_score: 60,
  attendance_percentage: 75,
  backlogs: 0,
  extracurricular_score: 50,
  leadership_score: 50,
  volunteer_experience: 'No',
  sleep_hours: 7,
  study_hours_per_day: 4,
  graduation_year: 2026,
  university_tier: 2,

  // --- READINESS SCORE FEATURES ---
  // (derived from above: cgpa, backlogs, programming_skills, num_projects, etc.)
}

export function normalizeProfile(data) {
  return { ...EMPTY_PROFILE, ...(data || {}) }
}
