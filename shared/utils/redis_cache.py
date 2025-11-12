"""
Redis Cache Helper for Layer 2 AI Services
Provides intelligent caching with semantic similarity support
"""
import json
import hashlib
import asyncio
from typing import Optional, Any, Dict, List
from datetime import timedelta
import redis.asyncio as redis
from shared.config import settings
from shared.utils.logger import setup_logger, LogEmoji

logger = setup_logger("redis_cache")


class RedisCache:
    """
    Redis cache manager with semantic caching support.

    Features:
    - Simple key-value caching
    - Semantic similarity caching (for LLM queries)
    - TTL support
    - Namespace isolation
    - JSON serialization
    """

    def __init__(self, namespace: str = "default"):
        """
        Initialize Redis cache.

        Args:
            namespace: Cache namespace for isolation (e.g., "classification", "core_gateway")
        """
        self.namespace = namespace
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if self._redis is None:
            try:
                self._redis = await redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5.0
                )
                # Test connection
                await self._redis.ping()
                logger.info(f"{LogEmoji.SUCCESS} Redis connected: {settings.redis_url}")
            except Exception as e:
                logger.error(f"{LogEmoji.ERROR} Redis connection failed: {e}")
                self._redis = None

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info(f"{LogEmoji.INFO} Redis connection closed")

    def _make_key(self, key: str) -> str:
        """Create namespaced key."""
        return f"{self.namespace}:{key}"

    def _hash_key(self, data: Any) -> str:
        """Create hash from data (for cache key)."""
        # Convert dict/list to JSON string for consistent hashing
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value (JSON deserialized) or None if not found
        """
        if not self._redis:
            await self.connect()
            if not self._redis:
                return None

        try:
            namespaced_key = self._make_key(key)
            value = await self._redis.get(namespaced_key)

            if value:
                logger.debug(f"{LogEmoji.SUCCESS} Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.debug(f"{LogEmoji.WARNING} Cache MISS: {key}")
                return None

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Cache get failed: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cache value.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None = no expiration)

        Returns:
            True if successful
        """
        if not self._redis:
            await self.connect()
            if not self._redis:
                return False

        try:
            namespaced_key = self._make_key(key)
            serialized = json.dumps(value, ensure_ascii=False)

            if ttl:
                await self._redis.setex(namespaced_key, ttl, serialized)
            else:
                await self._redis.set(namespaced_key, serialized)

            logger.debug(f"{LogEmoji.SUCCESS} Cache SET: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Cache set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        if not self._redis:
            return False

        try:
            namespaced_key = self._make_key(key)
            await self._redis.delete(namespaced_key)
            logger.debug(f"{LogEmoji.INFO} Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Cache delete failed: {e}")
            return False

    async def clear_namespace(self) -> int:
        """
        Clear all keys in current namespace.

        Returns:
            Number of keys deleted
        """
        if not self._redis:
            return 0

        try:
            pattern = self._make_key("*")
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self._redis.delete(*keys)
                logger.info(f"{LogEmoji.SUCCESS} Cleared {deleted} keys from namespace '{self.namespace}'")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Namespace clear failed: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for this namespace.

        Returns:
            Stats dict with key count, memory usage, etc.
        """
        if not self._redis:
            return {"error": "Not connected"}

        try:
            pattern = self._make_key("*")
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)

            return {
                "namespace": self.namespace,
                "key_count": len(keys),
                "sample_keys": keys[:5]
            }
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Stats failed: {e}")
            return {"error": str(e)}


class SemanticCache:
    """
    Semantic caching for LLM queries using embeddings.

    Caches LLM responses and retrieves them based on semantic similarity
    rather than exact key match.

    Example:
        "Tìm nhà Q7" ≈ "Tìm nhà Quận 7" → same cache entry
    """

    def __init__(self, namespace: str = "semantic"):
        self.cache = RedisCache(namespace=namespace)
        self.similarity_threshold = 0.95  # Very high threshold for safety

    async def connect(self):
        """Connect to Redis."""
        await self.cache.connect()

    async def close(self):
        """Close connection."""
        await self.cache.close()

    def _compute_simple_similarity(self, text1: str, text2: str) -> float:
        """
        Compute simple text similarity (Jaccard similarity).

        For production, should use embeddings + cosine similarity.
        This is a simple fallback.
        """
        # Normalize
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        # Exact match
        if text1 == text2:
            return 1.0

        # Tokenize
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())

        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    async def get_similar(
        self,
        query: str,
        threshold: Optional[float] = None
    ) -> Optional[Any]:
        """
        Get cached response for semantically similar query.

        Args:
            query: Input query
            threshold: Similarity threshold (default: 0.95)

        Returns:
            Cached response or None
        """
        threshold = threshold or self.similarity_threshold

        # For MVP: Use simple exact match with normalization
        # TODO: Implement embedding-based similarity in future
        normalized_query = query.lower().strip()
        cache_key = f"query:{self.cache._hash_key(normalized_query)}"

        result = await self.cache.get(cache_key)
        if result:
            logger.info(f"{LogEmoji.SUCCESS} Semantic cache HIT for: {query[:50]}...")
        else:
            logger.debug(f"{LogEmoji.WARNING} Semantic cache MISS for: {query[:50]}...")

        return result

    async def set_similar(
        self,
        query: str,
        response: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Cache response for query.

        Args:
            query: Input query
            response: Response to cache
            ttl: Time to live (default: 1 hour)

        Returns:
            True if successful
        """
        normalized_query = query.lower().strip()
        cache_key = f"query:{self.cache._hash_key(normalized_query)}"

        success = await self.cache.set(cache_key, response, ttl=ttl)
        if success:
            logger.info(f"{LogEmoji.SUCCESS} Cached response for: {query[:50]}...")
        return success


# Singleton instances for common namespaces
_cache_instances: Dict[str, RedisCache] = {}
_semantic_cache_instances: Dict[str, SemanticCache] = {}


def get_cache(namespace: str = "default") -> RedisCache:
    """
    Get or create Redis cache instance for namespace.

    Args:
        namespace: Cache namespace

    Returns:
        RedisCache instance
    """
    if namespace not in _cache_instances:
        _cache_instances[namespace] = RedisCache(namespace=namespace)
    return _cache_instances[namespace]


def get_semantic_cache(namespace: str = "semantic") -> SemanticCache:
    """
    Get or create semantic cache instance for namespace.

    Args:
        namespace: Cache namespace

    Returns:
        SemanticCache instance
    """
    if namespace not in _semantic_cache_instances:
        _semantic_cache_instances[namespace] = SemanticCache(namespace=namespace)
    return _semantic_cache_instances[namespace]


async def cleanup_all_caches():
    """Close all cache connections (for graceful shutdown)."""
    for cache in _cache_instances.values():
        await cache.close()
    for cache in _semantic_cache_instances.values():
        await cache.close()
    _cache_instances.clear()
    _semantic_cache_instances.clear()
