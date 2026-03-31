"""
Main FastAPI application — the entry point for the entire backend.

Creates the FastAPI app, configures CORS, registers all route files,
and sets up logging.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import health, inventory, items, locations
from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app.models import Item, Location, InventoryLog  # noqa: F401

# ─── LOGGING SETUP ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("safety_auditor")

# ─── CREATE FASTAPI APP ─────────────────────────────────────
app = FastAPI(
    title="Safety-First Inventory Auditor API",
    description=(
        "A computer vision-powered inventory management system for factory "
        "floor safety equipment. The mobile app uses YOLOv8-nano to detect "
        "PPE and tools, then logs detections to this API."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS MIDDLEWARE ─────────────────────────────────────────
# Allows the React Native mobile app to connect to this API.
# Without this, the phone's HTTP requests would be blocked by
# the browser's same-origin policy.
origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REGISTER ROUTES ────────────────────────────────────────
app.include_router(health.router)
app.include_router(items.router)
app.include_router(locations.router)
app.include_router(inventory.router)

# ─── CREATE TABLES ON STARTUP ────────────────────────────────
# In production, Alembic migrations handle this.
# This is a fallback for first deployment — creates tables if they
# do not exist yet. Does NOT overwrite existing tables.
Base.metadata.create_all(bind=engine)

logger.info("Safety-First Inventory Auditor API started successfully")


# ─── ROOT ENDPOINT ──────────────────────────────────────────
@app.get("/")
def root():
    """Root endpoint — redirects users to the docs."""
    return {
        "message": "Safety-First Inventory Auditor API",
        "docs": "/docs",
        "health": "/health",
    }
