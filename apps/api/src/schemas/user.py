"""User schemas"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(min_length=8)
    organization_id: UUID
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    """User update schema"""

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserResponse(UserBase):
    """User response schema"""

    id: UUID
    role: UserRole
    is_active: bool
    is_verified: bool
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserWithOrganization(UserResponse):
    """User response with organization details"""

    organization_name: str


class CurrentUser(BaseModel):
    """Current authenticated user schema"""

    id: UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    organization_id: UUID
    is_active: bool

    model_config = {"from_attributes": True}

    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
