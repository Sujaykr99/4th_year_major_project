"""ML Pipeline: Data loading, preprocessing, model training, and SHAP explainability."""
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, MultiLabelBinarizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import warnings
warnings.filterwarnings("ignore")

# Try to import SHAP, make it optional
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    shap = None
    SHAP_AVAILABLE = False


# Career roles from dataset
CAREER_ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Web Developer",
    "Mobile Developer",
    "DevOps Engineer",
    "Database Administrator",
    "System Administrator",
    "Network Engineer",
    "Security Analyst",
    "Cloud Architect",
    "Machine Learning Engineer",
    "Data Analyst",
    "Business Analyst",
    "Product Manager",
    "UI/UX Designer",
    "QA Engineer",
    "Technical Writer",
    "Project Manager",
    "Solutions Architect",
    "Full Stack Developer"
]


class CareerDataProcessor:
    """Handles data loading, preprocessing, and feature engineering."""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.skills_binarizer = MultiLabelBinarizer()
        self.feature_columns: List[str] = []
        self.target_column = "Career"
        self.is_fitted = False
        self.all_skills: List[str] = []

    def load_data(self) -> pd.DataFrame:
        """Load dataset from CSV."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
        df = pd.read_csv(self.dataset_path)
        print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def _clean_and_prepare_data(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Clean and prepare dataset: rename columns, parse skills, clean CGPA."""
        df = df.copy()

        # Rename columns to standard format
        column_mapping = {
            "Education Level": "education_level",
            "Specialization": "specialization",
            "Skills": "skills_raw",
            "Certifications": "certifications",
            "CGPA/Percentage": "cgpa",
            "Recommended Career": "Career"
        }
        df = df.rename(columns=column_mapping)

        # Clean CGPA/Percentage - convert to numeric, handle various formats
        def parse_cgpa(val):
            if pd.isna(val):
                return np.nan
            val_str = str(val).strip()
            # Handle percentage format (e.g., "85%")
            if val_str.endswith('%'):
                return float(val_str.rstrip('%'))
            # Handle CGPA format (e.g., "8.5" or "8.5/10")
            if '/' in val_str:
                parts = val_str.split('/')
                return float(parts[0]) / float(parts[1]) * 10 if float(parts[1]) > 10 else float(parts[0])
            return float(val_str)

        df['cgpa'] = df['cgpa'].apply(parse_cgpa)
        # If CGPA seems to be on 10-point scale, convert to percentage
        if df['cgpa'].max() <= 10:
            df['cgpa'] = df['cgpa'] * 10

        # Parse skills: comma-separated string -> list of skills
        def parse_skills(val):
            if pd.isna(val) or str(val).strip().lower() in ['none', 'nan', '']:
                return []
            return [s.strip() for s in str(val).split(',') if s.strip()]

        df['skills_list'] = df['skills_raw'].apply(parse_skills)

        # Collect all unique skills for binarization
        if fit:
            all_skills_list = []
            for skills in df['skills_list']:
                all_skills_list.extend(skills)
            self.all_skills = sorted(list(set(all_skills_list)))
            print(f"Found {len(self.all_skills)} unique skills")

        # Binarize skills
        if len(self.all_skills) > 0:
            if fit:
                skills_binarized = self.skills_binarizer.fit_transform(df['skills_list'])
            else:
                skills_binarized = self.skills_binarizer.transform(df['skills_list'])

            skills_df = pd.DataFrame(
                skills_binarized,
                columns=[f"skill_{s.replace(' ', '_').replace('-', '_').replace('.', '_').replace('/', '_')}" for s in self.skills_binarizer.classes_],
                index=df.index
            )
            df = pd.concat([df, skills_df], axis=1)

        # Drop raw skills column
        df = df.drop(columns=['skills_raw', 'skills_list'], errors='ignore')

        # Clean certifications
        def parse_certs(val):
            if pd.isna(val) or str(val).strip().lower() in ['none', 'nan', '']:
                return 0
            return len([c.strip() for c in str(val).split(',') if c.strip()])

        df['certifications_count'] = df['certifications'].apply(parse_certs)
        df = df.drop(columns=['certifications'], errors='ignore')

        # Fill missing CGPA with median
        if df['cgpa'].isna().any():
            median_cgpa = df['cgpa'].median()
            df['cgpa'] = df['cgpa'].fillna(median_cgpa)

        return df

    def explore_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Explore dataset structure and statistics."""
        # Clean data first for exploration
        df_clean = self._clean_and_prepare_data(df, fit=False)
        return {
            "shape": df_clean.shape,
            "columns": df_clean.columns.tolist(),
            "dtypes": df_clean.dtypes.to_dict(),
            "missing_values": df_clean.isnull().sum().to_dict(),
            "target_distribution": df_clean[self.target_column].value_counts().to_dict() if self.target_column in df_clean.columns else {},
            "numeric_stats": df_clean.describe().to_dict() if len(df_clean.select_dtypes(include=[np.number]).columns) > 0 else {}
        }

    def preprocess(self, df: pd.DataFrame, fit: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess data: handle missing values, encode categorical, scale numeric."""
        # Clean and prepare data first
        df = self._clean_and_prepare_data(df, fit=fit)

        # Separate features and target
        if self.target_column in df.columns:
            y = df[self.target_column].values
            X = df.drop(columns=[self.target_column])
        else:
            y = None
            X = df

        # Identify column types
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

        if fit:
            self.feature_columns = X.columns.tolist()

            # Fit label encoders for categorical columns
            for col in categorical_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.label_encoders[col] = le

            # Fit scaler on numeric columns
            if numeric_cols:
                self.scaler.fit(X[numeric_cols])
                X[numeric_cols] = self.scaler.transform(X[numeric_cols])

            self.is_fitted = True
        else:
            # Transform using fitted encoders/scaler
            for col in categorical_cols:
                if col in self.label_encoders:
                    # Handle unseen categories
                    le = self.label_encoders[col]
                    X[col] = X[col].astype(str).apply(
                        lambda x: le.transform([x])[0] if x in le.classes_ else -1
                    )

            if numeric_cols:
                X[numeric_cols] = self.scaler.transform(X[numeric_cols])

        # Ensure column order matches training
        X = X[self.feature_columns]

        return X.values, y

    def transform_input(self, input_data: Dict[str, Any]) -> np.ndarray:
        """Transform single input dict to model-ready array.

        Expects input_data to already have the processed feature names
        (e.g., 'education_level', 'specialization', 'cgpa', 'skill_Python', etc.)
        """
        # Create DataFrame with same structure as training features
        df = pd.DataFrame([input_data])

        # Add missing feature columns with defaults
        for col in self.feature_columns:
            if col not in df.columns:
                # Default to 0 for numeric/skill columns, "unknown" for categorical
                if col.startswith('skill_') or col in ['cgpa', 'certifications_count']:
                    df[col] = 0
                else:
                    df[col] = "unknown"

        # Ensure column order matches training
        df = df[self.feature_columns]

        # Apply label encoding and scaling (without re-running raw data cleaning)
        # Identify column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        # Transform using fitted encoders/scaler
        for col in categorical_cols:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                df[col] = df[col].astype(str).apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )

        if numeric_cols:
            df[numeric_cols] = self.scaler.transform(df[numeric_cols])

        # Ensure column order matches training
        df = df[self.feature_columns]

        return df.values

    def save(self, path: str):
        """Save preprocessor to disk."""
        joblib.dump({
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
            "skills_binarizer": self.skills_binarizer,
            "all_skills": self.all_skills,
            "feature_columns": self.feature_columns,
            "target_column": self.target_column,
            "is_fitted": self.is_fitted
        }, path)

    @classmethod
    def load(cls, path: str) -> "CareerDataProcessor":
        """Load preprocessor from disk."""
        data = joblib.load(path)
        processor = cls("")
        processor.scaler = data["scaler"]
        processor.label_encoders = data["label_encoders"]
        processor.skills_binarizer = data["skills_binarizer"]
        processor.all_skills = data["all_skills"]
        processor.feature_columns = data["feature_columns"]
        processor.target_column = data["target_column"]
        processor.is_fitted = data["is_fitted"]
        return processor


