"""共通テストfixture"""

from collections.abc import AsyncGenerator
from typing import Any

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.db.base import Base
from src.db.session import get_db
from src.main import app
from src.models.catalog import Catalog, CatalogCategory
from src.models.organization import Organization
from src.models.user import User, UserRole
from src.services.security import create_access_token, hash_password

TEST_DATABASE_URL = "postgresql+asyncpg://adms_user:adms_password@localhost:5432/adms_test"


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[Any]:
    """テスト用データベースエンジン"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # テーブル作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # テーブル削除
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: Any) -> AsyncGenerator[AsyncSession]:
    """テスト用データベースセッション"""
    session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient]:
    """テスト用HTTPクライアント"""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """テスト用組織"""
    org = Organization(
        name="Test Organization",
        code="TEST-ORG",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_user_admin(
    db_session: AsyncSession,
    test_organization: Organization,
) -> User:
    """テスト用管理者ユーザー"""
    user = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_manager(
    db_session: AsyncSession,
    test_organization: Organization,
) -> User:
    """テスト用マネージャーユーザー"""
    user = User(
        email="manager@test.com",
        password_hash=hash_password("manager123"),
        first_name="Manager",
        last_name="User",
        role=UserRole.MANAGER,
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_operator(
    db_session: AsyncSession,
    test_organization: Organization,
) -> User:
    """テスト用オペレーターユーザー"""
    user = User(
        email="operator@test.com",
        password_hash=hash_password("operator123"),
        first_name="Operator",
        last_name="User",
        role=UserRole.OPERATOR,
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_catalog(
    db_session: AsyncSession,
    test_organization: Organization,
) -> Catalog:
    """テスト用カタログ"""
    catalog = Catalog(
        organization_id=test_organization.id,
        name="DJI Mavic 3",
        category=CatalogCategory.DRONE,
        manufacturer="DJI",
        model_number="CP.MA.00000001",
        sku_code="DJI-M3-001",
        description="Test drone catalog",
        price=200000,
        weight_grams=900,
        max_flight_time_minutes=46,
        specifications={"camera": "4/3 CMOS", "video": "5.1K"},
        is_active=True,
        version=1,
    )
    db_session.add(catalog)
    await db_session.commit()
    await db_session.refresh(catalog)
    return catalog


@pytest.fixture
def auth_headers_admin(test_user_admin: User) -> dict[str, str]:
    """管理者用認証ヘッダー"""
    token = create_access_token(
        user_id=test_user_admin.id,
        email=test_user_admin.email,
        role=test_user_admin.role.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_manager(test_user_manager: User) -> dict[str, str]:
    """マネージャー用認証ヘッダー"""
    token = create_access_token(
        user_id=test_user_manager.id,
        email=test_user_manager.email,
        role=test_user_manager.role.value,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_operator(test_user_operator: User) -> dict[str, str]:
    """オペレーター用認証ヘッダー"""
    token = create_access_token(
        user_id=test_user_operator.id,
        email=test_user_operator.email,
        role=test_user_operator.role.value,
    )
    return {"Authorization": f"Bearer {token}"}
