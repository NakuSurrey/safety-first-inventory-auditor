"""
Verify the trained model works by running it on test images.

WHAT THIS SCRIPT DOES:
  1. Loads the trained best.pt model (easier to verify with PyTorch than TFLite)
  2. Picks a few random images from the test set
  3. Runs detection on each image
  4. Prints what it detected (class name, confidence score, bounding box)
  5. Saves annotated images (with bounding boxes drawn) to models/verify_output/

BEFORE RUNNING:
  Run train.py first. This script needs the best.pt file it produces.
"""

import random
from pathlib import Path
from ultralytics import YOLO

# ── Configuration ─────────────────────────────────────────────────────────

MODELS_DIR = Path("models")
BEST_WEIGHTS = MODELS_DIR / "runs" / "detect" / "ppe_model" / "weights" / "best.pt"
TEST_IMAGES_DIR = MODELS_DIR / "dataset" / "test" / "images"
OUTPUT_DIR = MODELS_DIR / "verify_output"
NUM_TEST_IMAGES = 5
CONFIDENCE_THRESHOLD = 0.5

# Class names (must match data.yaml)
CLASS_NAMES = {0: "Hardhat", 1: "Safety-Vest", 2: "Person"}

# ── Verification ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PHASE 4 — Model Verification")
    print("=" * 60)
    print("")

    # Check files exist
    if not BEST_WEIGHTS.exists():
        print(f"ERROR: {BEST_WEIGHTS} not found. Run train.py first.")
        return

    if not TEST_IMAGES_DIR.exists():
        print(f"ERROR: {TEST_IMAGES_DIR} not found. Run download_dataset.py first.")
        return

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load model
    model = YOLO(str(BEST_WEIGHTS))

    # Get test images
    image_files = list(TEST_IMAGES_DIR.glob("*.*"))
    image_files = [f for f in image_files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}]

    if not image_files:
        print("ERROR: No images found in test directory.")
        return

    # Pick random sample
    sample_size = min(NUM_TEST_IMAGES, len(image_files))
    test_images = random.sample(image_files, sample_size)

    print(f"Testing on {sample_size} random images from test set...")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print("")

    total_detections = 0

    for i, img_path in enumerate(test_images, 1):
        print(f"─── Image {i}/{sample_size}: {img_path.name} ───")

        # Run detection
        results = model.predict(
            source=str(img_path),
            conf=CONFIDENCE_THRESHOLD,
            save=True,
            project=str(OUTPUT_DIR),
            name="predictions",
            exist_ok=True,
        )

        # Parse results
        result = results[0]
        boxes = result.boxes

        if len(boxes) == 0:
            print("  No detections above confidence threshold.")
        else:
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                coords = box.xyxy[0].tolist()
                cls_name = CLASS_NAMES.get(cls_id, f"unknown({cls_id})")

                print(f"  Detected: {cls_name}")
                print(f"    Confidence: {conf:.2%}")
                print(f"    Box: ({coords[0]:.0f}, {coords[1]:.0f}) → ({coords[2]:.0f}, {coords[3]:.0f})")

                total_detections += 1

        print("")

    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Images tested:    {sample_size}")
    print(f"Total detections: {total_detections}")
    print(f"Annotated images saved to: {OUTPUT_DIR / 'predictions'}")
    print("")

    if total_detections > 0:
        print("Model is detecting objects. Ready for export.")
        print("NEXT STEP: Run export.py to convert to TFLite format.")
    else:
        print("WARNING: No detections found. Possible issues:")
        print("  1. Model needs more training epochs")
        print("  2. Confidence threshold too high (try lowering to 0.25)")
        print("  3. Test images may not contain target objects after filtering")


if __name__ == "__main__":
    main()
