"""
Detection API route — the endpoint the mobile app calls to detect PPE in photos.

POST /api/detect
  - Receives an image file (multipart form upload)
  - Passes it to detection_service.py
  - Returns a list of detections as JSON

This is the bridge between the phone's camera and the YOLO model.
The phone cannot run YOLO directly (it is a web app in a browser).
So the phone sends the photo here, the server runs YOLO, and sends back results.
"""

import os
import uuid
import logging
import tempfile

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from backend.app.services.detection_service import detect_objects

logger = logging.getLogger("safety_auditor.detect")

router = APIRouter(prefix="/api/detect", tags=["Detection"])


# ── Response schema ──────────────────────────────────────────────────────

class BoundingBox(BaseModel):
    """Pixel coordinates of the detection bounding box."""
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionResult(BaseModel):
    """One detected object in the image."""
    class_name: str
    class_id: int
    confidence: float
    bbox: BoundingBox


class DetectResponse(BaseModel):
    """Full response from the detection endpoint."""
    detections: list[DetectionResult]
    count: int
    image_width: int = 0
    image_height: int = 0


# ── Endpoint ─────────────────────────────────────────────────────────────

@router.post("/", response_model=DetectResponse)
async def detect_from_image(file: UploadFile = File(...)):
    """
    Upload an image and get YOLO detection results.

    The mobile app sends a photo here. The server:
    1. Saves the photo to a temporary file
    2. Runs YOLOv8-nano detection on it
    3. Deletes the temporary file
    4. Returns the detection results as JSON

    Accepts: JPEG, PNG, BMP images
    Returns: list of detections with class name, confidence, and bounding box
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/bmp", "image/jpg"}

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. "
            f"Allowed types: JPEG, PNG, BMP",
        )

    # Save uploaded file to a temp location
    # We need a file on disk because YOLO reads from file paths, not from memory
    temp_path = None
    try:
        # Create a unique filename to avoid collisions
        suffix = os.path.splitext(file.filename or "upload.jpg")[1] or ".jpg"
        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix="detect_")

        # Write uploaded bytes to the temp file
        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({len(contents) / 1024 / 1024:.1f}MB). Max: 10MB",
            )

        with os.fdopen(temp_fd, "wb") as f:
            f.write(contents)

        logger.info(f"Processing image: {file.filename} ({len(contents)} bytes)")

        # Run detection
        detections = detect_objects(temp_path)

        # Get image dimensions (YOLO provides this in results, but we can also
        # get it from the file — for now we return 0 and let the client handle it)
        return DetectResponse(
            detections=[DetectionResult(**d) for d in detections],
            count=len(detections),
        )

    except FileNotFoundError as e:
        logger.error(f"Model not found: {e}")
        raise HTTPException(
            status_code=503,
            detail="Detection model not available. The server needs the trained "
            "model file (best.pt). Contact the administrator.",
        )
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}",
        )
    finally:
        # Always clean up the temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
