"""
Pydantic schemas for InventoryLog — validation rules for detection events.

This is the CORE schema of the app. Every time the phone detects a safety
item and sends it to the API, this schema validates the data.

Schemas:
  - InventoryLogCreate: what the phone sends after a detection
  - InventoryLogResponse: what the API sends back (includes id, timestamps)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryLogCreate(BaseModel):
    """Schema for logging a new detection event.

    This is what the phone sends after YOLO detects an item.
    The phone knows: which item (item_id), how confident the model was,
    optionally where (location_id), and optionally how many (quantity).
    """

    item_id: int = Field(
        ...,
        gt=0,
        examples=[1],
        description="ID of the detected item (must exist in items table)",
    )

    location_id: Optional[int] = Field(
        default=None,
        gt=0,
        examples=[1],
        description="ID of the location where detection happened (optional)",
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        examples=[0.94],
        description="YOLO model confidence score (0.0 to 1.0)",
    )

    quantity: int = Field(
        default=1,
        ge=1,
        examples=[1],
        description="Number of items detected in this event",
    )

    image_path: Optional[str] = Field(
        default=None,
        max_length=500,
        examples=["/images/detection_001.jpg"],
        description="Path to saved screenshot of the detection (optional)",
    )

    notes: Optional[str] = Field(
        default=None,
        examples=["Worker on assembly line A, morning shift"],
        description="Optional notes from the factory worker",
    )


class InventoryLogResponse(BaseModel):
    """Schema for API responses — includes everything the database generated.

    Contains the full log entry with auto-generated id and detected_at timestamp.
    """

    id: int
    item_id: int
    location_id: Optional[int]
    confidence: float
    quantity: int
    detected_at: datetime
    image_path: Optional[str]
    notes: Optional[str]

    model_config = {"from_attributes": True}
