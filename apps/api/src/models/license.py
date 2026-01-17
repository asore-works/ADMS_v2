"""License model"""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.staff import Staff


class LicenseType(enum.Enum):
    """License/certification types"""

    PILOT_BASIC = "pilot_basic"  # Basic pilot license
    PILOT_ADVANCED = "pilot_advanced"  # Advanced pilot license
    PILOT_INSTRUCTOR = "pilot_instructor"  # Instructor certification
    MAINTENANCE = "maintenance"  # Maintenance certification
    RADIO = "radio"  # Radio operator license
    INSURANCE = "insurance"  # Insurance certification
    OTHER = "other"  # Other certifications


class License(Base, TimestampMixin):
    """License model

    Represents licenses, certifications, and qualifications held by staff.
    """

    __tablename__ = "licenses"

    id: Mapped[uuid_pk]
    license_type: Mapped[LicenseType] = mapped_column(
        Enum(LicenseType, native_enum=False, length=30),
        nullable=False,
        index=True,
    )
    license_number: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_authority: Mapped[str | None] = mapped_column(String(255))
    issue_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date, index=True)
    document_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Foreign keys
    staff_id: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    staff: Mapped[Staff] = relationship(back_populates="licenses")

    @property
    def is_expired(self) -> bool:
        """Check if the license has expired"""
        if self.expiry_date is None:
            return False
        return self.expiry_date < date.today()

    @property
    def days_until_expiry(self) -> int | None:
        """Return days until expiry, or None if no expiry date"""
        if self.expiry_date is None:
            return None
        return (self.expiry_date - date.today()).days

    def __repr__(self) -> str:
        return f"License(id={self.id!r}, name={self.name!r}, type={self.license_type!r})"
