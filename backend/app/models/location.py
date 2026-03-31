"""
Location model — represents a physical zone on the factory floor.

Examples: "Assembly Line A", "Warehouse Bay 3", "Main Entrance"

This table is populated once during setup. Workers select their
current location in the app before scanning items.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Location(Base):
    """A physical zone where safety equipment can be detected."""

    __tablename__ = "locations"

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

    zone: Mapped[str | None] = mapped_column(
        String(100),
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

    # Relationship: one location can appear in many inventory logs
    inventory_logs = relationship(
        "InventoryLog",
        back_populates="location",
    )

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name='{self.name}', zone='{self.zone}')>"
