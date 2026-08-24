#!/usr/bin/env python3
"""
Download Stack Overflow Developer Survey 2024 from Kaggle.
Run this script after placing kaggle.json in ~/.kaggle/
"""
import os
import json
import zipfile
from pathlib import Path

def setup_kaggle_credentials(username: str, key: str):
    """Create kaggle.json in the correct location."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)

    kaggle_json = kaggle_dir / "kaggle.json"
    credentials = {"username": username, "key": key}

    with open(kaggle_json, "w") as f:
        json.dump(credentials, f)

    # Set permissions (Unix-like)
    try:
        kaggle_json.chmod(0o600)
    except:
        pass  # Windows ignores this

    print(f"[OK] Created {kaggle_json}")
    return kaggle_json

def download_dataset():
    """Download using kaggle CLI via subprocess."""
    import subprocess

    # Change to project directory
    project_dir = Path.cwd()

    print("Downloading Stack Overflow Developer Survey 2024...")
    result = subprocess.run(
        ["kaggle", "datasets", "download", "stackoverflow/developer-survey-2024"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] Download failed: {result.stderr}")
        return False

    print("[OK] Download complete")
    return True

def unzip_dataset():
    """Unzip the downloaded file."""
    project_dir = Path.cwd()
    zip_files = list(project_dir.glob("developer-survey-2024*.zip"))

    if not zip_files:
        print("[ERROR] No zip file found")
        return False

    zip_path = zip_files[0]
    print(f"Unzipping {zip_path.name}...")

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(project_dir)

    print("[OK] Unzipped:")
    for f in project_dir.glob("*.csv"):
        print(f"  - {f.name} ({f.stat().st_size / 1e6:.1f} MB)")

    return True

def main():
    # Load credentials from environment variables or config file
    import os
    USERNAME = os.environ.get("KAGGLE_USERNAME")
    KEY = os.environ.get("KAGGLE_KEY")

    if not USERNAME or not KEY:
        # Fallback: read from config file
        config_path = Path.home() / ".kaggle" / "credentials.json"
        if config_path.exists():
            with open(config_path) as f:
                creds = json.load(f)
                USERNAME = creds.get("username")
                KEY = creds.get("key")

    if not USERNAME or not KEY:
        print("[ERROR] Kaggle credentials not found.")
        print("Set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
        print("Or create ~/.kaggle/credentials.json with username and key")
        return

    print("=" * 50)
    print("Stack Overflow 2024 Dataset Downloader")
    print("=" * 50)

    # Step 1: Setup credentials
    setup_kaggle_credentials(USERNAME, KEY)

    # Step 2: Install kaggle if needed
    import subprocess
    result = subprocess.run(["pip", "install", "kaggle"], capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] kaggle CLI installed/updated")
    else:
        print(f"Note: {result.stderr}")

    # Step 3: Download
    if not download_dataset():
        return

    # Step 4: Unzip
    if not unzip_dataset():
        return

    print("\n[OK] Done! Next: Run preprocessing pipeline")

if __name__ == "__main__":
    main()