"""
Item API routes — CRUD endpoints for safety items.

POST   /api/items       → create a new item
GET    /api/items       → list all items
GET    /api/items/{id}  → get one item
PUT    /api/items/{id}  → update an item
DELETE /api/items/{id}  → delete an item
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from backend.app.services import inventory_service as service

router = APIRouter(prefix="/api/items", tags=["Items"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new safety item in the master list."""
    return service.create_item(db=db, item_data=item)


@router.get("/", response_model=list[ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all safety items with optional pagination."""
    return service.get_items(db=db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by its ID."""
    db_item = service.get_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    return db_item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item. Only sent fields are changed."""
    db_item = service.update_item(db=db, item_id=item_id, item_data=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    return db_item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by its ID."""
    deleted = service.delete_item(db=db, item_id=item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
