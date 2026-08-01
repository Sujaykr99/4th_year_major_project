"""Roadmap endpoints."""
from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.models.schemas import (
    Roadmap,
    RoadmapGenerateRequest,
    RoadmapItem,
)
from app.core import security

router = APIRouter()


@router.post("/generate", response_model=Roadmap)
async def generate_roadmap(
    request: RoadmapGenerateRequest,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Generate a personalized learning roadmap for a target role.
    """
    # In a real implementation, this would use a more sophisticated algorithm
    # For now, we'll create a basic roadmap based on the target role

    # Define roadmap templates for different roles
    roadmap_templates = {
        "Software Engineer": [
            {"category": "course", "title": "Data Structures and Algorithms", "description": "Learn fundamental data structures and algorithms", "duration_weeks": 4, "priority": "high"},
            {"category": "project", "title": "Build a Personal Portfolio Website", "description": "Create a responsive portfolio showcasing your projects", "duration_weeks": 3, "priority": "high"},
            {"category": "certification", "title": "AWS Certified Developer", "description": "Validate your AWS development skills", "duration_weeks": 8, "priority": "medium"},
        ],
        "Data Scientist": [
            {"category": "course", "title": "Statistics for Data Science", "description": "Learn statistical methods for data analysis", "duration_weeks": 4, "priority": "high"},
            {"category": "project", "title": "Exploratory Data Analysis Project", "description": "Analyze a real-world dataset and derive insights", "duration_weeks": 3, "priority": "high"},
            {"category": "certification", "title": "Google Data Analytics Professional Certificate", "description": "Gain foundational data analytics skills", "duration_weeks": 12, "priority": "medium"},
        ],
        "Web Developer": [
            {"category": "course", "title": "Full Stack Web Development", "description": "Learn modern frontend and backend technologies", "duration_weeks": 6, "priority": "high"},
            {"category": "project", "title": "E-commerce Website", "description": "Build a full-stack e-commerce application", "duration_weeks": 4, "priority": "high"},
            {"category": "certification", "title": "Meta Front-End Developer Certificate", "description": "Develop skills in React and modern frontend development", "duration_weeks": 8, "priority": "medium"},
        ],
    }

    # Get template for target role or use a default one
    template = roadmap_templates.get(request.target_role, [
        {"category": "course", "title": f"Introduction to {request.target_role}", "description": f"Learn the basics of {request.target_role}", "duration_weeks": 4, "priority": "high"},
        {"category": "project", "title": f"{request.target_role} Capstone Project", "description": f"Apply your skills in a real-world {request.target_role} project", "duration_weeks": 4, "priority": "high"},
        {"category": "certification", "title": f"Certified {request.target_role}", "description": f"Get certified as a {request.target_role}", "duration_weeks": 6, "priority": "medium"},
    ])

    # Create roadmap items
    items = []
    total_duration = 0

    for i, item_template in enumerate(template):
        item = RoadmapItem(
            step=i + 1,
            category=item_template["category"],
            title=item_template["title"],
            description=item_template["description"],
            duration_weeks=item_template["duration_weeks"],
            priority=item_template["priority"],
            resources=[],  # In a real app, this would be populated with actual resources
            status="pending",
            target_role=request.target_role,
        )
        items.append(item)
        total_duration += item_template["duration_weeks"]

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