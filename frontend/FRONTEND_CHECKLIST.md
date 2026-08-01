# Matrix Frontend Checklist

This checklist tracks frontend work only. Backend, ML artifacts, database setup, and API implementation remain separate.

## 1. Foundation

- [x] Create the frontend page/component structure.
- [x] Configure client-side routing and protected-route placeholder behavior.
- [ ] Define shared design tokens, layout shell, responsive navigation, and reusable UI primitives.
- [ ] Add a centralized API-service layer with environment-based base URL (when integration begins).

## 2. Public experience

- [x] Build Matrix-inspired login UI.
- [x] Build Matrix code-rain background and dashboard-door reveal.
- [ ] Build registration screen.
- [ ] Add real auth validation, loading, errors, and JWT storage after backend verification.

## 3. Student profile

- [ ] Build profile input form: education, CGPA, skills, projects, internships, certifications, interests, and aptitude.
- [ ] Add local field validation and draft/mock profile state.
- [ ] Add edit and completion states.

## 4. Dashboard

- [x] Create initial static Matrix dashboard prototype.
- [ ] Refactor it into reusable dashboard components.
- [ ] Build dashboard overview: welcome, completion, CGPA, skills, quick actions, and recent activity.
- [ ] Add responsive sidebar, top bar, and empty/loading/error states.

## 5. Prediction and results

- [ ] Build career-prediction form page.
- [ ] Build result UI: career card, confidence, readiness, skill gaps, explainability, and roadmap preview.
- [ ] Build history screen.

## 6. Roadmap and settings

- [ ] Build roadmap timeline/checklist.
- [ ] Build profile/account settings and logout screen.

## 7. Integration and polish

- [ ] Connect auth, profile, prediction, roadmap, and history endpoints.
- [ ] Add API loading, success, empty, and error states.
- [ ] Add approved Motion animations from `ANIMATION_SPEC.md`.
- [ ] Verify keyboard access, reduced-motion support, and mobile/tablet layouts.
- [ ] Build production frontend and run final QA.
