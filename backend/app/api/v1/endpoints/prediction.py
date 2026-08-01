"""Prediction endpoints."""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.ml.service import MLModelService
from app.models.schemas import (
    PredictionHistory,
    PredictionInDB,
    PredictionInput,
    PredictionResult,
)
from app.core import security

router = APIRouter()

# Initialize ML service (will be loaded on startup)
ml_service = MLModelService()


@router.on_event("startup")
async def load_ml_model():
    """Load ML model on startup."""
    await ml_service.load()


@router.post("/predict", response_model=PredictionResult)
async def predict_career(
    input_data: PredictionInput,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Make a career prediction for the current user.
    """
    if not ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not available",
        )

    # Convert input data to dict for ML service
    input_dict = input_data.model_dump()

    # Get prediction
    prediction_result = ml_service.predict(input_dict)

    # Save prediction to database
    prediction_in_db = PredictionInDB(
        user_id=current_user_id,
        input_data=input_data,
        **{
            k: v
            for k, v in prediction_result.items()
            if k
            in [
                "predicted_role",
                "confidence",
                "confidence_level",
                "top_predictions",
                "placement_readiness_score",
                "skill_gaps",
                "shap_explanation",
            ]
        },
    )

    result = await db.predictions.insert_one(prediction_in_db.model_dump(by_alias=True))
    prediction_in_db.id = str(result.inserted_id)

    # Return prediction result
    return PredictionResult(
        predicted_role=prediction_result["predicted_role"],
        confidence=prediction_result["confidence"],
        confidence_level=prediction_result["confidence_level"],
        top_predictions=prediction_result["top_predictions"],
        placement_readiness_score=prediction_result["placement_readiness_score"],
        skill_gaps=prediction_result["skill_gaps"],
        shap_explanation=prediction_result.get("shap_explanation"),
    )


@router.post("/explain")
async def explain_prediction(
    input_data: PredictionInput,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get SHAP explanation for a career prediction.
    """
    if not ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not available",
        )

    # Convert input data to dict for ML service
    input_dict = input_data.model_dump()

    # Get explanation
    explanation = ml_service.explain(input_dict)

    return explanation


@router.post("/predict-explain", response_model=Dict[str, Any])
async def predict_and_explain(
    input_data: PredictionInput,
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    Get prediction and SHAP explanation together.
    """
    if not ml_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not available",
        )

    # Convert input data to dict for ML service
    input_dict = input_data.model_dump()

    # Get prediction and explanation
    result = ml_service.predict_with_explanation(input_dict)

    # Save prediction to database
    prediction_in_db = PredictionInDB(
        user_id=current_user_id,
        input_data=input_data,
        **{
            k: v
            for k, v in result["prediction"].items()
            if k
            in [
                "predicted_role",
                "confidence",
                "confidence_level",
                "top_predictions",
                "placement_readiness_score",
                "skill_gaps",
                "shap_explanation",
            ]
        },
    )

    await db.predictions.insert_one(prediction_in_db.model_dump(by_alias=True))

    return result


@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(
    current_user_id: str = Depends(security.get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
    limit: int = 10,
    skip: int = 0,
) -> Any:
    """
    Get prediction history for the current user.
    """
    cursor = db.predictions.find({"user_id": current_user_id}).sort(
        "created_at", -1
    ).skip(skip).limit(limit)

    predictions = await cursor.to_list(length=limit)
    history = []
    for pred in predictions:
        history.append(
            PredictionHistory(
                id=str(pred["_id"]),
                predicted_role=pred["predicted_role"],
                confidence=pred["confidence"],
                placement_readiness_score=pred["placement_readiness_score"],
                created_at=pred["created_at"],
            )
        )

    return history