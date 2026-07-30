"""ML Model Service: Load trained model and provide prediction/explanation API."""
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

from app.core.config import settings
from app.ml.pipeline import CareerDataProcessor, SHAPExplainer, CAREER_ROLES


class MLModelService:
    """Service for loading ML artifacts and making predictions."""

    def __init__(self):
        self.model = None
        self.processor = None
        self.shap_explainer = None
        self.target_encoder = None
        self.is_loaded = False
        self.feature_names: List[str] = []
        self.classes_: List[str] = CAREER_ROLES

    def load_artifacts(self, model_dir: Optional[str] = None) -> bool:
        """Load model, processor, SHAP explainer, and target encoder."""
        if model_dir is None:
            model_dir = str(Path(settings.MODEL_PATH).parent)

        model_path = Path(model_dir) / "model.pkl"
        processor_path = Path(model_dir) / "processor.pkl"
        shap_path = Path(model_dir) / "shap_explainer.pkl"
        target_encoder_path = Path(model_dir) / "target_encoder.pkl"

        try:
            # Load processor
            if processor_path.exists():
                self.processor = CareerDataProcessor.load(str(processor_path))
                self.feature_names = self.processor.feature_columns
                print(f"Loaded processor with {len(self.feature_names)} features")
            else:
                print(f"Processor not found at {processor_path}")
                return False

            # Load model
            if model_path.exists():
                self.model = joblib.load(model_path)
                print(f"Loaded model: {type(self.model).__name__}")
            else:
                print(f"Model not found at {model_path}")
                return False

            # Load target encoder
            if target_encoder_path.exists():
                self.target_encoder = joblib.load(target_encoder_path)
                self.classes_ = self.target_encoder.classes_.tolist()
                print(f"Loaded target encoder with {len(self.classes_)} classes")
            else:
                print("Target encoder not found, using default classes")

            # Load SHAP explainer
            if shap_path.exists() and self.model is not None and self.processor is not None:
                self.shap_explainer = SHAPExplainer.load(str(shap_path), self.model, self.processor)
                print("Loaded SHAP explainer")
            else:
                print("SHAP explainer not found or model/processor missing")

            self.is_loaded = True
            return True

        except Exception as e:
            print(f"Error loading ML artifacts: {e}")
            self.is_loaded = False
            return False

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make career prediction from input features."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_artifacts() first.")

        # Transform input
        X = self.processor.transform_input(input_data)

        # Predict
        pred_class = self.model.predict(X)[0]
        pred_proba = self.model.predict_proba(X)[0] if hasattr(self.model, "predict_proba") else None

        # Get class probabilities
        if pred_proba is not None:
            class_probs = dict(zip(self.classes_, pred_proba.tolist()))
            confidence = float(max(pred_proba))
        else:
            class_probs = {pred_class: 1.0}
            confidence = 1.0

        # Determine confidence level
        if confidence >= 0.8:
            confidence_level = "high"
        elif confidence >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Top 3 predictions
        top_predictions = sorted(class_probs.items(), key=lambda x: x[1], reverse=True)[:3]
        top_predictions_list = [
            {"role": role, "probability": prob, "confidence_level": "high" if prob >= 0.8 else "medium" if prob >= 0.5 else "low"}
            for role, prob in top_predictions
        ]

        return {
            "predicted_role": pred_class,
            "confidence": confidence,
            "confidence_level": confidence_level,
            "top_predictions": top_predictions_list,
            "all_probabilities": class_probs
        }

    def explain(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SHAP explanation for prediction."""
        if not self.is_loaded or self.shap_explainer is None:
            return {"error": "SHAP explainer not available"}

        try:
            explanation = self.shap_explainer.explain_single(input_data)
            return explanation
        except Exception as e:
            return {"error": f"SHAP explanation failed: {str(e)}"}

    def predict_with_explanation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction and generate explanation in one call."""
        prediction = self.predict(input_data)
        explanation = self.explain(input_data)

        return {
            "prediction": prediction,
            "explanation": explanation
        }

    def calculate_placement_readiness(self, input_data: Dict[str, Any]) -> float:
        """Calculate placement readiness score (0-100) based on profile completeness and strength."""
        score = 0.0

        # Academic score (0-25)
        cgpa = input_data.get("cgpa", 0)
        if cgpa > 0:
            score += min(25, (cgpa / 10) * 25)

        # Skills score (0-30)
        num_programming = len(input_data.get("programming_skills", []))
        num_frameworks = len(input_data.get("framework_skills", []))
        num_tools = len(input_data.get("tool_skills", []))
        num_soft = len(input_data.get("soft_skills", []))
        skill_score = min(30, (num_programming * 2 + num_frameworks * 2 + num_tools * 1.5 + num_soft * 1))
        score += skill_score

        # Experience score (0-25)
        num_projects = input_data.get("num_projects", 0)
        num_internships = input_data.get("num_internships", 0)
        has_research = input_data.get("has_research", False)
        has_publications = input_data.get("has_publications", False)
        hackathons = input_data.get("hackathon_participation", 0)
        certs = input_data.get("certifications_count", 0)

        exp_score = min(25, num_projects * 2 + num_internships * 5 + (5 if has_research else 0) +
                        (5 if has_publications else 0) + hackathons * 1 + certs * 1.5)
        score += exp_score

        # Activity score (0-20)
        # Based on recency and diversity of activities
        activity_score = min(20, hackathons * 2 + certs * 2)
        score += activity_score

        return round(min(100, score), 1)

    def get_skill_gaps(self, input_data: Dict[str, Any], target_role: str) -> Dict[str, List[str]]:
        """Identify missing skills for target role."""
        from app.services.roadmap_generator import identify_skill_gaps

        current_skills = []
        current_skills.extend(input_data.get("programming_skills", []))
        current_skills.extend(input_data.get("framework_skills", []))
        current_skills.extend(input_data.get("tool_skills", []))
        current_skills.extend(input_data.get("soft_skills", []))

        gaps = identify_skill_gaps(current_skills, target_role)

        return {
            "missing_required": gaps["missing_required"],
            "missing_nice_to_have": gaps["missing_nice_to_have"],
            "have_required": gaps["have_required"],
            "have_nice_to_have": gaps["have_nice_to_have"]
        }


# Singleton instance
ml_service = MLModelService()