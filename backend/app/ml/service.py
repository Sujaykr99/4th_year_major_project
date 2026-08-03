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


# Mapping from frontend skill categories to model skill features
SKILL_CATEGORY_MAPPING = {
    "programming_skills": {
        "Python": "skill_Python",
        "Java": "skill_Java",
        "C++": "skill_C++",
        "JavaScript": "skill_JavaScript",
        "TypeScript": "skill_TypeScript",
        "C#": "skill_C#",
        "Go": "skill_Go",
        "Rust": "skill_Rust",
        "SQL": "skill_SQL",
        "R": "skill_R",
    },
    "framework_skills": {
        "React": "skill_React",
        "Django": "skill_Django",
        "FastAPI": "skill_FastAPI",
        "Spring": "skill_Spring",
        "Node.js": "skill_Node.js",
        "Express": "skill_Express",
        "TensorFlow": "skill_TensorFlow",
        "PyTorch": "skill_PyTorch",
        "scikit-learn": "skill_scikit-learn",
        "Pandas": "skill_Pandas",
        "NumPy": "skill_NumPy",
    },
    "tool_skills": {
        "Git": "skill_Git",
        "Docker": "skill_Docker",
        "Kubernetes": "skill_Kubernetes",
        "AWS": "skill_AWS",
        "Azure": "skill_Azure",
        "GCP": "skill_GCP",
        "Linux": "skill_Linux",
        "VS Code": "skill_VS_Code",
        "Jupyter": "skill_Jupyter",
        "Tableau": "skill_Tableau",
        "Power BI": "skill_Power_BI",
        "Excel": "skill_Excel",
        "MS Office": "skill_MS_Office",
    },
    "soft_skills": {
        "Communication": "skill_Communication",
        "Leadership": "skill_Leadership",
        "Teamwork": "skill_Teamwork",
        "Problem Solving": "skill_Problem_Solving",
        "Critical Thinking": "skill_Critical_Thinking",
        "Adaptability": "skill_Adaptability",
        "Time Management": "skill_Time_Management",
        "Creativity": "skill_Creativity",
    }
}

# Model's expected skill features (from training)
MODEL_SKILL_FEATURES = [
    "skill_Accounting",
    "skill_Communication",
    "skill_Counseling",
    "skill_Data_Analysis",
    "skill_Financial_Analysis",
    "skill_MS_Office",
    "skill_Machine_Learning",
    "skill_Marketing",
    "skill_Python",
    "skill_SQL",
]


def map_frontend_to_model_features(input_data: Dict[str, Any], feature_names: List[str]) -> Dict[str, Any]:
    """
    Map frontend PredictionInput schema to model's expected features.

    Frontend sends: programming_skills, framework_skills, tool_skills, soft_skills (lists)
    Model expects: skill_Python, skill_SQL, skill_Machine_Learning, etc. (binary flags)
    """
    model_input = {}

    # Map education level
    if "current_education" in input_data and input_data["current_education"]:
        edu = input_data["current_education"]
        if isinstance(edu, dict):
            model_input["education_level"] = edu.get("degree", "Bachelor")
        else:
            model_input["education_level"] = str(edu)
    elif "education_level" in input_data:
        model_input["education_level"] = input_data["education_level"]
    else:
        model_input["education_level"] = "Bachelor"

    # Map specialization/branch
    if "current_education" in input_data and input_data["current_education"]:
        edu = input_data["current_education"]
        if isinstance(edu, dict):
            model_input["specialization"] = edu.get("field_of_study", "Computer Science")
        else:
            model_input["specialization"] = "Computer Science"
    elif "specialization" in input_data:
        model_input["specialization"] = input_data["specialization"]
    else:
        model_input["specialization"] = "Computer Science"

    # Map CGPA - frontend uses 0-10 scale, model expects percentage
    cgpa = input_data.get("cgpa", 0)
    if cgpa > 0:
        if cgpa <= 10:
            model_input["cgpa"] = cgpa * 10  # Convert to percentage
        else:
            model_input["cgpa"] = cgpa
    else:
        model_input["cgpa"] = 0

    # Initialize all skill features to 0
    for feat in MODEL_SKILL_FEATURES:
        model_input[feat] = 0

    # Map skills from frontend categories
    all_skills = []
    for cat in ["programming_skills", "framework_skills", "tool_skills", "soft_skills"]:
        skills = input_data.get(cat, [])
        if isinstance(skills, list):
            all_skills.extend(skills)

    # Match skills to model features (case-insensitive, fuzzy matching)
    for skill in all_skills:
        skill_clean = skill.strip()
        # Direct mapping
        for cat, mapping in SKILL_CATEGORY_MAPPING.items():
            for frontend_skill, model_feat in mapping.items():
                if frontend_skill.lower() == skill_clean.lower():
                    if model_feat in MODEL_SKILL_FEATURES:
                        model_input[model_feat] = 1

    # Also check for partial matches in model features
    for skill in all_skills:
        skill_lower = skill.strip().lower()
        for model_feat in MODEL_SKILL_FEATURES:
            feat_skill = model_feat.replace("skill_", "").replace("_", " ").lower()
            if skill_lower in feat_skill or feat_skill in skill_lower:
                model_input[model_feat] = 1

    # Certifications count
    model_input["certifications_count"] = input_data.get("certifications_count", 0)

    # Ensure all expected features are present
    for feat in feature_names:
        if feat not in model_input:
            if feat.startswith("skill_") or feat in ["cgpa", "certifications_count"]:
                model_input[feat] = 0
            else:
                model_input[feat] = "unknown"

    return model_input


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

        # Map frontend schema to model features
        model_input = map_frontend_to_model_features(input_data, self.feature_names)

        # Transform input
        X = self.processor.transform_input(model_input)

        # Predict
        pred_class_encoded = self.model.predict(X)[0]
        pred_proba = self.model.predict_proba(X)[0] if hasattr(self.model, "predict_proba") else None

        # Decode predicted class using target encoder
        if self.target_encoder is not None:
            pred_class = self.target_encoder.inverse_transform([pred_class_encoded])[0]
        else:
            pred_class = str(pred_class_encoded)

        # Get class probabilities - map to decoded labels
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

        # Top 3 predictions - use decoded labels
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

        # Map frontend schema to model features
        model_input = map_frontend_to_model_features(input_data, self.feature_names)

        try:
            explanation = self.shap_explainer.explain_single(model_input)
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

    def get_model_info(self) -> Dict[str, Any]:
        """Get ML model information and metadata."""
        if not self.is_loaded:
            return {"error": "Model not loaded"}

        return {
            "model_type": type(self.model).__name__ if self.model else None,
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "classes": self.classes_,
            "class_count": len(self.classes_),
            "has_shap_explainer": self.shap_explainer is not None,
            "target_encoder_loaded": self.target_encoder is not None,
        }


# Singleton instance
ml_service = MLModelService()