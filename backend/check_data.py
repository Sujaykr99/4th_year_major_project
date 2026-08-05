import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import OrdinalEncoder

# 1. Load the dataset
df = pd.read_csv("backend/data/matrix_dataset_v3_clean.csv")

# 2. Separate features and target
X = df.drop(columns=["Suggested Job Role"])
y = df["Suggested Job Role"]

# 3. Quickly encode object columns to numbers for the test
for col in X.select_dtypes(include=["object"]).columns:
    X[col] = OrdinalEncoder().fit_transform(X[[col]].astype(str))

# 4. Calculate Mutual Information Scores
mi_scores = mutual_info_classif(X, y, random_state=42)
mi_df = pd.DataFrame({"Feature": X.columns, "MI Score": mi_scores})
mi_df = mi_df.sort_values(by="MI Score", ascending=False)

print("--- Mutual Information Scores ---")
print(mi_df.to_string(index=False))