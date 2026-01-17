"""Authentication schemas"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """OAuth2 token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request"""

    refresh_token: str


class TokenData(BaseModel):
    """Token payload data"""

    user_id: UUID
    email: str
    role: str


class LoginRequest(BaseModel):
    """Login request (for JSON-based login alternative)"""

    email: EmailStr
    password: str = Field(min_length=8)


class PasswordChange(BaseModel):
    """Password change request"""

    current_password: str
    new_password: str = Field(min_length=8)


class PasswordReset(BaseModel):
    """Password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""

    token: str
    new_password: str = Field(min_length=8)
