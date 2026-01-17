"""Redis connection management"""

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis

from src.config.settings import settings


class RedisManager:
    """Redis connection pool manager"""

    _pool: ConnectionPool | None = None

    @classmethod
    async def get_pool(cls) -> ConnectionPool:
        """Get or create Redis connection pool"""
        if cls._pool is None:
            cls._pool = ConnectionPool.from_url(  # pyright: ignore[reportUnknownMemberType]
                settings.redis_url,
                max_connections=20,
                decode_responses=True,
            )
        return cls._pool

    @classmethod
    async def close_pool(cls) -> None:
        """Close Redis connection pool"""
        if cls._pool is not None:
            await cls._pool.aclose()
            cls._pool = None


async def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool"""
    return await RedisManager.get_pool()


async def get_redis() -> AsyncGenerator[Redis]:
    """Get Redis client from connection pool

    FastAPI Dependency Injection compatible.

    Yields:
        Redis: Async Redis client
    """
    pool = await RedisManager.get_pool()
    client = aioredis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.aclose()


async def close_redis_pool() -> None:
    """Close Redis connection pool

    Call this on application shutdown.
    """
    await RedisManager.close_pool()


# Convenience functions for direct usage (not dependency injection)


async def redis_get(key: str) -> str | None:
    """Get value from Redis by key"""
    pool = await RedisManager.get_pool()
    client = aioredis.Redis(connection_pool=pool)
    try:
        result = await client.get(key)
        if isinstance(result, bytes):
            return result.decode("utf-8")
        return result
    finally:
        await client.aclose()


async def redis_set(
    key: str,
    value: str,
    expire_seconds: int | None = None,
) -> bool:
    """Set value in Redis

    Args:
        key: Redis key
        value: Value to store
        expire_seconds: Optional TTL in seconds

    Returns:
        True if successful
    """
    pool = await RedisManager.get_pool()
    client = aioredis.Redis(connection_pool=pool)
    try:
        if expire_seconds:
            result = await client.setex(key, expire_seconds, value)
        else:
            result = await client.set(key, value)
        return bool(result)
    finally:
        await client.aclose()


async def redis_delete(key: str) -> int:
    """Delete key from Redis

    Returns:
        Number of keys deleted (0 or 1)
    """
    pool = await RedisManager.get_pool()
    client = aioredis.Redis(connection_pool=pool)
    try:
        result = await client.delete(key)
        return int(result)
    finally:
        await client.aclose()


async def redis_exists(key: str) -> bool:
    """Check if key exists in Redis"""
    pool = await RedisManager.get_pool()
    client = aioredis.Redis(connection_pool=pool)
    try:
        result = await client.exists(key)
        return bool(result)
    finally:
        await client.aclose()
