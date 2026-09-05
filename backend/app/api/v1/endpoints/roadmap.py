"""Roadmap endpoints."""
from typing import Any, List, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.models.schemas import (
    Roadmap,
    RoadmapGenerateRequest,
    RoadmapItem,
    PredictionResult,
)
from app.core import security
from app.services.roadmap_generator import generate_roadmap, identify_skill_gaps

router = APIRouter()


@router.post("/generate", response_model=Roadmap)
async def generate_roadmap_endpoint(
    request: RoadmapGenerateRequest,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Generate a personalized learning roadmap for a target role.
    """
    # Call the actual roadmap generator service
    from app.services.roadmap_generator import generate_roadmap as generate_roadmap_service

    # We use a default list of current skills for now, until the profile endpoint connects it
    current_skills = ["Python", "HTML", "CSS"]

    generated_data = generate_roadmap_service(
        target_role=request.target_role,
        current_skills=current_skills,
        time_commitment_hours_per_week=10,
        focus_areas=["courses", "projects", "certifications"]
    )

    # Create roadmap items
    items = []
    total_duration = generated_data["total_duration_weeks"]

    for i, item_data in enumerate(generated_data["items"]):
        item = RoadmapItem(
            step=i + 1,
            category=item_data["category"],
            title=item_data["title"],
            description=item_data["description"],
            duration_weeks=item_data["duration_weeks"],
            priority=item_data["priority"],
            resources=item_data["resources"],  # Includes YouTube URLs
            status="pending",
            target_role=request.target_role,
        )
        items.append(item)

    # Create roadmap object
    roadmap = Roadmap(
        user_id=current_user_id,
        target_role=request.target_role,
        items=items,
        total_duration_weeks=total_duration,
    )

    # Save to database
    result = await db.roadmaps.insert_one(roadmap.model_dump(by_alias=True))
    roadmap.id = str(result.inserted_id)

    return roadmap


@router.post("/generate-auto", response_model=Roadmap)
async def generate_roadmap_auto(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Generate a personalized learning roadmap based on the user's latest prediction.
    Fetches the user's latest prediction and profile, then creates a roadmap.
    """
    # Get the user's latest prediction
    pred = await db.predictions.find_one(
        {"user_id": current_user_id},
        sort=[("created_at", -1)]
    )

    if not pred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prediction found. Run a prediction first."
        )

    predicted_role = pred.get("role", pred.get("predicted_role", "Unknown"))
    skill_gaps = pred.get("skill_gaps", {})

    # Get user's profile for current skills
    profile = await db.profiles.find_one({"user_id": current_user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Complete your profile first."
        )

    pred_profile = profile.get("prediction_profile", {})
    current_skills = []
    current_skills.extend(pred_profile.get("programming_skills", []))
    current_skills.extend(pred_profile.get("framework_skills", []))
    current_skills.extend(pred_profile.get("tool_skills", []))
    current_skills.extend(pred_profile.get("soft_skills", []))

    # Check if a roadmap already exists for this prediction (avoid duplicates)
    existing_roadmap = await db.roadmaps.find_one({
        "user_id": current_user_id,
        "target_role": predicted_role
    }, sort=[("created_at", -1)])

    if existing_roadmap:
        existing_roadmap["id"] = str(existing_roadmap["_id"])
        return Roadmap(**existing_roadmap)

    # Generate roadmap using skill gaps from prediction
    missing_required = skill_gaps.get("missing_required", [])
    missing_nice = skill_gaps.get("missing_nice_to_have", [])

    # Use identify_skill_gaps to get structured gaps (but we already have them from prediction)
    # Generate roadmap with the current skills
    generated_data = generate_roadmap(
        target_role=predicted_role,
        current_skills=current_skills,
        time_commitment_hours_per_week=10,
        focus_areas=["courses", "projects", "certifications"]
    )

    # Create roadmap items
    items = []
    total_duration = generated_data["total_duration_weeks"]

    for i, item_data in enumerate(generated_data["items"]):
        item = RoadmapItem(
            step=i + 1,
            category=item_data["category"],
            title=item_data["title"],
            description=item_data["description"],
            duration_weeks=item_data["duration_weeks"],
            priority=item_data["priority"],
            resources=item_data["resources"],  # Includes YouTube URLs
            status="pending",
            target_role=predicted_role,
        )
        items.append(item)

    # Create roadmap object
    roadmap = Roadmap(
        user_id=current_user_id,
        target_role=predicted_role,
        items=items,
        total_duration_weeks=total_duration,
    )

    # Save to database
    result = await db.roadmaps.insert_one(roadmap.model_dump(by_alias=True))
    roadmap.id = str(result.inserted_id)

    return roadmap


@router.get("/latest", response_model=Roadmap)
async def get_latest_roadmap(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get the latest roadmap for the current user.
    Returns the most recent roadmap or 404 if none exists.
    """
    roadmap_doc = await db.roadmaps.find_one(
        {"user_id": current_user_id},
        sort=[("created_at", -1)]
    )

    if not roadmap_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roadmap found. Generate a roadmap first."
        )

    roadmap_doc["id"] = str(roadmap_doc["_id"])
    return Roadmap(**roadmap_doc)


@router.get("/me", response_model=List[Roadmap])
async def get_my_roadmaps(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get all roadmaps for the current user.
    """
    cursor = db.roadmaps.find({"user_id": current_user_id})
    roadmaps = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        roadmaps.append(Roadmap(**doc))
    return roadmaps


@router.get("/{roadmap_id}", response_model=Roadmap)
async def get_roadmap(
    roadmap_id: str,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get a specific roadmap by ID.
    """
    from bson import ObjectId

    if not ObjectId.is_valid(roadmap_id):
        raise HTTPException(status_code=400, detail="Invalid roadmap ID")

    roadmap_doc = await db.roadmaps.find_one({
        "_id": ObjectId(roadmap_id),
        "user_id": current_user_id
    })

    if not roadmap_doc:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    roadmap_doc["id"] = str(roadmap_doc["_id"])
    return Roadmap(**roadmap_doc)


@router.put("/{roadmap_id}/items/{item_id}", response_model=Roadmap)
async def update_roadmap_item(
    roadmap_id: str,
    item_id: int,
    status: str,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Update the status of a roadmap item.
    """
    from bson import ObjectId

    if not ObjectId.is_valid(roadmap_id):
        raise HTTPException(status_code=400, detail="Invalid roadmap ID")

    # Validate status
    if status not in ["pending", "in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    # Update the specific item in the roadmap
    result = await db.roadmaps.update_one(
        {
            "_id": ObjectId(roadmap_id),
            "user_id": current_user_id,
            "items.step": item_id
        },
        {
            "$set": {
                "items.$.status": status,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Roadmap or item not found")

    # Return updated roadmap
    roadmap_doc = await db.roadmaps.find_one({
        "_id": ObjectId(roadmap_id),
        "user_id": current_user_id
    })

    roadmap_doc["id"] = str(roadmap_doc["_id"])
    return Roadmap(**roadmap_doc)