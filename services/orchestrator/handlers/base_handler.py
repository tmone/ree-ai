"""
Base Handler for Orchestrator

Provides common functionality for all intent handlers
"""
import time
import httpx
from typing import Dict, Any, List, Optional
from shared.utils.logger import LogEmoji
from shared.utils.retry import retry_on_http_error
from shared.exceptions import ServiceUnavailableError


class BaseHandler:
    """
    Base class for all orchestrator handlers

    Provides:
    - HTTP client access
    - Logging utilities
    - Common service call methods with retry
    - Error handling
    """

    def __init__(self, http_client: httpx.AsyncClient, logger, service_urls: Dict[str, str]):
        """
        Initialize base handler

        Args:
            http_client: Shared HTTP client
            logger: Structured logger instance
            service_urls: Dict of service URLs (core_gateway, db_gateway, etc.)
        """
        self.http_client = http_client
        self.logger = logger
        self.service_urls = service_urls

    @retry_on_http_error
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "POST",
        json_data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Call external service with retry logic

        Args:
            service_name: Service key in service_urls
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            json_data: Request payload
            timeout: Request timeout in seconds

        Returns:
            Response JSON data

        Raises:
            ServiceUnavailableError: If service is unavailable
        """
        url = f"{self.service_urls[service_name]}{endpoint}"

        try:
            if method == "POST":
                response = await self.http_client.post(url, json=json_data, timeout=timeout)
            elif method == "GET":
                response = await self.http_client.get(url, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                self.logger.warning(f"{LogEmoji.WARNING} {service_name} returned {e.response.status_code}, will retry")
                raise  # Retry on 5xx
            else:
                self.logger.error(f"{LogEmoji.ERROR} {service_name} returned {e.response.status_code} (client error)")
                return {}

        except httpx.RequestError as e:
            self.logger.error(f"{LogEmoji.ERROR} Network error calling {service_name}: {e}")
            raise ServiceUnavailableError(service_name, {"endpoint": endpoint, "error": str(e)})

    def log_handler_start(self, request_id: str, handler_name: str, query: str):
        """Log handler execution start"""
        self.logger.info(f"{LogEmoji.TARGET} [{request_id}] {handler_name} handling: '{query}'")

    def log_handler_complete(self, request_id: str, handler_name: str, duration_ms: float):
        """Log handler execution completion"""
        self.logger.info(f"{LogEmoji.SUCCESS} [{request_id}] {handler_name} completed in {duration_ms:.0f}ms")
