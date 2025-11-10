"""
Centralized HTTP client management with connection pooling

This module provides a factory for creating configured HTTP clients
with best-practice defaults for inter-service communication.

Usage:
    from shared.utils.http_client import HTTPClientFactory

    # Create client with default settings
    client = HTTPClientFactory.create_client()

    # Create client with custom timeout
    client = HTTPClientFactory.create_client(timeout=90.0)

    # Create client with custom connection pool
    client = HTTPClientFactory.create_client(
        timeout=60.0,
        max_connections=200,
        max_keepalive=50
    )
"""
import httpx
from typing import Optional
from shared.config import settings


class HTTPClientFactory:
    """
    Factory for creating configured HTTP clients with connection pooling

    Benefits:
    - Reuses TCP connections (reduces latency)
    - Prevents connection leaks
    - Consistent configuration across all services
    - Easy to tune performance from one place
    """

    @staticmethod
    def create_client(
        timeout: Optional[float] = None,
        max_connections: Optional[int] = None,
        max_keepalive: Optional[int] = None,
        follow_redirects: bool = True,
        max_redirects: int = 3
    ) -> httpx.AsyncClient:
        """
        Create HTTP client with best-practice defaults

        Args:
            timeout: Request timeout in seconds (default: settings.HTTP_TIMEOUT_DEFAULT)
            max_connections: Total connection pool size (default: settings.HTTP_MAX_CONNECTIONS)
            max_keepalive: Keepalive connection pool size (default: settings.HTTP_MAX_KEEPALIVE)
            follow_redirects: Whether to follow HTTP redirects (default: True)
            max_redirects: Maximum number of redirects to follow (default: 3)

        Returns:
            Configured httpx.AsyncClient instance

        Example:
            ```python
            # Basic usage
            client = HTTPClientFactory.create_client()

            # Custom timeout for slow services
            client = HTTPClientFactory.create_client(timeout=120.0)

            # High-throughput client
            client = HTTPClientFactory.create_client(
                max_connections=500,
                max_keepalive=100
            )
            ```
        """
        # Use settings defaults if not provided
        timeout_value = timeout if timeout is not None else settings.HTTP_TIMEOUT_DEFAULT
        max_conn = max_connections if max_connections is not None else settings.HTTP_MAX_CONNECTIONS
        max_keep = max_keepalive if max_keepalive is not None else settings.HTTP_MAX_KEEPALIVE

        return httpx.AsyncClient(
            timeout=timeout_value,
            limits=httpx.Limits(
                max_keepalive_connections=max_keep,
                max_connections=max_conn,
                keepalive_expiry=30.0  # Reuse connections for 30 seconds
            ),
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            # Security: Use HTTP/2 for better performance (if server supports)
            http2=True
        )

    @staticmethod
    def create_rag_client() -> httpx.AsyncClient:
        """
        Create HTTP client optimized for RAG service (longer timeout)

        RAG operations can be slow due to:
        - Vector search in OpenSearch
        - LLM generation
        - Multiple retrieval rounds

        Returns:
            HTTP client with extended timeout (90s)
        """
        return HTTPClientFactory.create_client(
            timeout=settings.HTTP_TIMEOUT_RAG
        )

    @staticmethod
    def create_classification_client() -> httpx.AsyncClient:
        """
        Create HTTP client optimized for classification service

        Classification is typically fast (simple LLM calls)

        Returns:
            HTTP client with standard timeout (30s)
        """
        return HTTPClientFactory.create_client(
            timeout=settings.HTTP_TIMEOUT_CLASSIFICATION
        )

    @staticmethod
    def create_core_gateway_client() -> httpx.AsyncClient:
        """
        Create HTTP client optimized for Core Gateway (LLM calls)

        LLM generation can be slow depending on:
        - Model size
        - Response length
        - Provider latency

        Returns:
            HTTP client with LLM timeout (60s)
        """
        return HTTPClientFactory.create_client(
            timeout=settings.LLM_TIMEOUT
        )


class HTTPClientManager:
    """
    Manager for shared HTTP client instances (singleton pattern)

    Use this when you want to share a single client across multiple
    components instead of creating new clients repeatedly.

    WARNING: Only use if you understand the implications of sharing
    a client across async tasks. For most cases, create separate
    clients per service.

    Example:
        ```python
        # In service __init__
        self.http_client = HTTPClientManager.get_shared_client()

        # Don't forget to close on shutdown
        async def on_shutdown(self):
            await HTTPClientManager.close_all()
        ```
    """

    _shared_client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_shared_client(cls) -> httpx.AsyncClient:
        """
        Get or create shared HTTP client instance

        Returns:
            Shared httpx.AsyncClient (singleton)
        """
        if cls._shared_client is None:
            cls._shared_client = HTTPClientFactory.create_client()
        return cls._shared_client

    @classmethod
    async def close_all(cls):
        """
        Close shared HTTP client (call on service shutdown)
        """
        if cls._shared_client is not None:
            await cls._shared_client.aclose()
            cls._shared_client = None