class CareerModelTrainer:
    """Trains and evaluates multiple ML models for career prediction."""

    def __init__(self, processor: CareerDataProcessor):
        self.processor = processor
        self.models: Dict[str, Any] = {}
        self.best_model_name: Optional[str] = None
        self.best_model: Any = None
        self.results: Dict[str, Dict] = {}
        self.target_encoder = LabelEncoder()

    def get_models(self) -> Dict[str, Any]:
        """Return dictionary of models to train."""
        return {
            "RandomForest": RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            "XGBoost": XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                eval_metric="mlogloss"
            ),
            "SVM": SVC(
                kernel="rbf",
                C=10,
                gamma="scale",
                probability=True,
                random_state=42
            )
        }

    def train_all(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict]:
        """Train all models and return evaluation results using cross-validation."""
        # Encode target labels
        y_encoded = self.target_encoder.fit_transform(y)

        # Use cross-validation for robust evaluation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Also keep a holdout test set for final evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        self.models = self.get_models()

        for name, model in self.models.items():
            print(f"\nTraining {name}...")

            # Cross-validation scores
            cv_f1_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted', n_jobs=-1)
            cv_acc_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1)

            print(f"  CV F1: {cv_f1_scores.mean():.4f} (+/- {cv_f1_scores.std()*2:.4f})")
            print(f"  CV Acc: {cv_acc_scores.mean():.4f} (+/- {cv_acc_scores.std()*2:.4f})")

            # Train on full training set for final evaluation
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

            # Calculate metrics on holdout test set
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
            rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

            result = {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "cv_f1_mean": cv_f1_scores.mean(),
                "cv_f1_std": cv_f1_scores.std(),
                "cv_acc_mean": cv_acc_scores.mean(),
                "cv_acc_std": cv_acc_scores.std(),
                "cv_f1_scores": cv_f1_scores.tolist(),
                "cv_acc_scores": cv_acc_scores.tolist(),
                "classification_report": classification_report(y_test, y_pred, zero_division=0),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
            }

            if y_proba is not None:
                try:
                    result["roc_auc"] = roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")
                except:
                    result["roc_auc"] = None

            self.results[name] = result
            print(f"  Test Accuracy: {acc:.4f}, Test F1: {f1:.4f}")

        # Select best model by CV F1 score (more robust)
        self.best_model_name = max(self.results, key=lambda k: self.results[k]["cv_f1_mean"])
        self.best_model = self.models[self.best_model_name]
        print(f"\nBest model: {self.best_model_name} (CV F1: {self.results[self.best_model_name]['cv_f1_mean']:.4f})")

        return self.results

    def get_best_model(self):
        return self.best_model, self.best_model_name, self.target_encoder

    def save_model(self, model, path: str):
        joblib.dump(model, path)


