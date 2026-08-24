#!/usr/bin/env python3
"""
Hierarchical Career Predictor V2: Sector -> Role
Uses redesigned sectors based on skill similarity
"""
import os
import json
import joblib
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

warnings.filterwarnings("ignore")

# ============================================================
# SECTOR MAPPING V2 (must match training)
# ============================================================

SECTOR_MAPPING_V2 = {
    "Frontend Developer": "Web Development",
    "Full Stack Developer": "Web Development",
    "UI/UX Designer": "Web Development",
    "Backend Developer": "Backend & Data Engineering",
    "Database Engineer": "Backend & Data Engineering",
    "Mobile App Developer": "Mobile Development",
    "DevOps Engineer": "Cloud & DevOps",
    "Cloud Engineer": "Cloud & DevOps",
    "Cyber Security Engineer": "Security & Infrastructure",
    "Network Engineer": "Security & Infrastructure",
    "Engineering Manager": "Technical Leadership & Specialized",
    "QA Engineer": "Technical Leadership & Specialized",
    "Data Scientist": "Technical Leadership & Specialized",
    "AI/ML Engineer": "Technical Leadership & Specialized",
    "Embedded Engineer": "Technical Leadership & Specialized",
}

SECTORS_V2 = [
    "Web Development",
    "Backend & Data Engineering",
    "Mobile Development",
    "Cloud & DevOps",
    "Security & Infrastructure",
    "Technical Leadership & Specialized",
]


