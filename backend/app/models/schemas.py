"""Pydantic models for data validation and serialization."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

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

    # Preferences
    preferred_role: Optional[str] = None


class CareerPrediction(BaseModel):
    role: str
    probability: float
    confidence_level: str  # high, medium, low


class PredictionResult(BaseModel):
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