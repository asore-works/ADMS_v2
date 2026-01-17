"""Authentication service"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserRole
from src.schemas.auth import Token
from src.services.security import (
    check_needs_rehash,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


class AuthService:
    """Authentication service for user login and token management"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email

        Args:
            email: User's email address

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID

        Args:
            user_id: User's UUID

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password

        Args:
            email: User's email
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(email)
        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Rehash password if needed (e.g., algorithm parameters changed)
        if check_needs_rehash(user.password_hash):
            user.password_hash = hash_password(password)
            await self.db.commit()

        return user

    def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for user

        Args:
            user: Authenticated user

        Returns:
            Token object with access and refresh tokens
        """
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )
        refresh_token = create_refresh_token(user_id=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(self, refresh_token: str) -> Token | None:
        """Refresh access token using refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New Token object if refresh token is valid, None otherwise
        """
        payload = decode_refresh_token(refresh_token)
        if payload is None:
            return None

        user = await self.get_user_by_id(payload.user_id)
        if user is None or not user.is_active:
            return None

        return self.create_tokens(user)

    async def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organization_id: UUID,
        role: str = "viewer",
    ) -> User:
        """Create a new user

        Args:
            email: User's email
            password: Plain text password
            first_name: User's first name
            last_name: User's last name
            organization_id: Organization ID
            role: User role (default: viewer)

        Returns:
            Created user
        """
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
            role=UserRole(role),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change user's password

        Args:
            user: User to update
            current_password: Current password for verification
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise
        """
        if not verify_password(current_password, user.password_hash):
            return False

        user.password_hash = hash_password(new_password)
        await self.db.commit()
        return True
