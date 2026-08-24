# MATRIX — Career Intelligence & Placement Readiness Platform

> **Understand your skills. Discover your career. Build your roadmap.**

MATRIX is a full-stack AI/ML-powered career guidance platform designed for students to understand their career direction, evaluate placement readiness, identify skill gaps, and follow a personalized learning roadmap.

Instead of repeatedly asking the student for the same information, MATRIX uses a persistent profile as the central source of truth for the complete system.

---

## 🚀 What is MATRIX?

Students often know what technologies they are learning but don't know:

- Which career domain suits them?
- Which role should they target?
- What skills are missing?
- Are they actually placement-ready?
- What should they learn next?
- Which projects or certifications should they work on?

MATRIX brings these decisions into one platform.

```text
                 USER
                   │
             Register / Login
                   │
                   ▼
              USER PROFILE
                   │
          ┌────────┼─────────┐
          │        │         │
          ▼        ▼         ▼
     Prediction  Readiness  Profile
          │        │
          ▼        ▼
      Career     Score
       Role        │
          │        │
          └────┬───┘
               ▼
          SKILL GAPS
               │
               ▼
           ROADMAP
               │
               ▼
        LEARN → BUILD → IMPROVE
✨ Main Features
🎯 Career Prediction

MATRIX uses a hierarchical career prediction approach:

Student Profile
       │
       ▼
 Sector Prediction
       │
       ▼
  Role Prediction

Instead of directly predicting every possible career role, the system first determines the suitable career sector and then predicts a role within that sector.

Supported career areas include:

Web Development
Backend & Data Engineering
Cloud & DevOps
Security & Infrastructure
Other trained career sectors

The prediction system also provides alternative career predictions and confidence information.

🧠 Profile-Based Intelligence

The user's profile contains the information required by the ML pipeline.

The system works with information such as:

Programming skills
Framework skills
Tools and platforms
Database technologies
Experience
Education
Projects
Internships
Certifications
Career preferences
Placement-related information

The frontend profile is mapped into the exact feature representation expected by the trained models.

📊 Placement Prediction

MATRIX contains a separate placement prediction pipeline.

It evaluates information such as:

Age
Gender
CGPA
Branch
College tier
Internships
Projects
Certifications
Coding skill
Aptitude
Communication
Logical reasoning
Hackathons
GitHub repositories
LinkedIn connections
Mock interview performance
Attendance
Backlogs
Extracurricular activities
Leadership
Volunteer experience
Sleep hours
Study hours

The placement model is independent from the career prediction model.

📈 Placement Readiness Score

MATRIX also calculates a separate placement readiness score from 0–100.

The readiness system evaluates:

Component	Weight
Academic	25%
Technical Skills	20%
Projects	20%
Experience	15%
Soft Skills	10%
Achievements	10%

The result contains:

Overall readiness score
Readiness level
Component breakdown
Recommendations
Readiness Levels
Not Ready
    ↓
Needs Improvement
    ↓
Moderately Ready
    ↓
Ready
    ↓
Highly Ready
🗺️ Personalized Roadmap

After understanding the user's profile and target career, MATRIX generates a personalized roadmap.

Roadmap items can contain:

Skills
Projects
Courses
Certifications
Learning resources
Priority
Estimated duration
Progress status
Target role

The roadmap follows:

Current Skills
      ↓
Target Career
      ↓
Skill Gaps
      ↓
Learning Roadmap
      ↓
Projects
      ↓
Career Readiness
👤 Persistent User Experience

MATRIX is designed around user-specific persistent data.

New User
Register
   ↓
Dashboard
   ↓
Complete Profile
   ↓
Prediction
   ↓
Readiness
   ↓
Roadmap
Returning User
Login
   ↓
Existing User Data
   ↓
Dashboard
   ↓
Continue From Previous State

A user's profile, predictions and roadmap are associated with their authenticated identity.

This prevents different users from seeing the same profile or prediction data.

🔐 Authentication

MATRIX uses JWT-based authentication.

Features include:

User registration
User login
Password hashing
JWT access tokens
Protected API routes
Current-user verification
User-specific database access

User data follows:

User
 │
 ├── Profile
 │
 ├── Predictions
 │
 └── Roadmap
🏗️ System Architecture
┌───────────────────────────────────────────────────────┐
│                     FRONTEND                          │
│                  React + Vite                         │
│                                                       │
│ Login → Dashboard → Profile → Prediction → Roadmap   │
└───────────────────────┬───────────────────────────────┘
                        │
                     REST API
                        │
                        ▼
┌───────────────────────────────────────────────────────┐
│                     BACKEND                           │
│                     FastAPI                           │
│                                                       │
│ Authentication                                        │
│ Profile Management                                    │
│ Prediction API                                        │
│ Roadmap API                                           │
└───────────────┬───────────────────────┬───────────────┘
                │                       │
                ▼                       ▼
        ┌───────────────┐       ┌─────────────────┐
        │   MongoDB     │       │    ML SYSTEM    │
        │               │       │                 │
        │ Users         │       │ Career Model    │
        │ Profiles      │       │ Placement Model │
        │ Predictions   │       │ Readiness       │
        │ Roadmaps      │       │                 │
        └───────────────┘       └─────────────────┘
🤖 Machine Learning Architecture
Career Prediction
Profile Features
       │
       ▼
┌──────────────────┐
│ Sector Predictor  │
└────────┬─────────┘
         │
         ▼
 Predicted Sector
         │
         ▼
┌──────────────────┐
│  Role Predictor   │
└────────┬─────────┘
         │
         ▼
 Predicted Career Role

The runtime inference layer is separated from training code.

backend/app/ml/

├── inference/
│   ├── hierarchical_predictor_v2.py
│   ├── readiness_scorer.py
│   └── service_v2.py
│
└── training/
    ├── so_preprocess_hierarchical_v2.py
    └── train_placement.py
🔬 ML Pipeline
Dataset
   ↓
Data Processing
   ↓
Feature Engineering
   ↓
Preprocessing
   ↓
Model Training
   ↓
Evaluation
   ↓
Saved Model Artifacts
   ↓
Inference Service
   ↓
FastAPI
   ↓
Frontend

Training and inference are intentionally separated so that the production application does not need to retrain models.

📊 Explainability

MATRIX also includes SHAP-based explainability support.

The purpose is to make predictions more interpretable by showing the contribution/importance of model features instead of treating the prediction as a completely black-box result.

📁 Project Structure
MATRIX/
│
├── .github/
│   └── workflows/
│       ├── python-ci.yml
│       └── node-ci.yml
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── prediction.py
│   │   │           ├── profile.py
│   │   │           └── roadmap.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   │
│   │   ├── ml/
│   │   │   ├── inference/
│   │   │   └── training/
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/
│   │   │   └── roadmap_generator.py
│   │   │
│   │   └── main.py
│   │
│   ├── data/
│   ├── ml/
│   │   ├── model_card/
│   │   ├── plots_sector_v2/
│   │   ├── saved_models/
│   │   ├── saved_models_roles_v2/
│   │   └── saved_models_sector_v2/
│   │
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── dashboard/
│   │   │   └── layout/
│   │   │
│   │   ├── lib/
│   │   ├── pages/
│   │   └── routes/
│   │
│   └── package.json
│
├── download_so.py
├── PROJECT_CHECKLIST.md
├── LICENSE
├── README.md
└── .gitignore
🛠️ Technology Stack
Frontend
React
Vite
React Router
Tailwind CSS
Motion
Backend
Python
FastAPI
Uvicorn
Pydantic
Motor
PyMongo
JWT
Passlib
bcrypt
Machine Learning
Scikit-learn
XGBoost
Pandas
NumPy
SHAP
Joblib
Database
MongoDB Atlas
Development
Git
GitHub
GitHub Actions
⚙️ Installation
Prerequisites

Install:

Python 3.10+
Node.js
npm
MongoDB Atlas account
1. Clone Repository
git clone https://github.com/Sujaykr99/4th_year_major_project.git

cd 4th_year_major_project
2. Backend Setup

Create a virtual environment:

Windows
python -m venv .venv

.venv\Scripts\activate
Linux / macOS
python -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r backend/requirements.txt
3. Environment Variables

Create:

backend/.env

Use:

backend/.env.example

as the template.

Configure:

MongoDB Atlas connection
JWT secret
Application configuration

Never commit your real .env file.

4. Run Backend
cd backend

python -m uvicorn app.main:app --reload

Backend runs at:

http://127.0.0.1:8000
5. Run Frontend

Open another terminal:

cd frontend

npm install

npm run dev

Open the URL provided by Vite.

🔌 API Structure

MATRIX uses versioned REST APIs:

/api/v1/
│
├── auth
├── profile
├── prediction
└── roadmap
Authentication
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
Profile

Profile APIs manage the authenticated user's career and academic information.

Prediction

Prediction APIs handle:

Career prediction
Placement prediction
Readiness score
Skill gaps
Prediction history
Roadmap

Roadmap APIs handle:

Roadmap generation
Target role
Learning steps
Resources
Progress status
🧪 Development & Validation

Backend syntax check:

python -m compileall app

Frontend production build:

npm run build

Frontend lint:

npm run lint

The repository also contains GitHub Actions workflows for automated Python and Node checks.

🔒 Security

MATRIX follows basic application security practices:

Password hashing
JWT authentication
Protected routes
Environment-based secrets
MongoDB authentication
.env excluded from Git
User-specific data access

Never commit:

.env
API keys
MongoDB credentials
JWT secrets
private tokens
🎓 Academic Project

MATRIX was developed as a 4th-year major project to demonstrate the integration of:

Full-stack development
Machine learning
Feature engineering
Career recommendation
Classification
Explainable AI
User profiling
Placement readiness analysis
Personalized recommendation
REST API architecture
Database integration

The project combines machine learning with a complete production-style web application rather than keeping the ML system isolated inside notebooks.

🚧 Future Improvements

Possible future improvements include:

More career sectors and roles
Resume parsing
GitHub profile integration
LinkedIn profile integration
Adaptive roadmap generation
Continuous model retraining
Model monitoring
Better prediction calibration
Advanced explainability
Real-time learning progress
Cloud deployment
Scalable ML inference
👨‍💻 Author

Sujay Kumar

B.Tech — Computer Science Engineering
Artificial Intelligence & Machine Learning

📄 License

This project is licensed under the MIT License.

See LICENSE for details.

⭐ MATRIX

Understand where you are.
Discover where you fit.
Know what to improve.
Build where you want to go