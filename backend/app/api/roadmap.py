"""Roadmap API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List

from app.core.config import settings
from app.core.security import get_current_user_id
from app.core.database import get_database
from app.services.roadmap_generator import (
    generate_roadmap, get_roadmap_summary, identify_skill_gaps
)
from app.models.schemas import (
    RoadmapGenerateRequest, Roadmap, RoadmapItem
)


router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/roadmap", tags=["Roadmap"])


@router.post("/generate", response_model=Roadmap)
async def generate_personalized_roadmap(
    request: RoadmapGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Generate personalized learning roadmap for target role."""
    # Get user's current profile for skills
    profile = await db.profiles.find_one({"user_id": user_id})
    current_skills = []
    if profile and "skills" in profile:
        current_skills = [s["name"] for s in profile.get("skills", [])]

    # Generate roadmap
    roadmap_data = generate_roadmap(
        target_role=request.target_role,
        current_skills=current_skills,
        time_commitment_hours_per_week=request.time_commitment_hours_per_week,
        focus_areas=request.focus_areas
    )

    # Save to database
    roadmap_doc = {
        "user_id": user_id,
        **roadmap_data,
        "created_at": roadmap_data["created_at"],
        "updated_at": roadmap_data["created_at"]
    }
    result = await db.roadmaps.insert_one(roadmap_doc)
    roadmap_data["id"] = str(result.inserted_id)

    return Roadmap(**roadmap_data)


@router.get("", response_model=List[Roadmap])
async def get_user_roadmaps(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all roadmaps for current user."""
    cursor = db.roadmaps.find({"user_id": user_id}).sort("created_at", -1)
    roadmaps = await cursor.to_list(length=50)

    for r in roadmaps:
        r["id"] = str(r["_id"])
        r["user_id"] = str(r["user_id"])

    return [Roadmap(**r) for r in roadmaps]


@router.get("/{roadmap_id}", response_model=Roadmap)
async def get_roadmap(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific roadmap by ID."""
    roadmap = await db.roadmaps.find_one({"_id": ObjectId(roadmap_id), "user_id": user_id})
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    roadmap["id"] = str(roadmap["_id"])
    roadmap["user_id"] = str(roadmap["user_id"])
    return Roadmap(**roadmap)


@router.put("/{roadmap_id}/items/{item_step}")
async def update_roadmap_item_status(
    roadmap_id: str,
    item_step: int,
    status: str,  # pending, in_progress, completed
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update roadmap item status."""
    valid_statuses = ["pending", "in_progress", "completed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = await db.roadmaps.update_one(
        {"_id": ObjectId(roadmap_id), "user_id": user_id, "items.step": item_step},
        {"$set": {"items.$.status": status, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Roadmap or item not found")

    return {"message": "Status updated"}


@router.get("/{roadmap_id}/summary")
async def get_roadmap_summary_endpoint(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get human-readable roadmap summary."""
    roadmap = await db.roadmaps.find_one({"_id": ObjectId(roadmap_id), "user_id": user_id})
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    return {"summary": get_roadmap_summary(roadmap)}


@router.post("/skill-gaps")
async def analyze_skill_gaps(
    target_role: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Analyze skill gaps for a target role."""
    profile = await db.profiles.find_one({"user_id": user_id})
    current_skills = []
    if profile and "skills" in profile:
        current_skills = [s["name"] for s in profile.get("skills", [])]

    gaps = identify_skill_gaps(current_skills, target_role)
    return {"target_role": target_role, "gaps": gaps}


# Import datetime for update timestamp
from datetime import datetime