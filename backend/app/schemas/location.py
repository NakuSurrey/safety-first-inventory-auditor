"""
Pydantic schemas for Location — validation rules for API input and output.

Three schemas:
  - LocationBase: shared fields (used by both Create and Response)
  - LocationCreate: what the client sends when creating a new location
  - LocationResponse: what the API sends back (includes id, timestamps)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    """Fields shared by both create and response schemas."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Assembly Line A"],
        description="Name of the physical location or zone",
    )

    zone: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["Production Floor East"],
        description="Optional broader zone this location belongs to",
    )


class LocationCreate(LocationBase):
    """Schema for creating a new location. Inherits name, zone.

    Does NOT include id, created_at, updated_at — the database generates those.
    """

    pass


class LocationUpdate(BaseModel):
    """Schema for updating an existing location. All fields optional."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=["Assembly Line B"],
    )

    zone: Optional[str] = Field(
        default=None,
        max_length=100,
        examples=["Production Floor West"],
    )


class LocationResponse(LocationBase):
    """Schema for API responses. Includes database-generated fields."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
