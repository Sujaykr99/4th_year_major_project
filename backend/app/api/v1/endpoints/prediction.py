"""Prediction endpoints - Hierarchical Career + Placement Prediction."""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.ml.inference.service_v2 import unified_ml_service
from app.models.schemas import (
    PredictionHistory,
    PredictionInDB,
    PredictionInput,
    PredictionResult,
    ProfileResponse,
)
from app.core import security

router = APIRouter()


@router.on_event("startup")
async def load_ml_models():
    """Load ML models on startup."""
    success = unified_ml_service.load_all()
    if not success:
        print("WARNING: Some ML models failed to load")


async def _check_profile_completion(current_user_id: str, db: AsyncIOMotorDatabase) -> ProfileResponse:
    """Check if user has a complete profile for prediction."""
    profile_dict = await db.profiles.find_one({"user_id": current_user_id})
    if not profile_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile not found. Please create and complete your profile before running prediction."
        )

    prediction_profile = profile_dict.get("prediction_profile", {})
    if not prediction_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile incomplete. Please fill in required fields in your profile before running prediction."
        )

    # Check if profile has minimum required fields filled
    completion = profile_dict.get("profile_completion", 0)
    if completion < 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile is only {completion}% complete. Please fill in at least CGPA, Skills, Projects, Internships and Graduation Year."
        )

    profile_dict["id"] = str(profile_dict["_id"])
    profile_dict["user_id"] = str(profile_dict["user_id"])
    return ProfileResponse(**profile_dict)


def _profile_to_prediction_input(profile_dict: dict) -> PredictionInput:
    """Convert saved user profile to PredictionInput for ML model."""
    pred_profile = profile_dict.get("prediction_profile", {})

    # Build PredictionInput from saved profile
    # Required fields
    input_data = {
        "cgpa": pred_profile.get("cgpa", 7.0),
        # college_tier from form maps to university_tier in PredictionInput
        "university_tier": pred_profile.get("university_tier") or pred_profile.get("college_tier", 2),
        "graduation_year": pred_profile.get("graduation_year", 2026),
        "programming_skills": pred_profile.get("programming_skills", []),
        "framework_skills": pred_profile.get("framework_skills", []),
        "tool_skills": pred_profile.get("tool_skills", []),
        "soft_skills": pred_profile.get("soft_skills", []),
        "num_projects": pred_profile.get("num_projects", 0),
        "num_internships": pred_profile.get("num_internships", 0),
        "hackathon_participation": pred_profile.get("hackathon_participation", 0),
        "certifications_count": pred_profile.get("certifications_count", 0),
        "has_research": False,
        "has_publications": False,
    }

    # Optional fields with defaults from profile
    optional_fields = [
        "age", "gender", "branch", "college_tier",
        "coding_skill_score", "aptitude_score", "communication_skill_score",
        "logical_reasoning_score", "github_repos", "linkedin_connections",
        "mock_interview_score", "attendance_percentage", "backlogs",
        "extracurricular_score", "leadership_score", "volunteer_experience",
        "sleep_hours", "study_hours_per_day",
        "years_code_pro", "years_code", "ed_level", "work_exp_count",
        "is_developer", "remote_pref", "preferred_role"
    ]

    for field in optional_fields:
        if field in pred_profile and pred_profile[field] is not None:
            input_data[field] = pred_profile[field]

    return PredictionInput(**input_data)


