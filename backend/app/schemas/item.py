"""
Pydantic schemas for Item — validation rules for API input and output.

Three schemas:
  - ItemBase: shared fields (used by both Create and Response)
  - ItemCreate: what the client sends when creating a new item
  - ItemResponse: what the API sends back (includes id, timestamps)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Fields shared by both create and response schemas."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Hard Hat"],
        description="Name of the safety item or tool",
    )

    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["PPE"],
        description="Category grouping (e.g. PPE, Tool, Equipment)",
    )

    description: Optional[str] = Field(
        default=None,
        examples=["Standard yellow hard hat for factory floor use"],
        description="Optional detailed description of the item",
    )


class ItemCreate(ItemBase):
    """Schema for creating a new item. Inherits name, category, description.

    Does NOT include id, created_at, updated_at — the database generates those.
    """

    pass


class ItemUpdate(BaseModel):
    """Schema for updating an existing item. All fields optional.

    Only the fields the client sends will be updated.
    Fields not sent remain unchanged in the database.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=["Safety Helmet"],
    )

    category: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        examples=["PPE"],
    )

    description: Optional[str] = Field(
        default=None,
        examples=["Updated description"],
    )


class ItemResponse(ItemBase):
    """Schema for API responses. Includes everything the database generated.

    model_config with from_attributes=True tells Pydantic:
    'Read data from SQLAlchemy model attributes, not just dictionaries.'
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
