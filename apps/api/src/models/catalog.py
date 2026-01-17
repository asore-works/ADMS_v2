"""Catalog model"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.equipment import Equipment
    from src.models.organization import Organization


class CatalogCategory(enum.Enum):
    """Equipment catalog categories"""

    DRONE = "drone"  # Drone/UAV
    BATTERY = "battery"  # Battery
    CAMERA = "camera"  # Camera/Gimbal
    CONTROLLER = "controller"  # Remote controller
    SENSOR = "sensor"  # Sensor equipment
    ACCESSORY = "accessory"  # Other accessories


class Catalog(Base, TimestampMixin):
    """Catalog model

    Represents equipment templates/catalog items that can be instantiated as actual equipment.
    """

    __tablename__ = "catalogs"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model_number: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[CatalogCategory] = mapped_column(
        Enum(CatalogCategory, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text)
    specifications: Mapped[str | None] = mapped_column(Text)  # JSON string for flexible specs
    weight_grams: Mapped[int | None] = mapped_column()
    max_flight_time_minutes: Mapped[int | None] = mapped_column()
    max_range_meters: Mapped[int | None] = mapped_column()
    price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    image_url: Mapped[str | None] = mapped_column(String(500))
    spec_document_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="catalogs")
    equipments: Mapped[list[Equipment]] = relationship(
        back_populates="catalog", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Catalog(id={self.id!r}, name={self.name!r}, manufacturer={self.manufacturer!r})"
