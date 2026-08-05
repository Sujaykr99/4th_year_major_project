"""Quick test training on roo_data.csv - single model, small sample."""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib
import warnings
warnings.filterwarnings("ignore")

# Load data
df = pd.read_csv(r"C:/Users/DELL/Downloads/roo_data.csv")
print(f"Loaded: {df.shape}")

# Sample 5000 stratified
from sklearn.model_selection import train_test_split
df, _ = train_test_split(df, train_size=5000, random_state=42, stratify=df["Suggested Job Role"])
df = df.reset_index(drop=True)
print(f"Sampled: {df.shape}")

# Target
y = df["Suggested Job Role"]
X = df.drop(columns=["Suggested Job Role"])

# Encode categorical
cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
num_cols = X.select_dtypes(include=[np.number]).columns.tolist()

encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    encoders[col] = le

# Scale numeric
scaler = StandardScaler()
X[num_cols] = scaler.fit_transform(X[num_cols])

# Encode target
target_encoder = LabelEncoder()
y_enc = target_encoder.fit_transform(y)

print(f"Classes: {len(target_encoder.classes_)}")
print(f"Features: {X.shape[1]}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

# Train RandomForest (fast)
print("Training RandomForest...")
rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# Evaluate
y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="weighted")

print(f"\n=== RESULTS ===")
print(f"Accuracy: {acc:.4f}")
print(f"F1 Score (weighted): {f1:.4f}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_, zero_division=0))

# Per-class F1
from sklearn.metrics import f1_score
f1_per_class = f1_score(y_test, y_pred, average=None)
for i, cls in enumerate(target_encoder.classes_):
    print(f"  {cls}: F1={f1_per_class[i]:.4f}")

# Save quick model
joblib.dump(rf, "quick_roo_model.pkl")
joblib.dump(scaler, "quick_roo_scaler.pkl")
joblib.dump(encoders, "quick_roo_encoders.pkl")
joblib.dump(target_encoder, "quick_roo_target_encoder.pkl")
print("\nSaved quick artifacts")