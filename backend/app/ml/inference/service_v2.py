"""ML Model Service V2: Hierarchical Career Predictor + Placement Predictor."""
import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

from app.core.config import settings
from app.ml.inference.hierarchical_predictor_v2 import HierarchicalPredictorV2
from app.ml.inference.readiness_scorer import score_from_student_profile as calculate_readiness_score


# ============================================================
# PLACEMENT MODEL FEATURE MAPPING
# ============================================================

PLACEMENT_FEATURE_ORDER = [
    'age', 'gender', 'cgpa', 'branch', 'college_tier',
    'internships_count', 'projects_count', 'certifications_count',
    'coding_skill_score', 'aptitude_score', 'communication_skill_score',
    'logical_reasoning_score', 'hackathons_participated',
    'github_repos', 'linkedin_connections', 'mock_interview_score',
    'attendance_percentage', 'backlogs', 'extracurricular_score',
    'leadership_score', 'volunteer_experience', 'sleep_hours',
    'study_hours_per_day'
]

PLACEMENT_CATEGORICAL = ['gender', 'branch', 'college_tier', 'volunteer_experience']


def map_frontend_to_placement_features(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Map frontend PredictionInput schema to placement model features."""
    # Build all features with defaults
    feature_map = {
        'age': input_data.get('age', 22),
        'gender': input_data.get('gender', 'Male'),
        'cgpa': input_data.get('cgpa', 7.0),
        'branch': input_data.get('branch', 'Computer Science'),
        'college_tier': input_data.get('college_tier', 2),
        'internships_count': input_data.get('num_internships', 0),
        'projects_count': input_data.get('num_projects', 0),
        'certifications_count': input_data.get('certifications_count', 0),
        'coding_skill_score': input_data.get('coding_skill_score', 50),
        'aptitude_score': input_data.get('aptitude_score', 50),
        'communication_skill_score': input_data.get('communication_skill_score', 50),
        'logical_reasoning_score': input_data.get('logical_reasoning_score', 50),
        'hackathons_participated': input_data.get('hackathon_participation', 0),
        'github_repos': input_data.get('github_repos', 0),
        'linkedin_connections': input_data.get('linkedin_connections', 0),
        'mock_interview_score': input_data.get('mock_interview_score', 50),
        'attendance_percentage': input_data.get('attendance_percentage', 75),
        'backlogs': input_data.get('backlogs', 0),
        'extracurricular_score': input_data.get('extracurricular_score', 50),
        'leadership_score': input_data.get('leadership_score', 50),
        'volunteer_experience': input_data.get('volunteer_experience', 'No'),
        'sleep_hours': input_data.get('sleep_hours', 7),
        'study_hours_per_day': input_data.get('study_hours_per_day', 3),
    }

    # Return in the exact order expected by the processor
    return {k: feature_map[k] for k in PLACEMENT_FEATURE_ORDER}


def map_frontend_to_career_features(input_data: Dict[str, Any], feature_names: List[str]) -> Dict[str, Any]:
    """
    Map frontend PredictionInput schema to hierarchical career model features.
    Career model expects 66 binary features (skills + composites + exp/edu).
    """
    model_input = {}

    # Initialize all features to 0
    for feat in feature_names:
        if feat.startswith('skill_') or feat.endswith('_score') or feat in ['total_skills', 'language_diversity']:
            model_input[feat] = 0
        elif feat in ['years_code_pro', 'years_code', 'ed_level', 'work_exp_count', 'is_developer', 'remote_pref']:
            model_input[feat] = 0
        else:
            model_input[feat] = 0

    # Map skills from frontend categories
    all_skills = []
    for cat in ['programming_skills', 'framework_skills', 'tool_skills', 'soft_skills']:
        skills = input_data.get(cat, [])
        if isinstance(skills, list):
            all_skills.extend(skills)

    # Skill name normalization (frontend -> model format)
    skill_name_map = {
        # Programming languages
        'Python': 'skill_python',
        'Java': 'skill_java',
        'C++': 'skill_cpp',
        'C': 'skill_c',
        'C#': 'skill_csharp',
        'JavaScript': 'skill_javascript',
        'TypeScript': 'skill_typescript',
        'Go': 'skill_go',
        'Rust': 'skill_rust',
        'SQL': 'skill_sql',
        'R': 'skill_r',
        'PHP': 'skill_php',
        'Swift': 'skill_swift',
        'Kotlin': 'skill_kotlin',
        'Ruby': 'skill_ruby',
        # Frameworks
        'React': 'skill_react',
        'Django': 'skill_django',
        'FastAPI': 'skill_fastapi',
        'Spring': 'skill_spring',
        'Spring Boot': 'skill_spring',
        'Node.js': 'skill_nodejs',
        'Express': 'skill_express',
        'Next.js': 'skill_nextjs',
        'Vue.js': 'skill_vue',
        'Angular': 'skill_angular',
        'Flask': 'skill_flask',
        'ASP.NET Core': 'skill_aspnet_core',
        'TensorFlow': 'skill_tensorflow',
        'PyTorch': 'skill_pytorch',
        'scikit-learn': 'skill_scikit_learn',
        'Pandas': 'skill_pandas',
        'NumPy': 'skill_numpy',
        # Tools/Platforms
        'Git': 'skill_git',
        'Docker': 'skill_docker',
        'Kubernetes': 'skill_kubernetes',
        'AWS': 'skill_aws',
        'Azure': 'skill_microsoft_azure',
        'GCP': 'skill_google_cloud',
        'Google Cloud': 'skill_google_cloud',
        'Linux': 'skill_linux',
        'GitHub Actions': 'skill_github_actions',
        'GitLab CI/CD': 'skill_gitlab_ci',
        'Jenkins': 'skill_jenkins',
        'Terraform': 'skill_terraform',
        'Ansible': 'skill_ansible',
        'npm': 'skill_npm',
        'yarn': 'skill_yarn',
        'Webpack': 'skill_webpack',
        'Vite': 'skill_vite',
        'VS Code': 'skill_vs_code',
        'Jupyter': 'skill_jupyter',
        # Databases
        'PostgreSQL': 'skill_postgresql',
        'MySQL': 'skill_mysql',
        'MongoDB': 'skill_mongodb',
        'Redis': 'skill_redis',
        'SQLite': 'skill_sqlite',
        'Microsoft SQL Server': 'skill_microsoft_sql_server',
        'Oracle': 'skill_oracle',
        'Elasticsearch': 'skill_elasticsearch',
        'DynamoDB': 'skill_dynamodb',
        'Firebase': 'skill_firebase',
        'Heroku': 'skill_heroku',
        'Vercel': 'skill_vercel',
    }

    for skill in all_skills:
        skill_clean = skill.strip()
        # Direct mapping
        if skill_clean in skill_name_map:
            model_feat = skill_name_map[skill_clean]
            if model_feat in model_input:
                model_input[model_feat] = 1
        else:
            # Fuzzy matching for any skill
            skill_lower = skill_clean.lower()
            for model_feat in model_input:
                if model_feat.startswith('skill_'):
                    feat_skill = model_feat.replace('skill_', '').replace('_', ' ').lower()
                    if skill_lower == feat_skill or skill_lower in feat_skill or feat_skill in skill_lower:
                        model_input[model_feat] = 1

    # Experience/Education features
    model_input['years_code_pro'] = input_data.get('years_code_pro', 0)
    model_input['years_code'] = input_data.get('years_code', 0)
    model_input['ed_level'] = input_data.get('ed_level', 3)  # 3 = Bachelor default
    model_input['work_exp_count'] = input_data.get('work_exp_count', 0)
    model_input['is_developer'] = input_data.get('is_developer', 1)
    model_input['remote_pref'] = input_data.get('remote_pref', 1)  # 1 = hybrid default

    # Composite scores will be computed by predictor from skill features

    return model_input


# ============================================================
# HIERARCHICAL CAREER SERVICE
# ============================================================

class HierarchicalCareerService:
    """Service for hierarchical career prediction (Sector -> Role)."""

    def __init__(self):
        self.predictor = None
        self.is_loaded = False
        self.feature_names: List[str] = []
        self.sectors: List[str] = []

    def load_artifacts(
        self,
        sector_model_dir: str = "ml/saved_models_sector_v2",
        role_model_dir: str = "ml/saved_models_roles_v2",
        confidence_threshold: float = 0.4
    ) -> bool:
        """Load hierarchical model artifacts."""
        try:
            self.predictor = HierarchicalPredictorV2(
                sector_model_dir=sector_model_dir,
                role_model_dir=role_model_dir,
                confidence_threshold=confidence_threshold
            )
            self.predictor.load_all()

            # Get feature names from sector model
            with open(Path(sector_model_dir) / "sector_feature_names.json") as f:
                self.feature_names = json.load(f)

            with open(Path(sector_model_dir) / "sector_target_encoder.pkl", "rb") as f:
                sector_encoder = joblib.load(f)
                self.sectors = sector_encoder.classes_.tolist()

            self.is_loaded = True
            print(f"Loaded hierarchical career model: {len(self.feature_names)} features, {len(self.sectors)} sectors")
            return True
        except Exception as e:
            print(f"Error loading hierarchical career model: {e}")
            self.is_loaded = False
            return False

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make hierarchical career prediction."""
        if not self.is_loaded:
            raise RuntimeError("Hierarchical career model not loaded")

        # Map frontend input to model features
        model_input = map_frontend_to_career_features(input_data, self.feature_names)

        # Predict
        result = self.predictor.predict(model_input)

        # Add placement readiness score
        readiness = calculate_readiness_score(input_data)
        result['placement_readiness_score'] = readiness['readiness_score']
        result['readiness_level'] = readiness['readiness_level']
        result['readiness_breakdown'] = readiness['component_breakdown']

        # Add skill gaps for predicted role
        if result.get('role') and result['role'] != 'Unknown':
            result['skill_gaps'] = self.get_skill_gaps(input_data, result['role'])

        return result

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
        """Get model information."""
        if not self.is_loaded:
            return {"error": "Model not loaded"}

        return {
            "model_type": "Hierarchical (Sector -> Role)",
            "sector_classifier": "CatBoost",
            "role_classifiers": {
                "Web Development": "RandomForest",
                "Backend & Data Engineering": "CatBoost",
                "Cloud & DevOps": "RandomForest",
                "Security & Infrastructure": "CatBoost"
            },
            "feature_count": len(self.feature_names),
            "sectors": self.sectors,
            "confidence_threshold": self.predictor.confidence_threshold if self.predictor else 0.4
        }


# ============================================================
# PLACEMENT PREDICTION SERVICE
# ============================================================

class PlacementPredictionService:
    """Service for placement prediction (binary: Placed/Not Placed)."""

    def __init__(self):
        self.model = None
        self.processor = None
        self.target_encoder = None
        self.is_loaded = False
        self.feature_names: List[str] = []

    def load_artifacts(self, model_dir: str = "ml/saved_models") -> bool:
        """Load placement model artifacts."""
        try:
            model_path = Path(model_dir) / "placement_model.pkl"
            processor_path = Path(model_dir) / "placement_processor.pkl"
            encoder_path = Path(model_dir) / "placement_target_encoder.pkl"

            if not all(p.exists() for p in [model_path, processor_path, encoder_path]):
                print(f"Placement model artifacts not found in {model_dir}")
                return False

            self.model = joblib.load(model_path)

            # Load processor using classmethod (it was saved as dict)
            from app.ml.training.train_placement import PlacementDataProcessor
            self.processor = PlacementDataProcessor.load(processor_path)

            self.target_encoder = joblib.load(encoder_path)

            # Get feature names from processor
            if hasattr(self.processor, 'feature_columns'):
                self.feature_names = self.processor.feature_columns
            else:
                self.feature_names = PLACEMENT_FEATURE_ORDER

            self.is_loaded = True
            print(f"Loaded placement model: {type(self.model).__name__}, {len(self.feature_names)} features")
            return True
        except Exception as e:
            print(f"Error loading placement model: {e}")
            self.is_loaded = False
            return False

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make placement prediction."""
        if not self.is_loaded:
            raise RuntimeError("Placement model not loaded")

        # Map frontend input to placement features
        model_input = map_frontend_to_placement_features(input_data)

        # Transform using processor
        X = self.processor.transform_input(model_input)

        # Predict
        pred_encoded = self.model.predict(X)[0]
        pred_proba = self.model.predict_proba(X)[0] if hasattr(self.model, "predict_proba") else None

        # Decode
        pred_class = self.target_encoder.inverse_transform([pred_encoded])[0]

        # Probabilities
        if pred_proba is not None:
            classes = self.target_encoder.classes_
            prob_dict = dict(zip(classes, pred_proba.tolist()))
            confidence = float(max(pred_proba))
        else:
            prob_dict = {pred_class: 1.0}
            confidence = 1.0

        # Confidence level
        if confidence >= 0.7:
            confidence_level = "high"
        elif confidence >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return {
            "predicted_status": pred_class,
            "confidence": confidence,
            "confidence_level": confidence_level,
            "probabilities": prob_dict,
            "placement_probability": prob_dict.get("Placed", 0.0)
        }

    def predict_with_readiness(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict placement and calculate readiness score."""
        placement_result = self.predict(input_data)
        readiness = calculate_readiness_score(input_data)

        return {
            **placement_result,
            "readiness_score": readiness['readiness_score'],
            "readiness_level": readiness['readiness_level'],
            "readiness_breakdown": readiness['component_breakdown'],
            "recommendations": readiness['recommendations']
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if not self.is_loaded:
            return {"error": "Model not loaded"}

        return {
            "model_type": type(self.model).__name__ if self.model else None,
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "classes": self.target_encoder.classes_.tolist() if self.target_encoder else [],
            "target": "placement_status (binary: Placed/Not Placed)"
        }


# ============================================================
# UNIFIED ML SERVICE
# ============================================================

class UnifiedMLService:
    """Unified service combining hierarchical career + placement prediction."""

    def __init__(self):
        self.career_service = HierarchicalCareerService()
        self.placement_service = PlacementPredictionService()
        self.is_loaded = False

    def load_all(self) -> bool:
        """Load both career and placement models."""
        career_ok = self.career_service.load_artifacts()
        placement_ok = self.placement_service.load_artifacts()

        self.is_loaded = career_ok and placement_ok
        print(f"Unified ML Service loaded: career={career_ok}, placement={placement_ok}")
        return self.is_loaded

    def predict_career(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict career (hierarchical sector -> role)."""
        return self.career_service.predict(input_data)

    def predict_placement(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict placement probability."""
        return self.placement_service.predict_with_readiness(input_data)

    def predict_both(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict both career and placement."""
        career_result = self.predict_career(input_data)
        placement_result = self.predict_placement(input_data)

        return {
            "career_prediction": career_result,
            "placement_prediction": placement_result
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get info for both models."""
        return {
            "career_model": self.career_service.get_model_info(),
            "placement_model": self.placement_service.get_model_info()
        }


# Singleton instances
hierarchical_career_service = HierarchicalCareerService()
placement_service = PlacementPredictionService()
unified_ml_service = UnifiedMLService()