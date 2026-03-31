"""
Health check endpoint — verifies the API is running.

Used by Render (and any monitoring tool) to check if the server is alive.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Returns a simple status message confirming the API is running."""
    return {"status": "healthy", "service": "Safety-First Inventory Auditor API"}
