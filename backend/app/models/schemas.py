"""Pydantic models for data validation and serialization."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(
            cls.validate
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v

        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")

        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}



    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# --- Profile Models ---

class Skill(BaseModel):
    name: str
    proficiency: int = Field(..., ge=1, le=10)  # 1-10 scale
    category: Optional[str] = None  # programming, framework, tool, soft_skill


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = []
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    role: Optional[str] = None  # solo, lead, contributor
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Certification(BaseModel):
    name: str
    issuer: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class Education(BaseModel):
    degree: str
    institution: str
    field_of_study: str
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    start_date: datetime
    end_date: Optional[datetime] = None
    achievements: List[str] = []


class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_current: bool = False
    skills_used: List[str] = []


# Required fields for profile completion (core fields needed for prediction)
REQUIRED_PROFILE_FIELDS = [
    "cgpa",
    "university_tier",
    "graduation_year",
    "programming_skills",
    "framework_skills",
    "tool_skills",
    "soft_skills",
    "num_projects",
    "num_internships",
    "hackathon_participation",
    "certifications_count",
]

# Optional fields that enhance prediction but aren't required
OPTIONAL_PROFILE_FIELDS = [
    "age",
    "gender",
    "branch",
    "college_tier",
    "coding_skill_score",
    "aptitude_score",
    "communication_skill_score",
    "logical_reasoning_score",
    "github_repos",
    "linkedin_connections",
    "mock_interview_score",
    "attendance_percentage",
    "backlogs",
    "extracurricular_score",
    "leadership_score",
    "volunteer_experience",
    "sleep_hours",
    "study_hours_per_day",
    "years_code_pro",
    "years_code",
    "ed_level",
    "work_exp_count",
    "is_developer",
    "remote_pref",
]


def calculate_profile_completion(profile_dict: Dict[str, Any]) -> float:
    """Calculate profile completion percentage based on required fields only.
    Optional fields do not count toward completion.
    """
    if not profile_dict:
        return 0.0

    filled = 0
    for field in REQUIRED_PROFILE_FIELDS:
        value = profile_dict.get(field)
        if value is not None:
            if isinstance(value, list) and len(value) > 0:
                filled += 1
            elif isinstance(value, (int, float)) and value != 0:
                filled += 1
            elif isinstance(value, str) and value.strip():
                filled += 1
            elif isinstance(value, bool):
                filled += 1
            else:
                filled += 1

    return round((filled / len(REQUIRED_PROFILE_FIELDS)) * 100, 1)


class StudentProfile(BaseModel):
    # Academic
    current_education: Optional[Education] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    university: Optional[str] = None
    graduation_year: Optional[int] = None

    # Skills & Projects
    skills: List[Skill] = []
    projects: List[Project] = []
    certifications: List[Certification] = []

    # Experience
    experiences: List[Experience] = []
    internships: List[Experience] = []

    # Preferences
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    remote_preference: bool = True
    salary_expectation: Optional[str] = None

    # Raw prediction-form fields are persisted as part of the authenticated
    # user's profile. Ownership is always assigned by the backend route.
    prediction_profile: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    profile_completion: float = 0.0
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProfileUpdate(BaseModel):
    current_education: Optional[Education] = None
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    skills: Optional[List[Skill]] = None
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
    experiences: Optional[List[Experience]] = None
    internships: Optional[List[Experience]] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[bool] = None
    salary_expectation: Optional[str] = None
    prediction_profile: Optional[Dict[str, Any]] = None


class ProfileResponse(StudentProfile):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Prediction Models ---

class PredictionInput(BaseModel):
    # Academic features
    cgpa: float = Field(..., ge=0, le=10)
    university_tier: int = Field(..., ge=1, le=3)  # 1=top, 2=mid, 3=other
    graduation_year: int

    # Skill features
    programming_skills: List[str] = []
    framework_skills: List[str] = []
    tool_skills: List[str] = []
    soft_skills: List[str] = []

    # Experience features
    num_projects: int = Field(..., ge=0)
    num_internships: int = Field(..., ge=0)
    has_research: bool = False
    has_publications: bool = False
    hackathon_participation: int = Field(..., ge=0)
    certifications_count: int = Field(..., ge=0)

    # Placement-specific features (optional, defaults provided)
    age: Optional[int] = Field(None, ge=18, le=35)
    gender: Optional[str] = None  # Male, Female, Other
    branch: Optional[str] = None  # Computer Science, IT, ECE, etc.
    college_tier: Optional[int] = Field(None, ge=1, le=3)
    coding_skill_score: Optional[int] = Field(None, ge=0, le=100)
    aptitude_score: Optional[int] = Field(None, ge=0, le=100)
    communication_skill_score: Optional[int] = Field(None, ge=0, le=100)
    logical_reasoning_score: Optional[int] = Field(None, ge=0, le=100)
    github_repos: Optional[int] = Field(None, ge=0)
    linkedin_connections: Optional[int] = Field(None, ge=0)
    mock_interview_score: Optional[int] = Field(None, ge=0, le=100)
    attendance_percentage: Optional[int] = Field(None, ge=0, le=100)
    backlogs: Optional[int] = Field(None, ge=0)
    extracurricular_score: Optional[int] = Field(None, ge=0, le=100)
    leadership_score: Optional[int] = Field(None, ge=0, le=100)
    volunteer_experience: Optional[str] = None  # Yes, No
    sleep_hours: Optional[int] = Field(None, ge=0, le=12)
    study_hours_per_day: Optional[int] = Field(None, ge=0, le=16)

    # Career model features (optional)
    years_code_pro: Optional[float] = Field(None, ge=0)
    years_code: Optional[float] = Field(None, ge=0)
    ed_level: Optional[int] = Field(None, ge=0, le=5)
    work_exp_count: Optional[int] = Field(None, ge=0, le=5)
    is_developer: Optional[int] = Field(None, ge=0, le=1)
    remote_pref: Optional[int] = Field(None, ge=0, le=2)  # 0=onsite, 1=hybrid, 2=remote

    # Preferences
    preferred_role: Optional[str] = None


class CareerPrediction(BaseModel):
    role: str
    probability: float
    confidence_level: str  # high, medium, low


class PredictionResult(BaseModel):
    id: Optional[str] = None
    predicted_role: str
    confidence: float
    confidence_level: str
    top_predictions: List[CareerPrediction]
    placement_readiness_score: float
    skill_gaps: Dict[str, List[str]]  # role -> missing skills
    shap_explanation: Optional[Dict[str, float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PredictionInDB(PredictionResult):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    input_data: PredictionInput

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PredictionHistory(BaseModel):
    id: str
    predicted_role: str
    confidence: float
    placement_readiness_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# --- Roadmap Models ---

class RoadmapItem(BaseModel):
    step: int
    category: str  # course, project, certification, skill
    title: str
    description: str
    duration_weeks: int
    priority: str  # high, medium, low
    resources: List[str] = []  # URLs
    status: str = "pending"  # pending, in_progress, completed
    target_role: str


class Roadmap(BaseModel):
    id: Optional[str] = None
    user_id: str
    target_role: str
    items: List[RoadmapItem]
    total_duration_weeks: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class RoadmapGenerateRequest(BaseModel):
    target_role: str
    current_skills: List[str] = []
    time_commitment_hours_per_week: int = Field(default=10, ge=1, le=40)
    focus_areas: List[str] = []  # courses, projects, certifications


# --- SHAP Models ---

class SHAPExplanation(BaseModel):
    feature_names: List[str]
    shap_values: List[float]
    base_value: float
    prediction: str
    feature_importance: Dict[str, float]  # sorted by importance
