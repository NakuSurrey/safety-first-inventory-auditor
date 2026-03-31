"""
InventoryLog model — records every single detection event.

Each row represents ONE moment when the phone camera detected a
safety item. This table grows rapidly (many rows per day).

Foreign keys point to items and locations tables (normalised).
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class InventoryLog(Base):
    """A single detection event from the YOLO model."""

    __tablename__ = "inventory_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Foreign key: WHICH item was detected
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("items.id"),
        nullable=False,
        index=True,
    )

    # Foreign key: WHERE it was detected (optional)
    location_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )

    # How confident the YOLO model was (0.0 to 1.0)
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # How many items were counted in this detection
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # When the detection happened
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    # Optional path to a saved screenshot of the detection
    image_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Optional notes from the worker
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --- RELATIONSHIPS ---
    # These let you navigate from a log entry to its item/location
    # log.item → returns the Item object
    # log.location → returns the Location object
    item = relationship(
        "Item",
        back_populates="inventory_logs",
    )

    location = relationship(
        "Location",
        back_populates="inventory_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryLog(id={self.id}, item_id={self.item_id}, "
            f"confidence={self.confidence}, detected_at={self.detected_at})>"
        )
