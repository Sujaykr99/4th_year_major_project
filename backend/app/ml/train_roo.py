"""Training script for roo_data.csv - Career prediction with high accuracy."""
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import json
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


class RooDataProcessor:
    """Handles data loading, preprocessing for roo_data.csv."""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_columns: List[str] = []
        self.target_column = "Suggested Job Role"
        self.is_fitted = False

    def load_data(self) -> pd.DataFrame:
        """Load dataset from CSV."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")
        df = pd.read_csv(self.dataset_path)
        print(f"Loaded roo dataset: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def explore_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Explore dataset structure and statistics."""
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "target_distribution": df[self.target_column].value_counts().to_dict(),
            "n_classes": df[self.target_column].nunique()
        }

    def preprocess(self, df: pd.DataFrame, fit: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess data: encode categorical, scale numeric."""
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
        df = pd.DataFrame([input_data])

        # Add missing columns with defaults
        for col in self.feature_columns:
            if col not in df.columns:
                if col in df.select_dtypes(include=[np.number]).columns:
                    df[col] = 0
                else:
                    df[col] = "unknown"

        df = df[self.feature_columns]

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        for col in categorical_cols:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                df[col] = df[col].astype(str).apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )

        if numeric_cols:
            df[numeric_cols] = self.scaler.transform(df[numeric_cols])

        df = df[self.feature_columns]
        return df.values

    def save(self, path: str):
        joblib.dump({
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
            "feature_columns": self.feature_columns,
            "target_column": self.target_column,
            "is_fitted": self.is_fitted
        }, path)

    @classmethod
    def load(cls, path: str) -> "RooDataProcessor":
        data = joblib.load(path)
        processor = cls("")
        processor.scaler = data["scaler"]
        processor.label_encoders = data["label_encoders"]
        processor.feature_columns = data["feature_columns"]
        processor.target_column = data["target_column"]
        processor.is_fitted = data["is_fitted"]
        return processor


class RooModelTrainer:
    """Trains and evaluates models for roo career prediction."""

    def __init__(self, processor: RooDataProcessor):
        self.processor = processor
        self.models: Dict[str, Any] = {}
        self.best_model_name: Optional[str] = None
        self.best_model: Any = None
        self.results: Dict[str, Dict] = {}
        self.target_encoder = LabelEncoder()

    def get_models(self) -> Dict[str, Any]:
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
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=150,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            )
        }

    def train_all(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict]:
        y_encoded = self.target_encoder.fit_transform(y)

        # Cross-validation (5-fold)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Holdout test set
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        self.models = self.get_models()

        for name, model in self.models.items():
            print(f"\nTraining {name}...")

            # Cross-validation scores
            cv_f1_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted', n_jobs=-1)
            cv_acc_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1)
            cv_roc_auc_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc_ovr', n_jobs=-1)

            print(f"  CV F1: {cv_f1_scores.mean():.4f} (+/- {cv_f1_scores.std()*2:.4f})")
            print(f"  CV Acc: {cv_acc_scores.mean():.4f} (+/- {cv_acc_scores.std()*2:.4f})")
            print(f"  CV ROC-AUC: {cv_roc_auc_scores.mean():.4f} (+/- {cv_roc_auc_scores.std()*2:.4f})")

            # Train on full training set
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

            # Test metrics
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
                "cv_roc_auc_mean": cv_roc_auc_scores.mean(),
                "cv_roc_auc_std": cv_roc_auc_scores.std(),
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

        # Best by CV F1
        self.best_model_name = max(self.results, key=lambda k: self.results[k]["cv_f1_mean"])
        self.best_model = self.models[self.best_model_name]
        print(f"\nBest model: {self.best_model_name} (CV F1: {self.results[self.best_model_name]['cv_f1_mean']:.4f})")

        return self.results

    def get_best_model(self):
        return self.best_model, self.best_model_name, self.target_encoder

    def save_model(self, model, path: str):
        joblib.dump(model, path)


def run_roo_training(dataset_path: str, output_dir: str, sample_size: Optional[int] = 10000) -> Dict[str, Any]:
    """Complete training pipeline for roo_data.csv."""
    os.makedirs(output_dir, exist_ok=True)

    print("Loading roo data...")
    processor = RooDataProcessor(dataset_path)
    df = processor.load_data()

    # Sample for faster training (stratified)
    if sample_size and len(df) > sample_size:
        print(f"Sampling {sample_size} rows from {len(df)} for faster training...")
        from sklearn.model_selection import train_test_split
        df, _ = train_test_split(df, train_size=sample_size, random_state=42, stratify=df["Suggested Job Role"])
        df = df.reset_index(drop=True)

    print("Exploring data...")
    exploration = processor.explore_data(df)

    print("Preprocessing...")
    X, y = processor.preprocess(df, fit=True)

    print("Training models...")
    trainer = RooModelTrainer(processor)
    results = trainer.train_all(X, y)

    best_model, best_name, target_encoder = trainer.get_best_model()

    print("Saving artifacts...")
    processor.save(os.path.join(output_dir, "roo_processor.pkl"))
    trainer.save_model(best_model, os.path.join(output_dir, "roo_model.pkl"))
    joblib.dump(target_encoder, os.path.join(output_dir, "roo_target_encoder.pkl"))

    # Save metadata
    metadata = {
        "model_version": "1.0.0",
        "model_type": best_name,
        "training_date": datetime.utcnow().isoformat() + "Z",
        "dataset": {
            "source": os.path.basename(dataset_path),
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "target_column": "Suggested Job Role",
            "n_classes": exploration["n_classes"]
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
                "cv_roc_auc_mean": res.get("cv_roc_auc_mean"),
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
        }
    }

    with open(os.path.join(output_dir, "roo_model_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("Training complete!")
    return {
        "best_model": best_name,
        "results": results,
        "exploration": exploration,
        "feature_names": processor.feature_columns,
        "classes": target_encoder.classes_.tolist(),
        "metadata": metadata
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train career model on roo_data.csv")
    parser.add_argument("--data", required=True, help="Path to roo_data.csv")
    parser.add_argument("--output", default="backend/ml/saved_models_roo", help="Output directory")
    parser.add_argument("--sample", type=int, default=10000, help="Sample size (default: 10000)")
    args = parser.parse_args()

    print(f"Training with: {args.data}")
    print(f"Output: {args.output}")
    print(f"Sample size: {args.sample}")

    result = run_roo_training(args.data, args.output, args.sample)

    print("\n=== RESULTS ===")
    print(f"Best model: {result['best_model']}")
    print(f"Classes: {len(result['classes'])}")
    for name, metrics in result['results'].items():
        print(f"  {name}: Acc={metrics['accuracy']:.4f}, F1={metrics['f1_score']:.4f}, CV_F1={metrics.get('cv_f1_mean', 0):.4f}")