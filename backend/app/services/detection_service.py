"""
Detection service — loads the YOLO model and runs inference on uploaded images.

WHAT THIS FILE DOES:
  1. Loads the trained YOLOv8-nano model (best.pt) once when the server starts
  2. When an image is uploaded, runs the model on that image
  3. Returns a list of detections: class name, confidence score, bounding box

WHY SERVER-SIDE:
  The mobile app is an Expo web app running in a browser.
  Browsers cannot load .pt files directly.
  So the phone sends the photo to the server, the server runs YOLO,
  and sends back the results as JSON.

CONNECTION:
  - Loaded by detect.py route when POST /api/detect is called
  - Uses MODEL_CONFIDENCE_THRESHOLD from config.py (.env)
  - The 3 class names must match what the model was trained on (data.yaml)
"""

import logging
from pathlib import Path
from typing import Optional

from ultralytics import YOLO

from backend.app.core.config import settings

logger = logging.getLogger("safety_auditor.detection")

# ── Class names — must match data.yaml from Phase 4 training ─────────────
CLASS_NAMES = {0: "Hardhat", 1: "Safety-Vest", 2: "Person"}

# ── Model loading ────────────────────────────────────────────────────────
# The model is loaded ONCE when this module is first imported.
# Every request reuses the same loaded model — no reloading per request.
# This is critical for performance: loading takes ~2-3 seconds,
# but inference on a loaded model takes ~0.1-0.5 seconds.

_model: Optional[YOLO] = None


def _get_model() -> YOLO:
    """Load the YOLO model if not already loaded. Returns the cached model."""
    global _model

    if _model is not None:
        return _model

    # Look for best.pt (PyTorch format) — faster inference than TFLite on server
    model_path = Path("models") / "runs" / "detect" / "ppe_model" / "weights" / "best.pt"

    if not model_path.exists():
        # Fallback: try the TFLite file
        model_path = Path(settings.model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"No model file found. Checked:\n"
            f"  1. models/runs/detect/ppe_model/weights/best.pt\n"
            f"  2. {settings.model_path}\n"
            f"Run train.py first to create the model."
        )

    logger.info(f"Loading YOLO model from: {model_path}")
    _model = YOLO(str(model_path))
    logger.info("YOLO model loaded successfully")

    return _model


# ── Detection ────────────────────────────────────────────────────────────


def detect_objects(image_path: str) -> list[dict]:
    """
    Run YOLO detection on a single image.

    Args:
        image_path: path to the image file on disk

    Returns:
        List of detection dicts, each containing:
          - class_name: str ("Hardhat", "Safety-Vest", or "Person")
          - class_id: int (0, 1, or 2)
          - confidence: float (0.0 to 1.0)
          - bbox: dict with x1, y1, x2, y2 (pixel coordinates of bounding box)
    """
    model = _get_model()

    # Run inference
    results = model.predict(
        source=image_path,
        conf=settings.model_confidence_threshold,
        verbose=False,  # Do not print to console on every request
    )

    # Parse results into a clean list of dicts
    detections = []

    if results and len(results) > 0:
        result = results[0]
        boxes = result.boxes

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

            detections.append({
                "class_name": CLASS_NAMES.get(cls_id, f"unknown({cls_id})"),
                "class_id": cls_id,
                "confidence": round(conf, 4),
                "bbox": {
                    "x1": round(coords[0], 1),
                    "y1": round(coords[1], 1),
                    "x2": round(coords[2], 1),
                    "y2": round(coords[3], 1),
                },
            })

    logger.info(f"Detection complete: {len(detections)} objects found")
    return detections
