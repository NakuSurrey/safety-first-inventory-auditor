"""
Train a YOLOv8-nano model on our filtered PPE dataset.

WHAT THIS SCRIPT DOES:
  1. Loads the pre-trained YOLOv8-nano base model (yolov8n.pt)
     — this model already knows how to detect generic objects (80 classes)
     — we are re-training it to detect only OUR 3 classes
  2. Trains it on our dataset for a set number of epochs
     — an epoch is one complete pass through all training images
  3. Saves the trained weights to: runs/detect/ppe_model/weights/best.pt

BEFORE RUNNING:
  1. Run download_dataset.py first (to get the images)
  2. Run filter_dataset.py second (to keep only our 3 classes)
  3. Then run this script: python train.py

HARDWARE NOTE:
  - With a GPU (NVIDIA): training takes ~30-60 minutes
  - Without a GPU (CPU only): training takes ~3-6 hours
  - YOLOv8 auto-detects your hardware and uses the best available
"""

from pathlib import Path
from ultralytics import YOLO

# ── Configuration ─────────────────────────────────────────────────────────

DATA_YAML = str(Path(__file__).resolve().parent / "dataset" / "data.yaml")

# Training hyperparameters
EPOCHS = 50           # How many times to loop through all training images
BATCH_SIZE = 16       # How many images to process at once before updating weights
IMAGE_SIZE = 640      # Resize all images to 640x640 pixels for training
MODEL_NAME = "yolov8n.pt"  # "n" = nano — the smallest, fastest YOLOv8 variant
PROJECT_NAME = str(Path(__file__).resolve().parent / "runs" / "detect")
EXPERIMENT_NAME = "ppe_model"

# ── Training ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("PHASE 4 — YOLOv8-nano Training")
    print("=" * 60)
    print(f"Base model:    {MODEL_NAME}")
    print(f"Dataset:       {DATA_YAML}")
    print(f"Epochs:        {EPOCHS}")
    print(f"Batch size:    {BATCH_SIZE}")
    print(f"Image size:    {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"Output:        {PROJECT_NAME}/{EXPERIMENT_NAME}/")
    print("=" * 60)
    print("")

    # Load the pre-trained YOLOv8-nano model
    model = YOLO(MODEL_NAME)

    # Train on our dataset
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMAGE_SIZE,
        project=PROJECT_NAME,
        name=EXPERIMENT_NAME,
        exist_ok=True,          # Overwrite previous run if it exists
        patience=10,            # Stop early if no improvement for 10 epochs
        save=True,              # Save checkpoints
        save_period=10,         # Save a checkpoint every 10 epochs
        plots=True,             # Generate training metric plots
        verbose=True,           # Show progress during training
    )

    # ── Report results ────────────────────────────────────────────────────

    best_weights = Path(PROJECT_NAME) / EXPERIMENT_NAME / "weights" / "best.pt"

    print("")
    print("=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Best weights saved to: {best_weights}")
    print("")
    print("Training metrics (from results):")

    if hasattr(results, "results_dict"):
        metrics = results.results_dict
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")

    print("")
    print("NEXT STEP: Run export.py to convert best.pt → TFLite format")
    print("  python export.py")


if __name__ == "__main__":
    main()