@router.post("/career", response_model=PredictionResult)
async def predict_career(
    input_data: PredictionInput,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Make a hierarchical career prediction (Sector -> Role).
    Returns: sector, role, confidence, placement_readiness_score, skill_gaps
    """
    # Check profile completion before running ML
    await _check_profile_completion(current_user_id, db)

    if not unified_ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not available",
        )

    input_dict = input_data.model_dump()

    # Get hierarchical career prediction
    prediction_result = unified_ml_service.predict_career(input_dict)

    # Save prediction to database
    # Build top_predictions from role_probabilities
    role_probs = prediction_result.get("role_probabilities", {})
    top_predictions = [
        CareerPrediction(role=role, probability=prob, confidence_level="high" if prob > 0.7 else "medium" if prob > 0.4 else "low")
        for role, prob in sorted(role_probs.items(), key=lambda x: x[1], reverse=True)
    ]

    # If no role_probabilities, create a single entry with the predicted role
    if not top_predictions and prediction_result.get("role"):
        top_predictions = [
            CareerPrediction(
                role=prediction_result["role"],
                probability=prediction_result.get("role_confidence", 0.0),
                confidence_level="high" if prediction_result.get("role_confidence", 0) > 0.7 else "medium" if prediction_result.get("role_confidence", 0) > 0.4 else "low"
            )
        ]

    prediction_in_db = PredictionInDB(
        user_id=current_user_id,
        input_data=input_data,
        predicted_role=prediction_result.get("role", "Unknown"),
        confidence=prediction_result.get("role_confidence", 0.0),
        confidence_level="high" if prediction_result.get("role_confidence", 0) > 0.7 else "medium" if prediction_result.get("role_confidence", 0) > 0.4 else "low",
        top_predictions=top_predictions,
        placement_readiness_score=prediction_result.get("placement_readiness_score", 0.0),
        skill_gaps=prediction_result.get("skill_gaps", {}),
        shap_explanation=None,
    )

    result = await db.predictions.insert_one(prediction_in_db.model_dump(by_alias=True))
    prediction_in_db.id = str(result.inserted_id)

    # Return prediction result (adapt hierarchical result to PredictionResult schema)
    return PredictionResult(
        predicted_role=prediction_result.get("role", "Unknown"),
        confidence=prediction_result.get("role_confidence", 0.0),
        confidence_level="high" if prediction_result.get("role_confidence", 0) > 0.7 else "medium" if prediction_result.get("role_confidence", 0) > 0.4 else "low",
        top_predictions=top_predictions,
        placement_readiness_score=prediction_result.get("placement_readiness_score", 0.0),
        skill_gaps=prediction_result.get("skill_gaps", {}),
        shap_explanation=None,  # Not available for hierarchical model yet
    )


@router.post("/placement")
async def predict_placement(
    input_data: PredictionInput,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Make a placement prediction (Placed/Not Placed).
    Returns: predicted_status, placement_probability, confidence, readiness_score, recommendations
    """
    # Check profile completion before running ML
    await _check_profile_completion(current_user_id, db)

    if not unified_ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not available",
        )

    input_dict = input_data.model_dump()

    # Get placement prediction with readiness
    prediction_result = unified_ml_service.predict_placement(input_dict)

    # Save to database (extend schema or use generic collection)
    await db.placement_predictions.insert_one({
        "user_id": current_user_id,
        "input_data": input_dict,
        "predicted_status": prediction_result["predicted_status"],
        "placement_probability": prediction_result["placement_probability"],
        "confidence": prediction_result["confidence"],
        "confidence_level": prediction_result["confidence_level"],
        "probabilities": prediction_result["probabilities"],
        "readiness_score": prediction_result["readiness_score"],
        "readiness_level": prediction_result["readiness_level"],
        "readiness_breakdown": prediction_result["readiness_breakdown"],
        "recommendations": prediction_result["recommendations"],
    })

    return prediction_result


