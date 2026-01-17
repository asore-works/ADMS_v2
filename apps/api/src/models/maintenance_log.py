"""Maintenance Log model"""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.equipment import Equipment
    from src.models.staff import Staff


class MaintenanceType(enum.Enum):
    """Maintenance types"""

    ROUTINE = "routine"  # Regular scheduled maintenance
    REPAIR = "repair"  # Repair work
    INSPECTION = "inspection"  # Inspection only
    CALIBRATION = "calibration"  # Calibration/adjustment
    UPGRADE = "upgrade"  # Firmware/software upgrade
    PARTS_REPLACEMENT = "parts_replacement"  # Parts replacement


class MaintenanceStatus(enum.Enum):
    """Maintenance status"""

    SCHEDULED = "scheduled"  # Scheduled for future
    IN_PROGRESS = "in_progress"  # Currently being performed
    COMPLETED = "completed"  # Completed successfully
    FAILED = "failed"  # Maintenance revealed issues
    CANCELLED = "cancelled"  # Cancelled


class MaintenanceLog(Base, TimestampMixin):
    """Maintenance Log model

    Records maintenance activities performed on equipment.
    """

    __tablename__ = "maintenance_logs"

    id: Mapped[uuid_pk]
    maintenance_type: Mapped[MaintenanceType] = mapped_column(
        Enum(MaintenanceType, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(MaintenanceStatus, native_enum=False, length=20),
        default=MaintenanceStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Scheduling
    scheduled_date: Mapped[date | None] = mapped_column(Date, index=True)
    performed_date: Mapped[date | None] = mapped_column(Date)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Checklist and findings
    checklist_items: Mapped[str | None] = mapped_column(Text)  # JSON string of checklist items
    findings: Mapped[str | None] = mapped_column(Text)
    actions_taken: Mapped[str | None] = mapped_column(Text)
    parts_replaced: Mapped[str | None] = mapped_column(Text)  # JSON string of replaced parts

    # Cost tracking
    labor_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    parts_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    total_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # Next maintenance
    next_maintenance_date: Mapped[date | None] = mapped_column(Date)
    next_maintenance_notes: Mapped[str | None] = mapped_column(Text)

    # Documents
    document_urls: Mapped[str | None] = mapped_column(Text)  # JSON array of document URLs

    notes: Mapped[str | None] = mapped_column(Text)

    # Foreign keys
    equipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("equipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    technician_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("staff.id", ondelete="SET NULL"),
        index=True,
    )

    # Relationships
    equipment: Mapped[Equipment] = relationship(back_populates="maintenance_logs")
    technician: Mapped[Staff | None] = relationship(back_populates="maintenance_logs")

    def __repr__(self) -> str:
        return f"MaintenanceLog(id={self.id!r}, title={self.title!r}, status={self.status!r})"
