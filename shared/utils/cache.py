"""
Redis Caching Utilities
- Cache decorators for functions
- TTL-based caching
- JSON serialization
- Cache invalidation
"""

import json
import pickle
import functools
from typing import Any, Optional, Callable
from datetime import timedelta
import redis.asyncio as redis

from shared.utils.logger import get_logger
from shared.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("✅ Redis client initialized")

    return _redis_client


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("✅ Redis connection closed")


def cache(
    ttl: int = 300,
    key_prefix: str = "",
    serialize: str = "json"  # "json" or "pickle"
):
    """
    Cache decorator for async functions

    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
        serialize: Serialization method ("json" or "pickle")

    Example:
        @cache(ttl=600, key_prefix="user")
        async def get_user(user_id: str):
            return await db.get_user(user_id)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            try:
                client = await get_redis()

                # Try to get from cache
                cached = await client.get(cache_key)
                if cached:
                    logger.debug(f"🎯 Cache hit: {cache_key}")

                    if serialize == "json":
                        return json.loads(cached)
                    else:
                        return pickle.loads(cached.encode('latin1'))

                # Cache miss - call function
                logger.debug(f"❌ Cache miss: {cache_key}")
                result = await func(*args, **kwargs)

                # Store in cache
                if serialize == "json":
                    await client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, ensure_ascii=False)
                    )
                else:
                    await client.setex(
                        cache_key,
                        ttl,
                        pickle.dumps(result).decode('latin1')
                    )

                logger.debug(f"💾 Cached: {cache_key} (TTL: {ttl}s)")
                return result

            except Exception as e:
                logger.warning(f"⚠️ Cache error: {str(e)}, calling function directly")
                return await func(*args, **kwargs)

        return wrapper
    return decorator


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"❌ Cache get error: {str(e)}")
        return None


async def cache_set(key: str, value: Any, ttl: int = 300):
    """Set value in cache"""
    try:
        client = await get_redis()
        await client.setex(
            key,
            ttl,
            json.dumps(value, ensure_ascii=False)
        )
        logger.debug(f"💾 Cached: {key} (TTL: {ttl}s)")
    except Exception as e:
        logger.error(f"❌ Cache set error: {str(e)}")


async def cache_delete(key: str):
    """Delete key from cache"""
    try:
        client = await get_redis()
        await client.delete(key)
        logger.debug(f"🗑️ Deleted from cache: {key}")
    except Exception as e:
        logger.error(f"❌ Cache delete error: {str(e)}")


async def cache_clear(pattern: str = "*"):
    """Clear all keys matching pattern"""
    try:
        client = await get_redis()
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            await client.delete(*keys)
            logger.info(f"🗑️ Cleared {len(keys)} keys matching '{pattern}'")
    except Exception as e:
        logger.error(f"❌ Cache clear error: {str(e)}")
