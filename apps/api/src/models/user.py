"""User model"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.organization import Organization
    from src.models.staff import Staff


class UserRole(enum.Enum):
    """User roles for RBAC"""

    ADMIN = "admin"  # System administrator
    MANAGER = "manager"  # Organization manager
    OPERATOR = "operator"  # Drone operator
    VIEWER = "viewer"  # Read-only access


class User(Base, TimestampMixin):
    """User model

    Represents a user account with authentication and authorization info.
    """

    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            native_enum=False,
            length=20,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=UserRole.VIEWER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship(back_populates="users")
    staff: Mapped[Staff | None] = relationship(back_populates="user", uselist=False)

    @property
    def full_name(self) -> str:
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, role={self.role!r})"
