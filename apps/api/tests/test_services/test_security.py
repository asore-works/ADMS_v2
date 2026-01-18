"""セキュリティユーティリティテスト"""

from datetime import timedelta
from uuid import uuid4

from src.services.security import (
    check_needs_rehash,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """パスワードハッシュ化テスト"""

    def test_hash_password(self) -> None:
        """パスワードハッシュ化"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$argon2")

    def test_verify_password_success(self) -> None:
        """パスワード検証成功"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self) -> None:
        """パスワード検証失敗"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_check_needs_rehash_false(self) -> None:
        """再ハッシュ不要"""
        password = "test_password_123"
        hashed = hash_password(password)

        # 新しいハッシュは再ハッシュ不要
        assert check_needs_rehash(hashed) is False


class TestTokenCreation:
    """トークン作成テスト"""

    def test_create_access_token(self) -> None:
        """アクセストークン作成"""
        user_id = uuid4()
        email = "test@example.com"
        role = "admin"

        token = create_access_token(user_id, email, role)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self) -> None:
        """カスタム有効期限でアクセストークン作成"""
        user_id = uuid4()
        email = "test@example.com"
        role = "admin"
        expires_delta = timedelta(hours=1)

        token = create_access_token(user_id, email, role, expires_delta)

        assert token is not None
        payload = decode_access_token(token)
        assert payload is not None

    def test_create_refresh_token(self) -> None:
        """リフレッシュトークン作成"""
        user_id = uuid4()

        token = create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_with_custom_expiry(self) -> None:
        """カスタム有効期限でリフレッシュトークン作成"""
        user_id = uuid4()
        expires_delta = timedelta(days=14)

        token = create_refresh_token(user_id, expires_delta)

        assert token is not None
        payload = decode_refresh_token(token)
        assert payload is not None


class TestTokenDecoding:
    """トークンデコードテスト"""

    def test_decode_access_token_success(self) -> None:
        """アクセストークンデコード成功"""
        user_id = uuid4()
        email = "test@example.com"
        role = "admin"

        token = create_access_token(user_id, email, role)
        payload = decode_access_token(token)

        assert payload is not None
        assert payload.user_id == user_id
        assert payload.email == email
        assert payload.role == role
        assert payload.token_type == "access"

    def test_decode_access_token_invalid_token(self) -> None:
        """無効なアクセストークン"""
        payload = decode_access_token("invalid_token")
        assert payload is None

    def test_decode_access_token_wrong_type(self) -> None:
        """リフレッシュトークンをアクセストークンとしてデコード"""
        user_id = uuid4()
        token = create_refresh_token(user_id)

        # リフレッシュトークンはアクセストークンとしてデコードできない
        payload = decode_access_token(token)
        assert payload is None

    def test_decode_refresh_token_success(self) -> None:
        """リフレッシュトークンデコード成功"""
        user_id = uuid4()

        token = create_refresh_token(user_id)
        payload = decode_refresh_token(token)

        assert payload is not None
        assert payload.user_id == user_id
        assert payload.token_type == "refresh"

    def test_decode_refresh_token_invalid_token(self) -> None:
        """無効なリフレッシュトークン"""
        payload = decode_refresh_token("invalid_token")
        assert payload is None

    def test_decode_refresh_token_wrong_type(self) -> None:
        """アクセストークンをリフレッシュトークンとしてデコード"""
        user_id = uuid4()
        email = "test@example.com"
        role = "admin"

        token = create_access_token(user_id, email, role)

        # アクセストークンはリフレッシュトークンとしてデコードできない
        payload = decode_refresh_token(token)
        assert payload is None

    def test_decode_token_success(self) -> None:
        """トークンデコード成功（汎用）"""
        user_id = uuid4()
        email = "test@example.com"
        role = "admin"

        token = create_access_token(user_id, email, role)
        payload = decode_token(token)

        assert payload is not None
        assert payload.sub == str(user_id)

    def test_decode_token_invalid(self) -> None:
        """無効なトークン"""
        payload = decode_token("invalid_token")
        assert payload is None

    def test_token_payload_user_id_property(self) -> None:
        """TokenPayload.user_idプロパティ"""
        user_id = uuid4()
        email = "test@example.com"
        role = "admin"

        token = create_access_token(user_id, email, role)
        payload = decode_access_token(token)

        assert payload is not None
        assert payload.user_id == user_id
        assert isinstance(payload.user_id, type(user_id))
