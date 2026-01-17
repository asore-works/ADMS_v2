"""Authentication router"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.dependencies.auth import CurrentUser
from src.schemas.auth import PasswordChange, Token, TokenRefresh
from src.schemas.user import CurrentUser as CurrentUserSchema
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """OAuth2 compatible token login

    Get an access token and refresh token for future requests.
    Use the username field for email.
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_refresh: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Refresh access token using refresh token

    Get a new access token and refresh token pair.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_tokens(token_refresh.refresh_token)

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens


@router.get("/me", response_model=CurrentUserSchema)
async def get_current_user_info(current_user: CurrentUser) -> CurrentUserSchema:
    """Get current authenticated user information"""
    return CurrentUserSchema.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Change current user's password"""
    auth_service = AuthService(db)
    success = await auth_service.change_password(
        user=current_user,
        current_password=password_change.current_password,
        new_password=password_change.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout current user

    Note: With JWT tokens, logout is typically handled client-side
    by discarding the tokens. This endpoint is provided for
    completeness and can be extended to implement token blacklisting
    using Redis if needed.
    """
    return {"message": "Successfully logged out"}
