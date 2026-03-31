"""
Service layer — business logic for inventory operations.

Sits between the API routes and the database.
Routes call service functions. Service functions talk to the database.
Routes NEVER write to the database directly.
"""

from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.inventory_log import InventoryLog
from backend.app.models.item import Item
from backend.app.models.location import Location
from backend.app.schemas.inventory import InventoryLogCreate
from backend.app.schemas.item import ItemCreate, ItemUpdate
from backend.app.schemas.location import LocationCreate, LocationUpdate


# ─── ITEM SERVICES ───────────────────────────────────────────


def create_item(db: Session, item_data: ItemCreate) -> Item:
    """Create a new item in the database."""
    db_item = Item(
        name=item_data.name,
        category=item_data.category,
        description=item_data.description,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get a single item by ID. Returns None if not found."""
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    """Get all items with pagination."""
    return db.query(Item).offset(skip).limit(limit).all()


def update_item(db: Session, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
    """Update an existing item. Only updates fields that were sent."""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        return None

    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item by ID. Returns True if deleted, False if not found."""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        return False
    db.delete(db_item)
    db.commit()
    return True


# ─── LOCATION SERVICES ──────────────────────────────────────


def create_location(db: Session, location_data: LocationCreate) -> Location:
    """Create a new location in the database."""
    db_location = Location(
        name=location_data.name,
        zone=location_data.zone,
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location(db: Session, location_id: int) -> Optional[Location]:
    """Get a single location by ID. Returns None if not found."""
    return db.query(Location).filter(Location.id == location_id).first()


def get_locations(db: Session, skip: int = 0, limit: int = 100) -> list[Location]:
    """Get all locations with pagination."""
    return db.query(Location).offset(skip).limit(limit).all()


def update_location(
    db: Session, location_id: int, location_data: LocationUpdate
) -> Optional[Location]:
    """Update an existing location. Only updates fields that were sent."""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if db_location is None:
        return None

    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)

    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int) -> bool:
    """Delete a location by ID. Returns True if deleted, False if not found."""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if db_location is None:
        return False
    db.delete(db_location)
    db.commit()
    return True


# ─── INVENTORY LOG SERVICES ─────────────────────────────────


def create_inventory_log(
    db: Session, log_data: InventoryLogCreate
) -> InventoryLog:
    """Log a new detection event from the phone."""
    db_log = InventoryLog(
        item_id=log_data.item_id,
        location_id=log_data.location_id,
        confidence=log_data.confidence,
        quantity=log_data.quantity,
        image_path=log_data.image_path,
        notes=log_data.notes,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_inventory_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    item_id: Optional[int] = None,
    location_id: Optional[int] = None,
) -> list[InventoryLog]:
    """Get inventory logs with optional filtering by item or location."""
    query = db.query(InventoryLog)

    if item_id is not None:
        query = query.filter(InventoryLog.item_id == item_id)
    if location_id is not None:
        query = query.filter(InventoryLog.location_id == location_id)

    return (
        query.order_by(InventoryLog.detected_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_inventory_log(db: Session, log_id: int) -> Optional[InventoryLog]:
    """Get a single inventory log by ID."""
    return db.query(InventoryLog).filter(InventoryLog.id == log_id).first()
