"""
Export the trained YOLOv8-nano model to TFLite format for mobile deployment.

WHAT THIS SCRIPT DOES:
  1. Loads the trained best.pt weights file (output of train.py)
  2. Converts it to TFLite format (TensorFlow Lite)
     — TFLite is a lightweight format designed to run on mobile phones
     — The model file goes from ~6MB (PyTorch) to ~4MB (TFLite)
  3. Copies the .tflite file to models/yolov8n_safety.tflite
     — This is the path our .env file (MODEL_PATH) already points to

BEFORE RUNNING:
  Run train.py first. This script needs the best.pt file it produces.

WHY TFLITE:
  PyTorch (.pt) files need the full PyTorch library to run (~500MB).
  TFLite (.tflite) files need only TensorFlow Lite runtime (~5MB).
  A mobile phone cannot install full PyTorch. It CAN run TFLite.
"""

import shutil
from pathlib import Path
from ultralytics import YOLO

# ── Configuration ─────────────────────────────────────────────────────────

MODELS_DIR = Path("models")
BEST_WEIGHTS = MODELS_DIR / "runs" / "detect" / "ppe_model" / "weights" / "best.pt"
OUTPUT_FILENAME = "yolov8n_safety.tflite"
FINAL_PATH = MODELS_DIR / OUTPUT_FILENAME

# ── Export ────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PHASE 4 — Export to TFLite")
    print("=" * 60)
    print(f"Input:  {BEST_WEIGHTS}")
    print(f"Output: {FINAL_PATH}")
    print("=" * 60)
    print("")

    # Check that training has been done
    if not BEST_WEIGHTS.exists():
        print(f"ERROR: {BEST_WEIGHTS} not found.")
        print("")
        print("You need to run train.py first:")
        print("  python train.py")
        return

    # Load the trained model
    model = YOLO(str(BEST_WEIGHTS))

    # Export to TFLite
    print("Exporting to TFLite format...")
    print("(This may take a few minutes and will download TensorFlow if needed)")
    print("")

    export_path = model.export(
        format="tflite",
        imgsz=640,
        half=False,         # Full precision (FP32) — more compatible with mobile
    )

    print("")
    print(f"TFLite model exported to: {export_path}")

    # Copy to the final location our .env expects
    # The export produces a file like: best_saved_model/best_float32.tflite
    # We need to find it and copy it to models/yolov8n_safety.tflite

    export_path = Path(str(export_path))

    # ultralytics may return a directory or a file path
    if export_path.is_dir():
        # Find the .tflite file inside the directory
        tflite_files = list(export_path.glob("*.tflite"))
        if tflite_files:
            source = tflite_files[0]
        else:
            print(f"ERROR: No .tflite file found in {export_path}")
            return
    elif export_path.suffix == ".tflite":
        source = export_path
    else:
        # Try appending common suffixes
        possible = export_path.with_suffix(".tflite")
        if possible.exists():
            source = possible
        else:
            # Search in parent directory
            tflite_files = list(export_path.parent.glob("*.tflite"))
            if tflite_files:
                source = tflite_files[0]
            else:
                print(f"ERROR: Could not locate .tflite file after export.")
                print(f"Check the export output directory: {export_path.parent}")
                return

    shutil.copy2(str(source), str(FINAL_PATH))

    # Verify the file exists and report size
    if FINAL_PATH.exists():
        size_mb = FINAL_PATH.stat().st_size / (1024 * 1024)
        print("")
        print("=" * 60)
        print("EXPORT COMPLETE")
        print("=" * 60)
        print(f"Final model: {FINAL_PATH}")
        print(f"File size:   {size_mb:.1f} MB")
        print("")
        print("This file is ready for mobile deployment.")
        print("The .env file MODEL_PATH already points to: ./models/yolov8n_safety.tflite")
    else:
        print(f"ERROR: Failed to copy model to {FINAL_PATH}")


if __name__ == "__main__":
    main()
