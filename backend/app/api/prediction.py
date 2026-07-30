"""Prediction API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import get_current_user_id
from app.core.database import get_database
from app.ml.service import MLModelService, get_ml_service
from app.models.schemas import PredictionInput, PredictionResult, PredictionHistory, SHAPExplanation

router = APIRouter()


@router.post("/predict", response_model=PredictionResult)
async def predict_career(
    input_data: PredictionInput,
    user_id: str = Depends(get_current_user_id),
    ml: MLModelService = Depends(get_ml_service),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Predict career based on student profile."""
    if not ml.is_loaded:
        raise HTTPException(status_code=503, detail="ML model not loaded")

    # Convert to dict for ML service
    input_dict = input_data.model_dump()

    # Get prediction with explanation
    result = ml.predict_with_explanation(input_dict)

    prediction = result["prediction"]
    explanation = result["explanation"]

    # Calculate readiness score
    readiness_score = ml.calculate_placement_readiness(input_dict)

    # Build response
    response = PredictionResult(
        predicted_role=prediction["predicted_role"],
        confidence=prediction["confidence"],
        confidence_level=prediction["confidence_level"],
        top_predictions=prediction["top_predictions"],
        placement_readiness_score=readiness_score,
        skill_gaps={},  # Will be filled by roadmap generator
        shap_explanation=explanation.get("feature_importance") if explanation else None
    )

    # Save to history
    await db.predictions.insert_one({
        "user_id": user_id,
        "input_data": input_dict,
        "result": response.model_dump(),
        "created_at": response.created_at
    })

    return response


@router.post("/explain", response_model=SHAPExplanation)
async def explain_prediction(
    input_data: PredictionInput,
    user_id: str = Depends(get_current_user_id),
    ml: MLModelService = Depends(get_ml_service)
):
    """Get SHAP explanation for a prediction."""
    if not ml.is_loaded:
        raise HTTPException(status_code=503, detail="ML model not loaded")

    explanation = ml.explain(input_data.model_dump())
    return explanation


@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get user's prediction history."""
    cursor = db.predictions.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    predictions = await cursor.to_list(length=limit)

    history = []
    for pred in predictions:
        result = pred.get("result", {})
        history.append(PredictionHistory(
            id=str(pred["_id"]),
            predicted_role=result.get("predicted_role", "Unknown"),
            confidence=result.get("confidence", 0),
            placement_readiness_score=result.get("placement_readiness_score", 0),
            created_at=pred["created_at"]
        ))

    return history


@router.get("/model-info")
async def get_model_info(
    ml: MLModelService = Depends(get_ml_service)
):
    """Get ML model information."""
    return ml.get_model_info()