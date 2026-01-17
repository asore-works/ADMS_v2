"""Project Assignment model"""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.project import Project
    from src.models.staff import Staff


class AssignmentRole(enum.Enum):
    """Assignment role types"""

    PILOT = "pilot"  # Primary pilot
    COPILOT = "copilot"  # Co-pilot/assistant
    OBSERVER = "observer"  # Visual observer
    SUPERVISOR = "supervisor"  # Project supervisor
    TECHNICIAN = "technician"  # Technical support


class ProjectAssignment(Base, TimestampMixin):
    """Project Assignment model

    Represents staff assignments to projects with specific roles.
    """

    __tablename__ = "project_assignments"

    id: Mapped[uuid_pk]
    role: Mapped[AssignmentRole] = mapped_column(
        Enum(AssignmentRole, native_enum=False, length=20),
        nullable=False,
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    is_confirmed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Foreign keys
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    staff_id: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    project: Mapped[Project] = relationship(back_populates="staff_assignments")
    staff: Mapped[Staff] = relationship(back_populates="project_assignments")

    def __repr__(self) -> str:
        return f"ProjectAssignment(id={self.id!r}, role={self.role!r})"
