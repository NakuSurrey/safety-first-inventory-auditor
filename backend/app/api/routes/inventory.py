"""
Inventory Log API routes — the CORE endpoint of the entire app.

This is what the phone calls every time YOLO detects a safety item.

POST  /api/inventory       → log a new detection event
GET   /api/inventory       → list detection logs (with optional filters)
GET   /api/inventory/{id}  → get one detection log
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.inventory import InventoryLogCreate, InventoryLogResponse
from backend.app.services import inventory_service as service

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.post("/", response_model=InventoryLogResponse, status_code=201)
def log_detection(log: InventoryLogCreate, db: Session = Depends(get_db)):
    """Log a new detection event from the YOLO model on the phone.

    This is the primary endpoint the mobile app calls after detecting
    a safety item. It validates the data and writes it to the database.
    """
    # Verify the referenced item exists
    item = service.get_item(db=db, item_id=log.item_id)
    if item is None:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {log.item_id} not found. "
            "Cannot log detection for non-existent item.",
        )

    # Verify the referenced location exists (if provided)
    if log.location_id is not None:
        location = service.get_location(db=db, location_id=log.location_id)
        if location is None:
            raise HTTPException(
                status_code=404,
                detail=f"Location with id {log.location_id} not found.",
            )

    return service.create_inventory_log(db=db, log_data=log)


@router.get("/", response_model=list[InventoryLogResponse])
def list_inventory_logs(
    skip: int = 0,
    limit: int = 100,
    item_id: Optional[int] = Query(default=None, description="Filter by item ID"),
    location_id: Optional[int] = Query(
        default=None, description="Filter by location ID"
    ),
    db: Session = Depends(get_db),
):
    """Get detection logs with optional filtering by item or location."""
    return service.get_inventory_logs(
        db=db,
        skip=skip,
        limit=limit,
        item_id=item_id,
        location_id=location_id,
    )


@router.get("/{log_id}", response_model=InventoryLogResponse)
def get_inventory_log(log_id: int, db: Session = Depends(get_db)):
    """Get a single detection log by its ID."""
    db_log = service.get_inventory_log(db=db, log_id=log_id)
    if db_log is None:
        raise HTTPException(
            status_code=404, detail=f"Inventory log with id {log_id} not found"
        )
    return db_log
