"""Profile endpoints."""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.schemas import (
    ProfileResponse,
    ProfileUpdate,
    StudentProfile,
    UserResponse,
)
from app.core import security

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get current user's profile.
    """
    profile_dict = await db.profiles.find_one({"user_id": current_user_id})
    if not profile_dict:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile_dict["id"] = str(profile_dict["_id"])
    profile_dict["user_id"] = str(profile_dict["user_id"])
    return ProfileResponse(**profile_dict)


@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    profile_in: ProfileUpdate,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Update current user's profile.
    """
    # Get existing profile
    existing_profile = await db.profiles.find_one({"user_id": current_user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Prepare update data
    update_data = profile_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Update profile
    await db.profiles.update_one(
        {"user_id": current_user_id}, {"$set": update_data}
    )

    # Get updated profile
    updated_profile = await db.profiles.find_one({"user_id": current_user_id})
    updated_profile["id"] = str(updated_profile["_id"])
    updated_profile["user_id"] = str(updated_profile["user_id"])
    return ProfileResponse(**updated_profile)


@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile_in: StudentProfile,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Create a new profile for the current user.
    """
    # Check if profile already exists
    existing_profile = await db.profiles.find_one({"user_id": current_user_id})
    if existing_profile:
        raise HTTPException(
            status_code=400, detail="Profile already exists for this user"
        )

    # Create profile
    profile_dict = profile_in.model_dump()
    profile_dict["user_id"] = current_user_id
    profile_dict["created_at"] = datetime.utcnow()
    profile_dict["updated_at"] = datetime.utcnow()

    result = await db.profiles.insert_one(profile_dict)
    profile_dict["id"] = str(result.inserted_id)
    profile_dict["user_id"] = str(profile_dict["user_id"])

    return ProfileResponse(**profile_dict)