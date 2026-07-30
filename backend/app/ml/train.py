#!/usr/bin/env python3
"""Train ML model for career prediction."""
import argparse
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.pipeline import run_training_pipeline


def main():
    parser = argparse.ArgumentParser(description="Train career prediction model")
    parser.add_argument("--data", required=True, help="Path to dataset CSV")
    parser.add_argument("--output", default="backend/ml/saved_models", help="Output directory for model artifacts")
    args = parser.parse_args()

    print(f"Training model with dataset: {args.data}")
    print(f"Output directory: {args.output}")

    result = run_training_pipeline(args.data, args.output)

    print("\n=== Training Complete ===")
    print(f"Best model: {result['best_model']}")
    print(f"Classes: {result['classes']}")
    print("\nModel Comparison:")
    for name, metrics in result['results'].items():
        print(f"  {name}: Acc={metrics['accuracy']:.4f}, F1={metrics['f1_score']:.4f}")


if __name__ == "__main__":
    main()