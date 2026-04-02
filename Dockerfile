# Dockerfile for Railway deployment
# Runs the FastAPI backend with YOLO detection capability

# ── Base image ─────────────────────────────────────────────────────────
# Python 3.11 slim — smaller than full image, has everything we need
FROM python:3.11-slim

# ── System dependencies ────────────────────────────────────────────────
# OpenCV needs these Linux libraries to work (even the headless version)
# libgl1 = OpenGL (image processing), libglib2.0 = system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ────────────────────────────────────────
# IMPORTANT: Install CPU-only PyTorch FIRST from PyTorch's CPU index.
# ultralytics auto-installs PyTorch WITH CUDA (~2.5 GB) if torch is missing.
# Railway has no GPU, so we only need CPU torch (~200 MB).
# By installing torch first, ultralytics sees it exists and skips the CUDA version.
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Now install the rest of the dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Copy application code ─────────────────────────────────────────────
COPY backend/ ./backend/
COPY .env.example ./.env.example

# ── Copy the trained model ─────────────────────────────────────────────
# The model file (best.pt) must exist for detection to work
# We copy the full models directory structure that the code expects
COPY models/runs/detect/ppe_model/weights/best.pt ./models/runs/detect/ppe_model/weights/best.pt

# ── Expose port ────────────────────────────────────────────────────────
# Railway sets the PORT environment variable automatically
# uvicorn will read it from the environment
EXPOSE 8000

# ── Start command ──────────────────────────────────────────────────────
# Railway sets PORT env var — we use it. Default to 8000 if not set.
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
