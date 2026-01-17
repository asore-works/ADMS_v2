"""データベースセッション管理"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import settings

# 非同期エンジンの作成
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# セッションファクトリの作成
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """データベースセッションを取得するジェネレータ

    FastAPIのDependency Injectionで使用

    Yields:
        AsyncSession: 非同期データベースセッション
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
