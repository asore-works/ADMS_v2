"""Organization model"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.catalog import Catalog
    from src.models.client import Client
    from src.models.equipment import Equipment
    from src.models.flight_application import FlightApplication
    from src.models.project import Project
    from src.models.staff import Staff
    from src.models.user import User


class Organization(Base, TimestampMixin):
    """Organization model

    Represents a company or organization that owns drones and manages operations.
    """

    __tablename__ = "organizations"
    __table_args__ = (Index("ix_organizations_name_active", "name", "is_active"),)

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))
    logo_url: Mapped[str | None] = mapped_column(String(500))  # Organization logo
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)

    # Relationships
    users: Mapped[list[User]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    catalogs: Mapped[list[Catalog]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    equipments: Mapped[list[Equipment]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    staff: Mapped[list[Staff]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    clients: Mapped[list[Client]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    projects: Mapped[list[Project]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    applications: Mapped[list[FlightApplication]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Organization(id={self.id!r}, name={self.name!r}, code={self.code!r})"
