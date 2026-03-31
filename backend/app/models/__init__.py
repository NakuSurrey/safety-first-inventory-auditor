"""
Models package.

All models are imported here so that:
1. Alembic can discover them via Base.metadata
2. Other files can import from one place:
   from backend.app.models import Item, Location, InventoryLog
"""

from backend.app.models.inventory_log import InventoryLog
from backend.app.models.item import Item
from backend.app.models.location import Location

__all__ = ["Item", "Location", "InventoryLog"]
