#!/usr/bin/env python3
"""
Stack Overflow 2024 Developer Survey Preprocessing - HIERARCHICAL V2
Redesigned sectors based on actual skill similarity:
1. Web Development (Frontend + Full Stack + UI/UX) - JavaScript/React/TypeScript ecosystem
2. Backend & Data Engineering (Backend + Database) - SQL/PostgreSQL/Python ecosystem
3. Mobile Development (Mobile App Developer) - Firebase/SQLite/Java/Kotlin
4. Cloud & DevOps (DevOps + Cloud Engineer) - Python/Terraform/Ansible/AWS
5. Security & Infrastructure (Cyber Security + Network Engineer) - Python/SQL/Scripting
6. Technical Leadership & Specialized (Engineering Manager + QA) - Mixed technical skills
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

CAREER_MAPPING = {
    "Developer, back-end": "Backend Developer",
    "Developer, front-end": "Frontend Developer",
    "Developer, full-stack": "Full Stack Developer",
    "Developer, mobile": "Mobile App Developer",
    "Data scientist or ML specialist": "Data Scientist",
    "Machine learning specialist": "AI/ML Engineer",
    "DevOps specialist": "DevOps Engineer",
    "Cloud infrastructure engineer": "Cloud Engineer",
    "Security professional": "Cyber Security Engineer",
    "System administrator": "Network Engineer",
    "Database administrator": "Database Engineer",
    "Designer": "UI/UX Designer",
    "QA or test developer": "QA Engineer",
    "Engineering manager": "Engineering Manager",
    "Developer, embedded": "Embedded Engineer",
}

# ============================================================
# REDESIGNED SECTOR MAPPING (6 Sectors based on skill similarity)
# ============================================================

SECTOR_MAPPING_V2 = {
    # Sector 1: Web Development (JavaScript/React/TypeScript ecosystem)
    "Frontend Developer": "Web Development",
    "Full Stack Developer": "Web Development",
    "UI/UX Designer": "Web Development",

    # Sector 2: Backend & Data Engineering (SQL/PostgreSQL/Python ecosystem)
    "Backend Developer": "Backend & Data Engineering",
    "Database Engineer": "Backend & Data Engineering",

    # Sector 3: Mobile Development
    "Mobile App Developer": "Mobile Development",

    # Sector 4: Cloud & DevOps (Python/Cloud/Automation ecosystem)
    "DevOps Engineer": "Cloud & DevOps",
    "Cloud Engineer": "Cloud & DevOps",

    # Sector 5: Security & Infrastructure (Python/SQL/Scripting)
    "Cyber Security Engineer": "Security & Infrastructure",
    "Network Engineer": "Security & Infrastructure",

    # Sector 6: Technical Leadership & Specialized
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

SKILL_COLUMNS = {
    "LanguageHaveWorkedWith": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#",
        "Go", "Rust", "SQL", "R", "PHP", "Swift", "Kotlin", "Ruby"
    ],
    "WebframeHaveWorkedWith": [
        "React", "Node.js", "Vue.js", "Angular", "Django", "Flask",
        "FastAPI", "Spring", "Express", "ASP.NET Core", "Next.js"
    ],
    "DatabaseHaveWorkedWith": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
        "Microsoft SQL Server", "Oracle", "Elasticsearch", "DynamoDB"
    ],
    "PlatformHaveWorkedWith": [
        "AWS", "Google Cloud", "Microsoft Azure", "Docker", "Kubernetes",
        "Linux", "Heroku", "Vercel", "Firebase"
    ],
    "ToolsTechHaveWorkedWith": [
        "Git", "GitHub Actions", "GitLab CI/CD", "Jenkins",
        "Terraform", "Ansible", "npm", "yarn", "Webpack", "Vite"
    ],
}

TARGET_COLUMN = "DevType"

FILTER_COLUMNS = [
    "ResponseId", "MainBranch", "EdLevel", "YearsCode", "YearsCodePro",
    "DevType", "WorkExp", "RemoteWork", "Country",
    "LanguageHaveWorkedWith", "DatabaseHaveWorkedWith",
    "WebframeHaveWorkedWith", "PlatformHaveWorkedWith", "ToolsTechHaveWorkedWith"
]


# ============================================================
# HELPER FUNCTIONS (same as before)
# ============================================================

def parse_multi_select(value: str, options: list) -> dict:
    if pd.isna(value) or value == "":
        return {opt: 0 for opt in options}
    selected = set(str(value).split(";"))
    return {opt: 1 if opt in selected else 0 for opt in options}


def map_devtype_to_career(devtype_str: str) -> str:
    if pd.isna(devtype_str):
        return "Other"
    types = [t.strip() for t in str(devtype_str).split(";")]
    for t in types:
        if t in CAREER_MAPPING:
            return CAREER_MAPPING[t]
    return "Other"


def map_career_to_sector_v2(career: str) -> str:
    return SECTOR_MAPPING_V2.get(career, "Other")


def parse_years(val):
    if pd.isna(val):
        return 0
    s = str(val).lower()
    if "less than a year" in s:
        return 0.5
    try:
        return float(s.split()[0])
    except:
        return 0


def parse_ed_level(val):
    if pd.isna(val):
        return 0
    s = str(val).lower()
    if "doctoral" in s or "phd" in s:
        return 5
    elif "master" in s:
        return 4
    elif "bachelor" in s:
        return 3
    elif "associate" in s:
        return 2
    elif "some college" in s or "secondary" in s:
        return 1
    else:
        return 0


def parse_work_exp(val):
    if pd.isna(val):
        return 0
    exp_list = [w.strip().lower() for w in str(val).split(";")]
    count = 0
    for w in exp_list:
        if any(k in w for k in ["intern", "full-time", "part-time", "freelance", "contract", "self-employed"]):
            count += 1
    return min(count, 5)


def filter_student_early_career(df: pd.DataFrame) -> pd.DataFrame:
    ed_mask = df["EdLevel"].astype(str).str.contains(
        "Bachelor|Master|Some college|Secondary school|Doctoral|Associate", case=False, na=False
    )
    years_pro = df["YearsCodePro"].apply(parse_years)
    exp_mask = years_pro <= 5
    branch_mask = df["MainBranch"].astype(str).str.contains(
        "developer|student|learning", case=False, na=False
    )
    filtered = df[ed_mask & exp_mask & branch_mask].copy()
    print(f"Filtered: {len(df)} -> {len(filtered)} rows")
    return filtered


def extract_binary_skill_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)
    for col_name, skills in SKILL_COLUMNS.items():
        if col_name not in df.columns:
            print(f"Warning: {col_name} not in dataset")
            for skill in skills:
                feat_name = f"skill_{skill.lower().replace('.', '').replace(' ', '_').replace('+', 'p')}"
                features[feat_name] = 0
            continue
        print(f"Processing {col_name}...")
        parsed = df[col_name].apply(lambda x: parse_multi_select(x, skills))
        parsed_df = pd.DataFrame(parsed.tolist(), index=df.index)
        for skill in skills:
            feat_name = f"skill_{skill.lower().replace('.', '').replace(' ', '_').replace('+', 'p')}"
            features[feat_name] = parsed_df[skill].astype(int)
    return features


def add_experience_education_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)
    features["years_code_pro"] = df["YearsCodePro"].apply(parse_years)
    features["years_code"] = df["YearsCode"].apply(parse_years)
    features["ed_level"] = df["EdLevel"].apply(parse_ed_level)
    features["work_exp_count"] = df["WorkExp"].apply(parse_work_exp)
    features["is_developer"] = df["MainBranch"].astype(str).str.contains(
        "developer", case=False, na=False
    ).astype(int)
    def map_remote(val):
        if pd.isna(val):
            return 1
        s = str(val).lower()
        if "fully remote" in s:
            return 2
        elif "hybrid" in s:
            return 1
        else:
            return 0
    features["remote_pref"] = df["RemoteWork"].apply(map_remote)
    return features


def add_composite_features(skill_features: pd.DataFrame) -> pd.DataFrame:
    features = skill_features.copy()
    web_skills = [c for c in features.columns if c.startswith("skill_") and any(k in c for k in
        ["react", "vue", "angular", "nodejs", "javascript", "typescript", "express", "nextjs", "django", "flask", "fastapi", "spring"])]
    if web_skills:
        features["web_score"] = features[web_skills].sum(axis=1)
    cloud_skills = [c for c in features.columns if c.startswith("skill_") and any(k in c for k in
        ["aws", "google_cloud", "microsoft_azure", "docker", "kubernetes", "linux", "terraform", "ansible", "jenkins", "github_actions", "gitlab_ci"])]
    if cloud_skills:
        features["cloud_score"] = features[cloud_skills].sum(axis=1)
    data_skills = [c for c in features.columns if c.startswith("skill_") and any(k in c for k in
        ["python", "r_", "sql", "postgresql", "mysql", "mongodb", "redis", "sqlite", "elasticsearch", "dynamodb"])]
    if data_skills:
        features["data_score"] = features[data_skills].sum(axis=1)
    mobile_skills = [c for c in features.columns if c.startswith("skill_") and any(k in c for k in
        ["swift", "kotlin", "flutter", "react_native", "dart"])]
    if mobile_skills:
        features["mobile_score"] = features[mobile_skills].sum(axis=1)
    backend_skills = [c for c in features.columns if c.startswith("skill_") and any(k in c for k in
        ["nodejs", "express", "django", "flask", "fastapi", "spring", "aspnet_core", "sql", "postgresql", "mysql", "mongodb", "redis"])]
    if backend_skills:
        features["backend_score"] = features[backend_skills].sum(axis=1)
    skill_cols = [c for c in features.columns if c.startswith("skill_")]
    features["total_skills"] = features[skill_cols].sum(axis=1)
    lang_cols = [c for c in features.columns if c.startswith("skill_") and any(l in c for l in
        ["python", "java", "javascript", "typescript", "cpp", "c#", "go", "rust", "php", "swift", "kotlin", "ruby"])]
    features["language_diversity"] = (features[lang_cols] > 0).sum(axis=1)
    return features


# ============================================================
# MAIN PREPROCESSING PIPELINE
# ============================================================

def preprocess_stackoverflow_hierarchical_v2(input_path: str, output_path: str) -> dict:
    print(f"Loading {input_path}...")
    df = pd.read_csv(input_path, low_memory=False, usecols=lambda c: c in FILTER_COLUMNS or c == TARGET_COLUMN)
    print(f"Loaded: {df.shape}")

    df = filter_student_early_career(df)

    df["career_label"] = df[TARGET_COLUMN].apply(map_devtype_to_career)
    df["sector_label"] = df["career_label"].apply(map_career_to_sector_v2)

    valid_careers = set(CAREER_MAPPING.values())
    df = df[df["career_label"].isin(valid_careers)].copy()
    print(f"After career filtering: {len(df)} rows")
    print(f"Career distribution:\n{df['career_label'].value_counts()}")
    print(f"\nSector distribution (V2):\n{df['sector_label'].value_counts()}")

    print("Extracting binary skill features...")
    skill_features = extract_binary_skill_features(df)

    print("Adding experience/education features...")
    exp_ed_features = add_experience_education_features(df)

    print("Adding composite skill cluster features...")
    skill_features = add_composite_features(skill_features)

    all_features = pd.concat([skill_features, exp_ed_features], axis=1)

    final_df = pd.concat([all_features, df[["career_label", "sector_label"]]], axis=1)

    print(f"\nFinal: {final_df.shape[0]} samples, {len(all_features.columns)} features")
    print(f"Career classes: {final_df['career_label'].nunique()}")
    print(f"Sector classes: {final_df['sector_label'].nunique()}")
    print(f"Sector distribution:\n{final_df['sector_label'].value_counts()}")

    final_df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")

    return {
        "n_samples": len(final_df),
        "n_features": len(all_features.columns),
        "n_career_classes": final_df["career_label"].nunique(),
        "n_sector_classes": final_df["sector_label"].nunique(),
        "career_distribution": final_df["career_label"].value_counts().to_dict(),
        "sector_distribution": final_df["sector_label"].value_counts().to_dict(),
        "feature_columns": all_features.columns.tolist(),
        "career_target": "career_label",
        "sector_target": "sector_label",
        "sectors": SECTORS_V2,
        "career_to_sector": SECTOR_MAPPING_V2,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Preprocess Stack Overflow 2024 Survey - HIERARCHICAL V2")
    parser.add_argument("--input", default="survey_results_public.csv", help="Input CSV path")
    parser.add_argument("--output", default="matrix_dataset_hierarchical_v2.csv", help="Output CSV path")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        exit(1)

    metadata = preprocess_stackoverflow_hierarchical_v2(str(input_path), args.output)

    with open("so_preprocess_hierarchical_v2_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("\nHierarchical V2 preprocessing complete!")
    print(f"Output: {args.output}")