"""
Item model — represents a type of detectable safety item.

Examples: "Hard Hat", "High-Vis Vest", "Safety Goggles", "Wrench"

This table is the master list. It is populated once during setup.
Each row represents one TYPE of item, not an individual physical item.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Item(Base):
    """A type of safety equipment or tool that the YOLO model can detect."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship: one item can appear in many inventory logs
    inventory_logs = relationship(
        "InventoryLog",
        back_populates="item",
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name='{self.name}', category='{self.category}')>"
