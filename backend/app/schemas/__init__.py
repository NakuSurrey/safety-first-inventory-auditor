"""
Schema package — Pydantic validation schemas for all API endpoints.

Importing from here lets other files do:
    from backend.app.schemas import ItemCreate, ItemResponse
instead of:
    from backend.app.schemas.item import ItemCreate, ItemResponse
"""

from backend.app.schemas.inventory import InventoryLogCreate, InventoryLogResponse
from backend.app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from backend.app.schemas.location import LocationCreate, LocationResponse, LocationUpdate

__all__ = [
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "InventoryLogCreate",
    "InventoryLogResponse",
]
