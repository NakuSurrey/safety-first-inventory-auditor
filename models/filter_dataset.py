"""
Filter the downloaded dataset to keep only our target classes.

The Roboflow dataset (v30) has 25 classes:
  0: Excavator, 1: Gloves, 2: Hardhat, 3: Ladder, 4: Mask,
  5: NO-Hardhat, 6: NO-Mask, 7: NO-Safety Vest, 8: Person,
  9: SUV, 10: Safety Cone, 11: Safety Vest, 12: bus, 13: dump truck,
  14: fire hydrant, 15: machinery, 16: mini-van, 17: sedan, 18: semi,
  19: trailer, 20: truck and trailer, 21: truck, 22: van, 23: vehicle,
  24: wheel loader

We only want 3 classes for our project:
  0: Hardhat
  1: Safety-Vest
  2: Person

This script:
  1. Reads every label .txt file in train/, valid/, test/
  2. Keeps only lines where the class_id is 2 (Hardhat), 11 (Safety Vest), or 8 (Person)
  3. Remaps old class IDs to new ones:
       old 2  (Hardhat)     → new 0
       old 11 (Safety Vest) → new 1
       old 8  (Person)      → new 2
  4. Overwrites the label file with only the filtered lines
  5. Deletes any images that have zero remaining labels (no target objects in them)
"""

import os
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────

DATASET_DIR = Path(__file__).resolve().parent / "dataset"

# Mapping: old_class_id → new_class_id
# Only classes in this dict are kept. Everything else is discarded.
CLASS_MAP = {
    2: 0,    # Hardhat     → 0
    11: 1,   # Safety Vest → 1
    8: 2,    # Person      → 2
}

# ── Processing ────────────────────────────────────────────────────────────

def filter_labels(split_name: str) -> dict:
    """
    Filter label files for one split (train, valid, or test).
    Returns a dict with counts of images kept and removed.
    """
    labels_dir = DATASET_DIR / split_name / "labels"
    images_dir = DATASET_DIR / split_name / "images"

    if not labels_dir.exists():
        print(f"  WARNING: {labels_dir} does not exist. Skipping.")
        return {"kept": 0, "removed": 0}

    kept = 0
    removed = 0

    for label_file in sorted(labels_dir.glob("*.txt")):
        new_lines = []

        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue

                old_class_id = int(parts[0])

                if old_class_id in CLASS_MAP:
                    new_class_id = CLASS_MAP[old_class_id]
                    parts[0] = str(new_class_id)
                    new_lines.append(" ".join(parts))

        if new_lines:
            # Overwrite with filtered lines
            with open(label_file, "w") as f:
                f.write("\n".join(new_lines) + "\n")
            kept += 1
        else:
            # No target objects found — delete label AND matching image
            label_file.unlink()

            # Find and delete matching image (could be .jpg, .jpeg, .png)
            stem = label_file.stem
            for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
                img_path = images_dir / (stem + ext)
                if img_path.exists():
                    img_path.unlink()
                    break

            removed += 1

    return {"kept": kept, "removed": removed}


# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Filtering dataset to keep only: Hardhat (0), Safety Vest (1), Person (2)")
    print(f"Dataset location: {DATASET_DIR}")
    print("")

    total_kept = 0
    total_removed = 0

    for split in ["train", "valid", "test"]:
        print(f"Processing {split}/...")
        result = filter_labels(split)
        total_kept += result["kept"]
        total_removed += result["removed"]
        print(f"  Kept: {result['kept']} images")
        print(f"  Removed: {result['removed']} images (no target objects)")
        print("")

    print(f"TOTAL: {total_kept} images kept, {total_removed} images removed")
    print("")
    print("Class mapping after filtering:")
    print("  0 → Hardhat")
    print("  1 → Safety-Vest")
    print("  2 → Person")
