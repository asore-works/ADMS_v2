"""Project model"""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.client import Client
    from src.models.flight_application import FlightApplication
    from src.models.flight_log import FlightLog
    from src.models.organization import Organization
    from src.models.project_assignment import ProjectAssignment


class ProjectStatus(enum.Enum):
    """Project status"""

    PLANNING = "planning"  # In planning phase
    IN_PROGRESS = "in_progress"  # Currently active
    COMPLETED = "completed"  # Successfully completed
    CANCELLED = "cancelled"  # Cancelled
    ON_HOLD = "on_hold"  # Temporarily paused


class Project(Base, TimestampMixin):
    """Project model

    Represents drone operation projects.
    """

    __tablename__ = "projects"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))  # Project code
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False, length=20),
        default=ProjectStatus.PLANNING,
        nullable=False,
        index=True,
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    location: Mapped[str | None] = mapped_column(Text)  # Project location description
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    budget: Mapped[float | None] = mapped_column(Numeric(14, 2))
    actual_cost: Mapped[float | None] = mapped_column(Numeric(14, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"),
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="projects")
    client: Mapped[Client | None] = relationship(back_populates="projects")
    staff_assignments: Mapped[list[ProjectAssignment]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    flight_logs: Mapped[list[FlightLog]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    flight_applications: Mapped[list[FlightApplication]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, status={self.status!r})"
