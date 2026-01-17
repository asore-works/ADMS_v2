"""Equipment model"""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.catalog import Catalog
    from src.models.flight_log import FlightLog
    from src.models.maintenance_log import MaintenanceLog
    from src.models.organization import Organization


class EquipmentStatus(enum.Enum):
    """Equipment operational status"""

    ACTIVE = "active"  # In operation
    STORED = "stored"  # In storage
    MAINTENANCE = "maintenance"  # Under maintenance
    RETIRED = "retired"  # Decommissioned


class Equipment(Base, TimestampMixin):
    """Equipment model

    Represents actual equipment owned by the organization.
    """

    __tablename__ = "equipments"

    id: Mapped[uuid_pk]
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    internal_id: Mapped[str | None] = mapped_column(String(50))  # Internal asset ID
    nickname: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[EquipmentStatus] = mapped_column(
        Enum(EquipmentStatus, native_enum=False, length=20),
        default=EquipmentStatus.STORED,
        nullable=False,
        index=True,
    )
    purchase_date: Mapped[date | None] = mapped_column(Date)
    warranty_expiry_date: Mapped[date | None] = mapped_column(Date)
    last_maintenance_date: Mapped[date | None] = mapped_column(Date)
    next_maintenance_date: Mapped[date | None] = mapped_column(Date)
    total_flight_time_minutes: Mapped[int] = mapped_column(default=0, nullable=False)
    total_flight_count: Mapped[int] = mapped_column(default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    qr_code: Mapped[str | None] = mapped_column(String(500))  # QR code URL or data

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    catalog_id: Mapped[UUID] = mapped_column(
        ForeignKey("catalogs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="equipments")
    catalog: Mapped[Catalog] = relationship(back_populates="equipments")
    flight_logs: Mapped[list[FlightLog]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )
    maintenance_logs: Mapped[list[MaintenanceLog]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Equipment(id={self.id!r}, serial_number={self.serial_number!r})"