class HierarchicalPredictorV2:
    """Hierarchical predictor V2: Sector -> Role within sector"""

    def __init__(
        self,
        sector_model_dir: str = "backend/ml/saved_models_sector_v2",
        role_model_dir: str = "backend/ml/saved_models_roles_v2",
        confidence_threshold: float = 0.4
    ):
        self.sector_model_dir = Path(sector_model_dir)
        self.role_model_dir = Path(role_model_dir)
        self.confidence_threshold = confidence_threshold

        # Sector artifacts
        self.sector_model = None
        self.sector_scaler = None
        self.sector_encoder = None
        self.sector_features = None

        # Role artifacts per sector
        self.role_models = {}
        self.role_scalers = {}
        self.role_encoders = {}
        self.role_features = {}

        # Sectors with role classifiers (more than 1 role)
        self.sectors_with_roles = [
            "Web Development",
            "Backend & Data Engineering",
            "Cloud & DevOps",
            "Security & Infrastructure",
        ]

        # Sectors with single role (no classifier needed)
        self.single_role_sectors = {
            "Mobile Development": "Mobile App Developer",
            "Technical Leadership & Specialized": "Engineering Manager",
        }

    def load_sector_artifacts(self):
        """Load sector classifier artifacts"""
        self.sector_model = joblib.load(self.sector_model_dir / "sector_model.pkl")
        self.sector_scaler = joblib.load(self.sector_model_dir / "sector_scaler.pkl")
        self.sector_encoder = joblib.load(self.sector_model_dir / "sector_target_encoder.pkl")
        with open(self.sector_model_dir / "sector_feature_names.json") as f:
            self.sector_features = json.load(f)

    def load_role_artifacts(self):
        """Load role classifier artifacts for each sector"""
        for sector in self.sectors_with_roles:
            sector_safe = sector.replace(" ", "_").replace("&", "and").replace("/", "_")
            model_path = self.role_model_dir / sector_safe / f"role_model_{sector_safe}.pkl"
            scaler_path = self.role_model_dir / sector_safe / f"role_scaler_{sector_safe}.pkl"
            encoder_path = self.role_model_dir / sector_safe / f"role_target_encoder_{sector_safe}.pkl"
            features_path = self.role_model_dir / sector_safe / f"role_feature_names_{sector_safe}.json"

            if model_path.exists():
                self.role_models[sector] = joblib.load(model_path)
                self.role_scalers[sector] = joblib.load(scaler_path)
                self.role_encoders[sector] = joblib.load(encoder_path)
                with open(features_path) as f:
                    self.role_features[sector] = json.load(f)
                print(f"  Loaded role model for: {sector}")
            else:
                print(f"  Warning: No role model found for {sector}")

    def load_all(self):
        """Load all artifacts"""
        print("Loading sector model...")
        self.load_sector_artifacts()
        print("Loading role models...")
        self.load_role_artifacts()

    def prepare_features(self, input_features: Dict[str, Any]) -> np.ndarray:
        """Prepare feature vector for sector prediction"""
        feature_vector = []
        for feat in self.sector_features:
            feature_vector.append(input_features.get(feat, 0))
        return np.array(feature_vector).reshape(1, -1)

    def predict_sector(self, features: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """Predict sector with probabilities"""
        X_scaled = self.sector_scaler.transform(features)
        probs = self.sector_model.predict_proba(X_scaled)[0]
        pred_idx = np.argmax(probs)
        sector = self.sector_encoder.classes_[pred_idx]
        confidence = probs[pred_idx]

        all_probs = dict(zip(self.sector_encoder.classes_, probs))

        return sector, float(confidence), all_probs

    def predict_role(self, sector: str, features: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """Predict role within sector"""
        if sector not in self.role_models:
            # Single-role sector
            if sector in self.single_role_sectors:
                return self.single_role_sectors[sector], 1.0, {self.single_role_sectors[sector]: 1.0}
            return "Unknown", 0.0, {}

        model = self.role_models[sector]
        scaler = self.role_scalers[sector]
        encoder = self.role_encoders[sector]

        sector_feats = self.role_features[sector]
        feature_vector = []
        for feat in sector_feats:
            if feat in self.sector_features:
                idx = self.sector_features.index(feat)
                feature_vector.append(features[0, idx])
            else:
                feature_vector.append(0)

        X_scaled = scaler.transform(np.array(feature_vector).reshape(1, -1))
        probs = model.predict_proba(X_scaled)[0]
        pred_idx = np.argmax(probs)
        role = encoder.classes_[pred_idx]
        confidence = probs[pred_idx]

        all_probs = dict(zip(encoder.classes_, probs))

        return role, float(confidence), all_probs

    def predict(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Full hierarchical prediction: Sector -> Role"""
        features = self.prepare_features(input_features)

        # Stage 1: Predict sector
        sector, sector_conf, sector_probs = self.predict_sector(features)

        # Stage 2: Predict role within sector (if confident enough)
        if sector_conf >= self.confidence_threshold:
            role, role_conf, role_probs = self.predict_role(sector, features)
        else:
            role = f"Uncertain ({sector})"
            role_conf = sector_conf
            role_probs = {}

        return {
            "sector": sector,
            "sector_confidence": sector_conf,
            "sector_probabilities": sector_probs,
            "role": role,
            "role_confidence": role_conf,
            "role_probabilities": role_probs,
            "hierarchical": True,
            "confidence_threshold": self.confidence_threshold
        }

    def predict_batch(self, feature_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch prediction"""
        return [self.predict(f) for f in feature_list]


def evaluate_hierarchical_v2(
    dataset_path: str,
    sector_model_dir: str = "backend/ml/saved_models_sector_v2",
    role_model_dir: str = "backend/ml/saved_models_roles_v2"
) -> Dict[str, Any]:
    """Evaluate hierarchical model V2 on test set"""
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)

    from sklearn.model_selection import train_test_split
    X = df.drop(columns=["career_label", "sector_label"])
    y_career = df["career_label"]
    y_sector = df["sector_label"]

    _, X_test, _, y_career_test, _, y_sector_test = train_test_split(
        X, y_career, y_sector, test_size=0.2, random_state=42, stratify=y_sector
    )

    print(f"Test set: {len(X_test)} samples")

    predictor = HierarchicalPredictorV2(sector_model_dir, role_model_dir)
    predictor.load_all()

    sector_correct = 0
    role_correct = 0
    sector_total = 0
    role_total = 0

    results = []
    for idx, row in X_test.iterrows():
        features = row.to_dict()
        true_career = y_career_test.loc[idx]
        true_sector = y_sector_test.loc[idx]

        pred = predictor.predict(features)

        if pred["sector"] == true_sector:
            sector_correct += 1
        sector_total += 1

        # Role accuracy
        if true_sector in predictor.sectors_with_roles:
            if pred["role"] == true_career:
                role_correct += 1
            role_total += 1
        elif true_sector in predictor.single_role_sectors:
            if pred["role"] == true_career:
                role_correct += 1
            role_total += 1

        results.append({
            "true_sector": true_sector,
            "pred_sector": pred["sector"],
            "true_career": true_career,
            "pred_role": pred["role"],
            "sector_conf": pred["sector_confidence"],
            "role_conf": pred["role_confidence"]
        })

    sector_acc = sector_correct / sector_total if sector_total > 0 else 0
    role_acc = role_correct / role_total if role_total > 0 else 0

    print(f"\n=== HIERARCHICAL V2 EVALUATION ===")
    print(f"Sector Accuracy: {sector_acc:.4f} ({sector_correct}/{sector_total})")
    print(f"Role Accuracy (conditional): {role_acc:.4f} ({role_correct}/{role_total})")

    print("\nPer-sector breakdown:")
    for sector in SECTORS_V2:
        sector_results = [r for r in results if r["true_sector"] == sector]
        if not sector_results:
            continue
        sector_hits = sum(1 for r in sector_results if r["pred_sector"] == sector)
        role_hits = sum(1 for r in sector_results if r["pred_role"] == r["true_career"])
        print(f"  {sector}: Sector {sector_hits}/{len(sector_results)}, Role {role_hits}/{len(sector_results)}")

    return {
        "sector_accuracy": sector_acc,
        "role_accuracy": role_acc,
        "sector_correct": sector_correct,
        "sector_total": sector_total,
        "role_correct": role_correct,
        "role_total": role_total,
        "detailed_results": results
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Hierarchical Predictor V2")
    parser.add_argument("--data", default="matrix_dataset_hierarchical_v2.csv", help="Dataset path")
    parser.add_argument("--sector-model", default="backend/ml/saved_models_sector_v2", help="Sector model dir")
    parser.add_argument("--role-model", default="backend/ml/saved_models_roles_v2", help="Role model dir")
    parser.add_argument("--threshold", type=float, default=0.4, help="Confidence threshold")
    args = parser.parse_args()

    evaluate_hierarchical_v2(args.data, args.sector_model, args.role_model)