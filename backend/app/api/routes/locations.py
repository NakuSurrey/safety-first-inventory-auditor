"""
Location API routes — CRUD endpoints for factory floor zones.

POST   /api/locations       → create a new location
GET    /api/locations       → list all locations
GET    /api/locations/{id}  → get one location
PUT    /api/locations/{id}  → update a location
DELETE /api/locations/{id}  → delete a location
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from backend.app.services import inventory_service as service

router = APIRouter(prefix="/api/locations", tags=["Locations"])


@router.post("/", response_model=LocationResponse, status_code=201)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new factory floor location."""
    return service.create_location(db=db, location_data=location)


@router.get("/", response_model=list[LocationResponse])
def list_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all locations with optional pagination."""
    return service.get_locations(db=db, skip=skip, limit=limit)


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a single location by its ID."""
    db_location = service.get_location(db=db, location_id=location_id)
    if db_location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    return db_location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int, location: LocationUpdate, db: Session = Depends(get_db)
):
    """Update an existing location. Only sent fields are changed."""
    db_location = service.update_location(
        db=db, location_id=location_id, location_data=location
    )
    if db_location is None:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
    return db_location


@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Delete a location by its ID."""
    deleted = service.delete_location(db=db, location_id=location_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Location with id {location_id} not found"
        )
