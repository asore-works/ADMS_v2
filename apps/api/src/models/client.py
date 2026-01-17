"""Client model"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.organization import Organization
    from src.models.project import Project


class Client(Base, TimestampMixin):
    """Client model

    Represents clients who request drone services.
    """

    __tablename__ = "clients"

    id: Mapped[uuid_pk]
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    billing_address: Mapped[str | None] = mapped_column(Text)
    tax_id: Mapped[str | None] = mapped_column(String(100))  # Tax identification number
    payment_terms: Mapped[str | None] = mapped_column(String(100))  # e.g., "Net 30"
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="clients")
    projects: Mapped[list[Project]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Client(id={self.id!r}, company_name={self.company_name!r})"
