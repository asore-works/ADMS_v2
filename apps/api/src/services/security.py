"""Security utilities for password hashing and JWT tokens"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from src.config.settings import settings

# Password hasher instance
_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2id

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        _password_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def check_needs_rehash(hashed_password: str) -> bool:
    """Check if password hash needs to be updated

    Args:
        hashed_password: Stored hash to check

    Returns:
        True if hash needs updating
    """
    return _password_hasher.check_needs_rehash(hashed_password)


def create_access_token(
    user_id: UUID,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token

    Args:
        user_id: User's UUID
        email: User's email
        role: User's role
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token

    Args:
        user_id: User's UUID
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)

    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


class TokenPayload:
    """Decoded token payload"""

    def __init__(
        self,
        sub: str,
        token_type: str,
        exp: datetime,
        iat: datetime,
        email: str | None = None,
        role: str | None = None,
    ) -> None:
        self.sub = sub
        self.token_type = token_type
        self.exp = exp
        self.iat = iat
        self.email = email
        self.role = role

    @property
    def user_id(self) -> UUID:
        """Get user ID as UUID"""
        return UUID(self.sub)


def decode_token(token: str) -> TokenPayload | None:
    """Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(
            sub=payload.get("sub", ""),
            token_type=payload.get("type", ""),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=UTC),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=UTC),
            email=payload.get("email"),
            role=payload.get("role"),
        )
    except JWTError:
        return None


def decode_access_token(token: str) -> TokenPayload | None:
    """Decode and validate an access token

    Args:
        token: JWT access token string

    Returns:
        TokenPayload if valid access token, None otherwise
    """
    payload = decode_token(token)
    if payload is None or payload.token_type != "access":
        return None
    return payload


def decode_refresh_token(token: str) -> TokenPayload | None:
    """Decode and validate a refresh token

    Args:
        token: JWT refresh token string

    Returns:
        TokenPayload if valid refresh token, None otherwise
    """
    payload = decode_token(token)
    if payload is None or payload.token_type != "refresh":
        return None
    return payload
