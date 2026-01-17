"""Staff model"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.flight_log import FlightLog
    from src.models.license import License
    from src.models.maintenance_log import MaintenanceLog
    from src.models.organization import Organization
    from src.models.project_assignment import ProjectAssignment
    from src.models.user import User


class Staff(Base, TimestampMixin):
    """Staff model

    Represents staff members who can operate drones or perform maintenance.
    A staff member is linked to a user account.
    """

    __tablename__ = "staff"

    id: Mapped[uuid_pk]
    employee_id: Mapped[str | None] = mapped_column(String(50))  # Internal employee ID
    phone: Mapped[str | None] = mapped_column(String(50))
    emergency_contact: Mapped[str | None] = mapped_column(String(255))
    emergency_phone: Mapped[str | None] = mapped_column(String(50))
    hire_date: Mapped[date | None] = mapped_column(Date)
    department: Mapped[str | None] = mapped_column(String(100))
    position: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    is_pilot: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_maintenance_staff: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="staff")
    user: Mapped[User] = relationship(back_populates="staff")
    licenses: Mapped[list[License]] = relationship(
        back_populates="staff", cascade="all, delete-orphan"
    )
    flight_logs: Mapped[list[FlightLog]] = relationship(
        back_populates="pilot", cascade="all, delete-orphan"
    )
    maintenance_logs: Mapped[list[MaintenanceLog]] = relationship(
        back_populates="technician", cascade="all, delete-orphan"
    )
    project_assignments: Mapped[list[ProjectAssignment]] = relationship(
        back_populates="staff", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Staff(id={self.id!r}, employee_id={self.employee_id!r})"