class SHAPExplainer:
    """SHAP-based model explainability."""

    def __init__(self, model, processor: CareerDataProcessor, X_train: np.ndarray, feature_names: List[str]):
        self.model = model
        self.processor = processor
        self.feature_names = feature_names
        self.explainer = None
        if SHAP_AVAILABLE:
            self._build_explainer(X_train)
        else:
            print("SHAP not available, explainer disabled")

    def _build_explainer(self, X_train: np.ndarray):
        """Build SHAP explainer based on model type."""
        model_type = type(self.model).__name__

        if "XGB" in model_type or "RandomForest" in model_type or "DecisionTree" in model_type:
            self.explainer = shap.TreeExplainer(self.model)
        else:
            # Use KernelExplainer for other models (slower but works)
            # Sample background data for efficiency
            background = shap.sample(X_train, min(100, len(X_train)), random_state=42)
            self.explainer = shap.KernelExplainer(self.model.predict_proba, background)

    def explain(self, X: np.ndarray) -> Dict[str, Any]:
        """Generate SHAP explanations for predictions."""
        if not SHAP_AVAILABLE or self.explainer is None:
            return {"error": "SHAP explainer not available"}

        shap_values = self.explainer.shap_values(X)

        # Handle multi-class output
        if isinstance(shap_values, list):
            # Multi-class: shap_values is list of arrays (one per class)
            # For single prediction, get values for predicted class
            if len(X) == 1:
                pred_class = self.model.predict(X)[0]
                class_idx = list(self.model.classes_).index(pred_class)
                shap_vals = shap_values[class_idx][0]
            else:
                # For batch, return all
                shap_vals = shap_values
        else:
            shap_vals = shap_values

        # Calculate feature importance (mean absolute SHAP)
        if len(shap_vals.shape) == 1:
            importance = np.abs(shap_vals)
        else:
            importance = np.mean(np.abs(shap_vals), axis=0)

        # Create feature importance dict
        feature_importance = dict(zip(self.feature_names, importance.tolist()))
        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))

        return {
            "shap_values": shap_vals.tolist() if hasattr(shap_vals, "tolist") else shap_vals,
            "feature_names": self.feature_names,
            "feature_importance": feature_importance,
            "base_value": float(self.explainer.expected_value) if hasattr(self.explainer, "expected_value") else 0.0
        }

    def explain_single(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Explain a single prediction from raw input."""
        if not SHAP_AVAILABLE:
            return {"error": "SHAP not available"}
        X = self.processor.transform_input(input_dict)
        return self.explain(X)

    def save(self, path: str):
        joblib.dump({
            "explainer": self.explainer,
            "feature_names": self.feature_names
        }, path)

    @classmethod
    def load(cls, path: str, model, processor: CareerDataProcessor):
        data = joblib.load(path)
        explainer = cls.__new__(cls)  # Create instance without calling __init__
        explainer.model = model
        explainer.processor = processor
        explainer.feature_names = data["feature_names"]
        explainer.explainer = data["explainer"]
        return explainer


def run_training_pipeline(dataset_path: str, output_dir: str) -> Dict[str, Any]:
    """Complete training pipeline: load -> preprocess -> train -> explain -> save."""
    import json
    from datetime import datetime

    os.makedirs(output_dir, exist_ok=True)

    # 1. Load and preprocess
    print("Loading data...")
    processor = CareerDataProcessor(dataset_path)
    df = processor.load_data()

    print("Exploring data...")
    exploration = processor.explore_data(df)

    print("Preprocessing...")
    X, y = processor.preprocess(df, fit=True)

    # 2. Train models
    print("Training models...")
    trainer = CareerModelTrainer(processor)
    results = trainer.train_all(X, y)

    best_model, best_name, target_encoder = trainer.get_best_model()

    # 3. Create SHAP explainer (optional)
    print("Building SHAP explainer...")
    shap_explainer = SHAPExplainer(best_model, processor, X, processor.feature_columns)

    # 4. Save everything
    print("Saving artifacts...")
    processor.save(os.path.join(output_dir, "processor.pkl"))
    trainer.save_model(best_model, os.path.join(output_dir, "model.pkl"))

    if SHAP_AVAILABLE and shap_explainer.explainer is not None:
        shap_explainer.save(os.path.join(output_dir, "shap_explainer.pkl"))
        print("SHAP explainer saved")
    else:
        print("SHAP explainer not available, skipping")

    # Save label encoder for target
    joblib.dump(target_encoder, os.path.join(output_dir, "target_encoder.pkl"))

    # 5. Save model metadata with versioning
    metadata = {
        "model_version": "1.0.0",
        "model_type": best_name,
        "training_date": datetime.utcnow().isoformat() + "Z",
        "dataset": {
            "source": os.path.basename(dataset_path),
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "target_column": "Recommended Career",
            "description": "Kaggle Career Recommendation Dataset"
        },
        "preprocessing": {
            "cgpa_normalization": "Converted to percentage scale (0-100)",
            "skills_binarization": "MultiLabelBinarizer on comma-separated skills",
            "categorical_encoding": "LabelEncoder for education_level and specialization",
            "feature_scaling": "StandardScaler on numeric features",
            "duplicates_removed": 1,
            "missing_values_filled": "CGPA filled with median"
        },
        "features": processor.feature_columns,
        "classes": target_encoder.classes_.tolist(),
        "model_comparison": {
            name: {
                "accuracy": res["accuracy"],
                "f1_score": res["f1_score"],
                "cv_f1_mean": res.get("cv_f1_mean"),
                "cv_f1_std": res.get("cv_f1_std"),
                "cv_acc_mean": res.get("cv_acc_mean"),
                "cv_acc_std": res.get("cv_acc_std"),
                "precision": res["precision"],
                "recall": res["recall"]
            }
            for name, res in results.items()
        },
        "best_model": {
            "name": best_name,
            "f1_score": results[best_name]["f1_score"],
            "cv_f1_mean": results[best_name].get("cv_f1_mean"),
            "accuracy": results[best_name]["accuracy"]
        },
        "reproduction": {
            "command": f"python -m app.ml.train --data {dataset_path} --output {output_dir}",
            "requirements": "backend/requirements.txt",
            "python_version": "3.14"
        }
    }

    with open(os.path.join(output_dir, "model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("Training pipeline complete!")
    return {
        "best_model": best_name,
        "results": results,
        "exploration": exploration,
        "feature_names": processor.feature_columns,
        "classes": target_encoder.classes_.tolist(),
        "metadata": metadata
    }