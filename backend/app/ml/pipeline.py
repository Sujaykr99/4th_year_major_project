"""ML Pipeline: Data loading, preprocessing, model training, and SHAP explainability."""
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import shap
import warnings
warnings.filterwarnings("ignore")


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
        self.feature_columns: List[str] = []
        self.target_column = "Career"
        self.is_fitted = False

    def load_data(self) -> pd.DataFrame:
        """Load dataset from CSV."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
        df = pd.read_csv(self.dataset_path)
        print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def explore_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Explore dataset structure and statistics."""
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "target_distribution": df[self.target_column].value_counts().to_dict() if self.target_column in df.columns else {},
            "numeric_stats": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
        }

    def preprocess(self, df: pd.DataFrame, fit: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess data: handle missing values, encode categorical, scale numeric."""
        df = df.copy()

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
        """Transform single input dict to model-ready array."""
        # Create DataFrame with same structure
        df = pd.DataFrame([input_data])

        # Add missing columns with defaults
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0 if col in df.select_dtypes(include=[np.number]).columns else "unknown"

        X, _ = self.preprocess(df, fit=False)
        return X

    def save(self, path: str):
        """Save preprocessor to disk."""
        joblib.dump({
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
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
        """Train all models and return evaluation results."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.models = self.get_models()

        for name, model in self.models.items():
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

            # Calculate metrics
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
            rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

            result = {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1,
                "classification_report": classification_report(y_test, y_pred, zero_division=0),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
            }

            if y_proba is not None:
                try:
                    result["roc_auc"] = roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")
                except:
                    result["roc_auc"] = None

            self.results[name] = result
            print(f"  Accuracy: {acc:.4f}, F1: {f1:.4f}")

        # Select best model by F1 score
        self.best_model_name = max(self.results, key=lambda k: self.results[k]["f1_score"])
        self.best_model = self.models[self.best_model_name]
        print(f"\nBest model: {self.best_model_name} (F1: {self.results[self.best_model_name]['f1_score']:.4f})")

        return self.results

    def get_best_model(self):
        return self.best_model, self.best_model_name

    def save_model(self, model, path: str):
        joblib.dump(model, path)


class SHAPExplainer:
    """SHAP-based model explainability."""

    def __init__(self, model, processor: CareerDataProcessor, X_train: np.ndarray, feature_names: List[str]):
        self.model = model
        self.processor = processor
        self.feature_names = feature_names
        self.explainer = None
        self._build_explainer(X_train)

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
        explainer = cls(model, processor, np.array([]), data["feature_names"])
        explainer.explainer = data["explainer"]
        return explainer


def run_training_pipeline(dataset_path: str, output_dir: str) -> Dict[str, Any]:
    """Complete training pipeline: load -> preprocess -> train -> explain -> save."""
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

    best_model, best_name = trainer.get_best_model()

    # 3. Create SHAP explainer
    print("Building SHAP explainer...")
    shap_explainer = SHAPExplainer(best_model, processor, X, processor.feature_columns)

    # 4. Save everything
    print("Saving artifacts...")
    processor.save(os.path.join(output_dir, "processor.pkl"))
    trainer.save_model(best_model, os.path.join(output_dir, "model.pkl"))
    shap_explainer.save(os.path.join(output_dir, "shap_explainer.pkl"))

    # Save label encoder for target
    target_encoder = LabelEncoder()
    target_encoder.fit(y)
    joblib.dump(target_encoder, os.path.join(output_dir, "target_encoder.pkl"))

    print("Training pipeline complete!")
    return {
        "best_model": best_name,
        "results": results,
        "exploration": exploration,
        "feature_names": processor.feature_columns,
        "classes": target_encoder.classes_.tolist()
    }