@router.post("/both")
async def predict_both(
    input_data: PredictionInput,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get both career and placement predictions in one call.
    """
    # Check profile completion before running ML
    await _check_profile_completion(current_user_id, db)

    if not unified_ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not available",
        )

    input_dict = input_data.model_dump()
    result = unified_ml_service.predict_both(input_dict)

    # Save career prediction
    career_result = result["career_prediction"]

    # Convert hierarchical model output to match PredictionInDB schema
    # Build top_predictions from role_probabilities
    role_probs = career_result.get("role_probabilities", {})
    top_predictions = [
        CareerPrediction(role=role, probability=prob, confidence_level="high" if prob > 0.7 else "medium" if prob > 0.4 else "low")
        for role, prob in sorted(role_probs.items(), key=lambda x: x[1], reverse=True)
    ]

    # If no role_probabilities, create a single entry with the predicted role
    if not top_predictions and career_result.get("role"):
        top_predictions = [
            CareerPrediction(
                role=career_result["role"],
                probability=career_result.get("role_confidence", 0.0),
                confidence_level="high" if career_result.get("role_confidence", 0) > 0.7 else "medium" if career_result.get("role_confidence", 0) > 0.4 else "low"
            )
        ]

    prediction_in_db = PredictionInDB(
        user_id=current_user_id,
        input_data=input_data,
        predicted_role=career_result.get("role", "Unknown"),
        confidence=career_result.get("role_confidence", 0.0),
        confidence_level="high" if career_result.get("role_confidence", 0) > 0.7 else "medium" if career_result.get("role_confidence", 0) > 0.4 else "low",
        top_predictions=top_predictions,
        placement_readiness_score=career_result.get("placement_readiness_score", 0.0),
        skill_gaps=career_result.get("skill_gaps", {}),
        shap_explanation=None,
    )
    await db.predictions.insert_one(prediction_in_db.model_dump(by_alias=True))

    # Save placement prediction
    placement_result = result["placement_prediction"]
    await db.placement_predictions.insert_one({
        "user_id": current_user_id,
        "input_data": input_dict,
        **placement_result
    })

    return result


@router.get("/model/info")
async def get_model_info() -> Any:
    """Get information about loaded ML models."""
    if not unified_ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not loaded",
        )
    return unified_ml_service.get_model_info()


@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
    limit: int = 10,
    skip: int = 0,
) -> Any:
    """Get career prediction history for the current user."""
    cursor = db.predictions.find({"user_id": current_user_id}).sort(
        "created_at", -1
    ).skip(skip).limit(limit)

    predictions = await cursor.to_list(length=limit)
    history = []
    for pred in predictions:
        history.append(
            PredictionHistory(
                id=str(pred["_id"]),
                predicted_role=pred.get("role", pred.get("predicted_role", "Unknown")),
                confidence=pred.get("role_confidence", pred.get("confidence", 0.0)),
                placement_readiness_score=pred.get("placement_readiness_score", 0.0),
                created_at=pred["created_at"],
            )
        )

    return history


@router.get("/history/placement")
async def get_placement_history(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
    limit: int = 10,
    skip: int = 0,
) -> Any:
    """Get placement prediction history for the current user."""
    cursor = db.placement_predictions.find({"user_id": current_user_id}).sort(
        "created_at", -1
    ).skip(skip).limit(limit)

    predictions = await cursor.to_list(length=limit)
    for pred in predictions:
        pred["_id"] = str(pred["_id"])
    return predictions


@router.post("/career/auto", response_model=PredictionResult)
async def predict_career_auto(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Make a hierarchical career prediction using the user's saved profile.
    Fetches the user's profile from MongoDB and converts it to PredictionInput.
    """
    # Check profile completion and get profile
    profile = await _check_profile_completion(current_user_id, db)

    if not unified_ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not available",
        )

    # Convert profile to PredictionInput
    input_data = _profile_to_prediction_input(profile.model_dump())
    input_dict = input_data.model_dump()

    # Get hierarchical career prediction
    prediction_result = unified_ml_service.predict_career(input_dict)

    # Save prediction to database
    # Build top_predictions from role_probabilities
    role_probs = prediction_result.get("role_probabilities", {})
    top_predictions = [
        CareerPrediction(role=role, probability=prob, confidence_level="high" if prob > 0.7 else "medium" if prob > 0.4 else "low")
        for role, prob in sorted(role_probs.items(), key=lambda x: x[1], reverse=True)
    ]

    # If no role_probabilities, create a single entry with the predicted role
    if not top_predictions and prediction_result.get("role"):
        top_predictions = [
            CareerPrediction(
                role=prediction_result["role"],
                probability=prediction_result.get("role_confidence", 0.0),
                confidence_level="high" if prediction_result.get("role_confidence", 0) > 0.7 else "medium" if prediction_result.get("role_confidence", 0) > 0.4 else "low"
            )
        ]

    prediction_in_db = PredictionInDB(
        user_id=current_user_id,
        input_data=input_data,
        predicted_role=prediction_result.get("role", "Unknown"),
        confidence=prediction_result.get("role_confidence", 0.0),
        confidence_level="high" if prediction_result.get("role_confidence", 0) > 0.7 else "medium" if prediction_result.get("role_confidence", 0) > 0.4 else "low",
        top_predictions=top_predictions,
        placement_readiness_score=prediction_result.get("placement_readiness_score", 0.0),
        skill_gaps=prediction_result.get("skill_gaps", {}),
        shap_explanation=None,
    )

    result = await db.predictions.insert_one(prediction_in_db.model_dump(by_alias=True))
    prediction_in_db.id = str(result.inserted_id)

    # Return prediction result
    return PredictionResult(
        predicted_role=prediction_result.get("role", "Unknown"),
        confidence=prediction_result.get("role_confidence", 0.0),
        confidence_level="high" if prediction_result.get("role_confidence", 0) > 0.7 else "medium" if prediction_result.get("role_confidence", 0) > 0.4 else "low",
        top_predictions=top_predictions,
        placement_readiness_score=prediction_result.get("placement_readiness_score", 0.0),
        skill_gaps=prediction_result.get("skill_gaps", {}),
        shap_explanation=None,
    )


