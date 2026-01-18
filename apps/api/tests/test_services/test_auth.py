"""認証サービステスト"""

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from src.models.user import User, UserRole
from src.services.auth import AuthService
from src.services.security import create_refresh_token, hash_password

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models.organization import Organization


@pytest.mark.asyncio
class TestAuthService:
    """AuthServiceのテスト"""

    async def test_get_user_by_email_success(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """メールアドレスでユーザー取得成功"""
        auth_service = AuthService(db_session)
        user = await auth_service.get_user_by_email(test_user_manager.email)

        assert user is not None
        assert user.id == test_user_manager.id
        assert user.email == test_user_manager.email

    async def test_get_user_by_email_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """存在しないメールアドレス"""
        auth_service = AuthService(db_session)
        user = await auth_service.get_user_by_email("nonexistent@example.com")

        assert user is None

    async def test_get_user_by_id_success(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """IDでユーザー取得成功"""
        auth_service = AuthService(db_session)
        user = await auth_service.get_user_by_id(test_user_manager.id)

        assert user is not None
        assert user.id == test_user_manager.id
        assert user.email == test_user_manager.email

    async def test_get_user_by_id_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """存在しないID"""
        auth_service = AuthService(db_session)
        user = await auth_service.get_user_by_id(uuid4())

        assert user is None

    async def test_authenticate_success(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """認証成功"""
        auth_service = AuthService(db_session)
        user = await auth_service.authenticate("manager@test.com", "manager123")

        assert user is not None
        assert user.id == test_user_manager.id
        assert user.email == test_user_manager.email

    async def test_authenticate_wrong_password(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """パスワード不一致"""
        auth_service = AuthService(db_session)
        user = await auth_service.authenticate("manager@test.com", "wrong_password")

        assert user is None

    async def test_authenticate_user_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """存在しないユーザー"""
        auth_service = AuthService(db_session)
        user = await auth_service.authenticate("nonexistent@test.com", "password")

        assert user is None

    async def test_create_tokens(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """トークン生成"""
        auth_service = AuthService(db_session)
        tokens = auth_service.create_tokens(test_user_manager)

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        assert isinstance(tokens.access_token, str)
        assert isinstance(tokens.refresh_token, str)

    async def test_refresh_tokens_success(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """トークンリフレッシュ成功"""
        auth_service = AuthService(db_session)

        # リフレッシュトークンを作成
        refresh_token = create_refresh_token(test_user_manager.id)

        # トークンをリフレッシュ
        new_tokens = await auth_service.refresh_tokens(refresh_token)

        assert new_tokens is not None
        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None
        assert new_tokens.token_type == "bearer"

    async def test_refresh_tokens_invalid_token(
        self,
        db_session: AsyncSession,
    ) -> None:
        """無効なリフレッシュトークン"""
        auth_service = AuthService(db_session)
        new_tokens = await auth_service.refresh_tokens("invalid_token")

        assert new_tokens is None

    async def test_refresh_tokens_user_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """存在しないユーザーのトークン"""
        auth_service = AuthService(db_session)

        # 存在しないユーザーIDでリフレッシュトークンを作成
        refresh_token = create_refresh_token(uuid4())

        new_tokens = await auth_service.refresh_tokens(refresh_token)

        assert new_tokens is None

    async def test_refresh_tokens_inactive_user(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """非アクティブユーザーのトークン"""
        # 非アクティブユーザーを作成
        inactive_user = User(
            email="inactive@test.com",
            password_hash=hash_password("password123"),
            first_name="Inactive",
            last_name="User",
            role=UserRole.VIEWER,
            organization_id=test_organization.id,
            is_active=False,
        )
        db_session.add(inactive_user)
        await db_session.commit()
        await db_session.refresh(inactive_user)

        auth_service = AuthService(db_session)
        refresh_token = create_refresh_token(inactive_user.id)

        new_tokens = await auth_service.refresh_tokens(refresh_token)

        assert new_tokens is None

    async def test_create_user(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """ユーザー作成"""
        auth_service = AuthService(db_session)

        user = await auth_service.create_user(
            email="newuser@test.com",
            password="password123",
            first_name="New",
            last_name="User",
            organization_id=test_organization.id,
            role="operator",
        )

        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.organization_id == test_organization.id
        assert user.role == UserRole.OPERATOR
        assert user.password_hash != "password123"  # ハッシュ化されている

    async def test_change_password_success(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """パスワード変更成功"""
        auth_service = AuthService(db_session)

        # パスワード変更
        success = await auth_service.change_password(
            user=test_user_manager,
            current_password="manager123",
            new_password="new_password456",
        )

        assert success is True

        # 新しいパスワードで認証できることを確認
        await db_session.refresh(test_user_manager)
        user = await auth_service.authenticate("manager@test.com", "new_password456")
        assert user is not None
        assert user.id == test_user_manager.id

    async def test_change_password_wrong_current_password(
        self,
        db_session: AsyncSession,
        test_user_manager: User,
    ) -> None:
        """現在のパスワードが不一致"""
        auth_service = AuthService(db_session)

        # 間違った現在のパスワードでパスワード変更を試みる
        success = await auth_service.change_password(
            user=test_user_manager,
            current_password="wrong_password",
            new_password="new_password456",
        )

        assert success is False

        # 元のパスワードで認証できることを確認
        user = await auth_service.authenticate("manager@test.com", "manager123")
        assert user is not None
