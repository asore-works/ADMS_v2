"""Flight Application model"""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.organization import Organization
    from src.models.project import Project


class ApplicationStatus(enum.Enum):
    """Flight application status"""

    DRAFT = "draft"  # Draft, not submitted
    SUBMITTED = "submitted"  # Submitted, awaiting review
    UNDER_REVIEW = "under_review"  # Under review by authorities
    APPROVED = "approved"  # Approved
    REJECTED = "rejected"  # Rejected
    CANCELLED = "cancelled"  # Cancelled by applicant
    EXPIRED = "expired"  # Application period expired


class FlightCategory(enum.Enum):
    """Flight category for DIPS2.0"""

    CATEGORY_1 = "category_1"  # Specific category 1
    CATEGORY_2 = "category_2"  # Specific category 2
    CATEGORY_3 = "category_3"  # Specific category 3
    OPEN = "open"  # Open category


class FlightApplication(Base, TimestampMixin):
    """Flight Application model

    Represents flight applications for regulatory approval (DIPS2.0 integration).
    """

    __tablename__ = "flight_applications"

    id: Mapped[uuid_pk]
    application_number: Mapped[str | None] = mapped_column(String(100), index=True)
    dips_reference_id: Mapped[str | None] = mapped_column(String(100))  # DIPS2.0 reference

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.DRAFT,
        nullable=False,
        index=True,
    )
    flight_category: Mapped[FlightCategory] = mapped_column(
        Enum(FlightCategory, native_enum=False, length=20),
        nullable=False,
    )

    # Flight details
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    flight_area: Mapped[str | None] = mapped_column(Text)  # GeoJSON or description
    flight_altitude_max: Mapped[int | None] = mapped_column()  # meters
    flight_altitude_min: Mapped[int | None] = mapped_column()  # meters

    # Schedule
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    flight_time_start: Mapped[str | None] = mapped_column(String(10))  # HH:MM format
    flight_time_end: Mapped[str | None] = mapped_column(String(10))  # HH:MM format

    # Approval details
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_number: Mapped[str | None] = mapped_column(String(100))
    approval_conditions: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    # Valid period after approval
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date, index=True)

    # Documents
    application_document_url: Mapped[str | None] = mapped_column(String(500))
    approval_document_url: Mapped[str | None] = mapped_column(String(500))

    notes: Mapped[str | None] = mapped_column(Text)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="applications")
    project: Mapped[Project | None] = relationship(back_populates="flight_applications")

    @property
    def is_valid(self) -> bool:
        """Check if the application is currently valid"""
        if self.status != ApplicationStatus.APPROVED:
            return False
        if self.valid_from is None or self.valid_until is None:
            return False
        today = date.today()
        return self.valid_from <= today <= self.valid_until

    def __repr__(self) -> str:
        return f"FlightApplication(id={self.id!r}, number={self.application_number!r})"
