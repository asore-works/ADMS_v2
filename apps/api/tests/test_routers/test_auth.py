"""認証APIテスト"""

from typing import TYPE_CHECKING

import pytest

from src.models.user import User, UserRole
from src.services.security import create_refresh_token, hash_password

if TYPE_CHECKING:
    import httpx

    from src.models.organization import Organization


@pytest.mark.asyncio
class TestAuthRoutes:
    """認証APIエンドポイントテスト"""

    async def test_login_success(
        self,
        client: httpx.AsyncClient,
        test_user_manager: User,
    ) -> None:
        """ログイン成功"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "manager@test.com",
                "password": "manager123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(
        self,
        client: httpx.AsyncClient,
        test_user_manager: User,
    ) -> None:
        """パスワード不一致"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "manager@test.com",
                "password": "wrong_password",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    async def test_login_user_not_found(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        """存在しないユーザー"""
        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent@test.com",
                "password": "password",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    async def test_login_inactive_user(
        self,
        client: httpx.AsyncClient,
        db_session: AsyncSession,
        test_organization: Organization,
    ) -> None:
        """非アクティブユーザー"""
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

        response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "inactive@test.com",
                "password": "password123",
            },
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Inactive user account"

    async def test_refresh_token_success(
        self,
        client: httpx.AsyncClient,
        test_user_manager: User,
    ) -> None:
        """トークンリフレッシュ成功"""
        refresh_token = create_refresh_token(test_user_manager.id)

        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        """無効なリフレッシュトークン"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid or expired refresh token"

    async def test_get_current_user(
        self,
        client: httpx.AsyncClient,
        test_user_manager: User,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """現在のユーザー情報取得"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers_manager,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "manager@test.com"
        assert data["first_name"] == "Manager"
        assert data["last_name"] == "User"
        assert data["role"] == "manager"

    async def test_get_current_user_unauthorized(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        """未認証でアクセス"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_change_password_success(
        self,
        client: httpx.AsyncClient,
        test_user_manager: User,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """パスワード変更成功"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers_manager,
            json={
                "current_password": "manager123",
                "new_password": "new_password456",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password changed successfully"

        # 新しいパスワードでログインできることを確認
        login_response = await client.post(
            "/api/v1/auth/token",
            data={
                "username": "manager@test.com",
                "password": "new_password456",
            },
        )
        assert login_response.status_code == 200

    async def test_change_password_wrong_current_password(
        self,
        client: httpx.AsyncClient,
        test_user_manager: User,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """現在のパスワードが不一致"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers_manager,
            json={
                "current_password": "wrong_password",
                "new_password": "new_password456",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Current password is incorrect"

    async def test_change_password_unauthorized(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        """未認証でアクセス"""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "current123",
                "new_password": "new456",
            },
        )

        assert response.status_code == 401

    async def test_logout(
        self,
        client: httpx.AsyncClient,
        auth_headers_manager: dict[str, str],
    ) -> None:
        """ログアウト"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers_manager,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    async def test_logout_without_auth(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        """未認証でログアウト（認証不要エンドポイント）"""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"
