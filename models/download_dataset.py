"""
Download the Construction Site Safety dataset from Roboflow.

This script downloads a pre-labelled PPE detection dataset in YOLOv8 format.
The dataset contains images of hard hats, safety vests, and other PPE items
with bounding box labels already drawn.

Dataset: Construction Site Safety by Roboflow Universe Projects
Source: https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety
Classes: Hardhat, Mask, NO-Hardhat, NO-Mask, NO-Safety Vest,
         Person, Safety Cone, Safety Vest, machinery, vehicle

BEFORE RUNNING:
1. Create a free Roboflow account at https://roboflow.com
2. Go to Settings > API Key > copy your private API key
3. Add this line to your .env file:
   ROBOFLOW_API_KEY=your_key_here
"""

import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# ── Load environment variables from .env ──────────────────────────────────
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")

if not ROBOFLOW_API_KEY:
    print("ERROR: ROBOFLOW_API_KEY not found in .env file.")
    print("")
    print("To fix this:")
    print("  1. Go to https://app.roboflow.com → Settings → API Key")
    print("  2. Copy your private API key")
    print("  3. Add this line to your .env file:")
    print("     ROBOFLOW_API_KEY=your_key_here")
    sys.exit(1)

# ── Clean up old download (Roboflow skips if data.yaml already exists) ───
DATASET_DIR = Path(__file__).resolve().parent / "dataset"

if DATASET_DIR.exists():
    print(f"Removing old dataset folder: {DATASET_DIR}")
    shutil.rmtree(DATASET_DIR)
    print("Old dataset removed.\n")

# ── Download dataset ──────────────────────────────────────────────────────
from roboflow import Roboflow

rf = Roboflow(api_key=ROBOFLOW_API_KEY)

project = rf.workspace("roboflow-universe-projects").project("construction-site-safety")

dataset = project.version(30).download("yolov8", location=str(DATASET_DIR))

# ── Verify download actually worked ──────────────────────────────────────
train_images = DATASET_DIR / "train" / "images"
valid_images = DATASET_DIR / "valid" / "images"

if not train_images.exists() or not any(train_images.iterdir()):
    print("")
    print("ERROR: Download appeared to succeed but no images were found!")
    print(f"Expected images at: {train_images}")
    print("")
    print("Possible causes:")
    print("  1. Your API key may not have access to this dataset")
    print("  2. The dataset version may have changed")
    print("  3. Roboflow may be rate-limiting your account")
    print("")
    print("Try downloading manually:")
    print("  1. Go to https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety/dataset/30")
    print("  2. Click 'Download Dataset' → Format: YOLOv8 → Download zip")
    print("  3. Unzip into models/dataset/ so you have models/dataset/train/, models/dataset/valid/, models/dataset/test/")
    sys.exit(1)

train_count = len(list(train_images.glob("*")))
valid_count = len(list(valid_images.glob("*"))) if valid_images.exists() else 0

print("")
print("Dataset downloaded and VERIFIED successfully!")
print(f"Location: {DATASET_DIR}")
print(f"Train images: {train_count}")
print(f"Valid images: {valid_count}")
print("")
print("Folder structure created:")
print("  dataset/")
print("  ├── train/")
print("  │   ├── images/   ← training images")
print("  │   └── labels/   ← training label .txt files")
print("  ├── valid/")
print("  │   ├── images/   ← validation images")
print("  │   └── labels/   ← validation label .txt files")
print("  └── test/")
print("      ├── images/   ← test images")
print("      └── labels/   ← test label .txt files")
