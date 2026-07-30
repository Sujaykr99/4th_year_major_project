"""Profile API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List

from app.core.config import settings
from app.core.security import get_current_user_id
from app.core.database import get_database
from app.models.schemas import (
    StudentProfile, ProfileUpdate, ProfileResponse,
    Skill, Project, Certification, Education, Experience
)


router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/profile", tags=["Profile"])


async def calculate_profile_completion(profile: StudentProfile) -> float:
    """Calculate profile completion percentage."""
    total_fields = 0
    filled_fields = 0

    fields = [
        ("current_education", profile.current_education),
        ("cgpa", profile.cgpa),
        ("university", profile.university),
        ("graduation_year", profile.graduation_year),
        ("skills", profile.skills),
        ("projects", profile.projects),
        ("certifications", profile.certifications),
        ("experiences", profile.experiences),
        ("internships", profile.internships),
        ("preferred_roles", profile.preferred_roles),
        ("preferred_locations", profile.preferred_locations),
    ]

    for _, value in fields:
        total_fields += 1
        if value:
            if isinstance(value, list) and len(value) > 0:
                filled_fields += 1
            elif not isinstance(value, list):
                filled_fields += 1

    return round((filled_fields / total_fields) * 100, 1) if total_fields > 0 else 0


@router.get("", response_model=ProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get user's profile."""
    profile = await db.profiles.find_one({"user_id": user_id})
    if not profile:
        # Return empty profile structure
        return ProfileResponse(
            id="",
            user_id=user_id,
            created_at=datetime.utcnow(),
            profile_completion=0.0,
            skills=[],
            projects=[],
            certifications=[],
            experiences=[],
            internships=[],
            preferred_roles=[],
            preferred_locations=[],
            remote_preference=True
        )

    profile["id"] = str(profile["_id"])
    profile["user_id"] = str(profile["user_id"])
    return ProfileResponse(**profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create or update user's profile."""
    # Calculate completion
    profile_dict = profile_data.model_dump(exclude_unset=True)
    temp_profile = StudentProfile(**profile_dict)
    completion = await calculate_profile_completion(temp_profile)

    # Update or create
    update_doc = {
        **profile_dict,
        "user_id": user_id,
        "profile_completion": completion,
        "updated_at": datetime.utcnow()
    }

    result = await db.profiles.update_one(
        {"user_id": user_id},
        {"$set": update_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True
    )

    # Fetch updated profile
    profile = await db.profiles.find_one({"user_id": user_id})
    profile["id"] = str(profile["_id"])
    profile["user_id"] = str(profile["user_id"])
    return ProfileResponse(**profile)


@router.post("/skills", response_model=Skill)
async def add_skill(
    skill: Skill,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a skill to profile."""
    skill_doc = skill.model_dump()
    skill_doc["user_id"] = user_id
    skill_doc["created_at"] = datetime.utcnow()

    await db.skills.update_one(
        {"user_id": user_id, "skill_name": skill.name},
        {"$set": skill_doc},
        upsert=True
    )

    # Update profile skills array
    profile = await db.profiles.find_one({"user_id": user_id})
    if profile:
        skills = profile.get("skills", [])
        skill_names = [s["name"] for s in skills]
        if skill.name not in skill_names:
            skills.append(skill.model_dump())
            await db.profiles.update_one(
                {"user_id": user_id},
                {"$set": {"skills": skills, "updated_at": datetime.utcnow()}}
            )

    return skill


@router.delete("/skills/{skill_name}")
async def remove_skill(
    skill_name: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove a skill from profile."""
    await db.skills.delete_one({"user_id": user_id, "skill_name": skill_name})

    # Update profile
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$pull": {"skills": {"name": skill_name}}, "$set": {"updated_at": datetime.utcnow()}}
    )

    return {"message": "Skill removed"}


@router.post("/projects", response_model=Project)
async def add_project(
    project: Project,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a project to profile."""
    project_doc = project.model_dump()
    project_doc["user_id"] = user_id
    project_doc["created_at"] = datetime.utcnow()

    result = await db.projects.insert_one(project_doc)

    # Update profile
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$push": {"projects": project.model_dump()}, "$set": {"updated_at": datetime.utcnow()}},
        upsert=True
    )

    project_doc["id"] = str(result.inserted_id)
    return Project(**project_doc)


@router.delete("/projects/{project_id}")
async def remove_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove a project from profile."""
    await db.projects.delete_one({"_id": ObjectId(project_id), "user_id": user_id})
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$pull": {"projects": {"id": project_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return {"message": "Project removed"}


@router.post("/certifications", response_model=Certification)
async def add_certification(
    cert: Certification,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a certification to profile."""
    cert_doc = cert.model_dump()
    cert_doc["user_id"] = user_id
    cert_doc["created_at"] = datetime.utcnow()

    result = await db.certifications.insert_one(cert_doc)

    await db.profiles.update_one(
        {"user_id": user_id},
        {"$push": {"certifications": cert.model_dump()}, "$set": {"updated_at": datetime.utcnow()}},
        upsert=True
    )

    cert_doc["id"] = str(result.inserted_id)
    return Certification(**cert_doc)


@router.delete("/certifications/{cert_id}")
async def remove_certification(
    cert_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove a certification from profile."""
    await db.certifications.delete_one({"_id": ObjectId(cert_id), "user_id": user_id})
    await db.profiles.update_one(
        {"user_id": user_id},
        {"$pull": {"certifications": {"id": cert_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return {"message": "Certification removed"}