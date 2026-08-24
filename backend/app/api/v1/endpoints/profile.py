"""Profile endpoints."""
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.schemas import (
    ProfileResponse,
    ProfileUpdate,
    StudentProfile,
    UserResponse,
    calculate_profile_completion,
)
from app.core import security

router = APIRouter()


def _save_profile_with_completion(
    profile_dict: dict, current_user_id: str, db: AsyncIOMotorDatabase, is_new: bool = False
) -> dict:
    """Helper to calculate completion and save profile."""
    # Calculate profile completion from prediction_profile
    prediction_profile = profile_dict.get("prediction_profile", {})
    completion = calculate_profile_completion(prediction_profile)
    profile_dict["profile_completion"] = completion
    profile_dict["updated_at"] = datetime.utcnow()

    if is_new:
        profile_dict["user_id"] = current_user_id
        profile_dict["created_at"] = datetime.utcnow()
        result = db.profiles.insert_one(profile_dict)
        profile_dict["id"] = str(result.inserted_id)
    else:
        db.profiles.update_one(
            {"user_id": current_user_id}, {"$set": profile_dict}
        )
        profile_dict["id"] = str(profile_dict["_id"])

    profile_dict["user_id"] = str(profile_dict["user_id"])
    return profile_dict


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

    # Merge with existing profile data
    merged_profile = {**existing_profile, **update_data}

    # Calculate completion and save
    saved_profile = _save_profile_with_completion(merged_profile, current_user_id, db)

    return ProfileResponse(**saved_profile)


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

    # Calculate completion and save
    saved_profile = _save_profile_with_completion(profile_dict, current_user_id, db, is_new=True)

    return ProfileResponse(**saved_profile)


@router.get("/prediction", response_model=ProfileResponse)
async def get_prediction_profile(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get current user's profile formatted for prediction.
    Returns the prediction_profile dict with all fields needed for ML prediction.
    """
    profile_dict = await db.profiles.find_one({"user_id": current_user_id})
    if not profile_dict:
        raise HTTPException(status_code=404, detail="Profile not found. Please create a profile first.")

    prediction_profile = profile_dict.get("prediction_profile", {})
    if not prediction_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile incomplete. Please fill in required fields in your profile before running prediction."
        )

    profile_dict["id"] = str(profile_dict["_id"])
    profile_dict["user_id"] = str(profile_dict["user_id"])
    return ProfileResponse(**profile_dict)