@router.post("/both/auto")
async def predict_both_auto(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get both career and placement predictions using the user's saved profile.
    Fetches the user's profile from MongoDB and converts it to PredictionInput.
    """
    # Check profile completion and get profile
    profile = await _check_profile_completion(current_user_id, db)

    if not unified_ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML models not available",
        )

    # Convert profile to PredictionInput
    input_data = _profile_to_prediction_input(profile.model_dump())
    input_dict = input_data.model_dump()
    result = unified_ml_service.predict_both(input_dict)

    # Save career prediction
    career_result = result["career_prediction"]
    prediction_in_db = PredictionInDB(
        user_id=current_user_id,
        input_data=input_data,
        predicted_role=career_result.get("role", "Unknown"),
        confidence=career_result.get("role_confidence", career_result.get("confidence", 0.0)),
        confidence_level=career_result.get("confidence_level", "low"),
        top_predictions=career_result.get("top_predictions", []),
        placement_readiness_score=career_result.get("placement_readiness_score", 0.0),
        skill_gaps=career_result.get("skill_gaps", {}),
    )
    await db.predictions.insert_one(prediction_in_db.model_dump(by_alias=True))

    # Save placement prediction
    placement_result = result["placement_prediction"]
    await db.placement_predictions.insert_one({
        "user_id": current_user_id,
        "input_data": input_dict,
        **placement_result
    })

    return result


@router.get("/latest", response_model=PredictionResult)
async def get_latest_prediction(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get the latest career prediction for the current user.
    Returns the most recent prediction or 404 if none exists.
    """
    pred = await db.predictions.find_one(
        {"user_id": current_user_id},
        sort=[("created_at", -1)]
    )

    if not pred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prediction found. Run a prediction first."
        )

    # Convert to PredictionResult
    return PredictionResult(
        id=str(pred["_id"]),
        predicted_role=pred.get("role", pred.get("predicted_role", "Unknown")),
        confidence=pred.get("role_confidence", pred.get("confidence", 0.0)),
        confidence_level=pred.get("confidence_level", "low"),
        top_predictions=pred.get("top_predictions", []),
        placement_readiness_score=pred.get("placement_readiness_score", 0.0),
        skill_gaps=pred.get("skill_gaps", {}),
        shap_explanation=pred.get("shap_explanation"),
        created_at=pred["created_at"],
    )