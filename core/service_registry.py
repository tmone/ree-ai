"""Service Registry models and client for service discovery."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import httpx


class ServiceInfo(BaseModel):
    """Information about a registered service."""
    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    host: str = Field(..., description="Service host")
    port: int = Field(..., description="Service port")
    capabilities: List[str] = Field(default_factory=list, description="Service capabilities")
    health_endpoint: str = Field("/health", description="Health check endpoint")
    registered_at: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    @property
    def base_url(self) -> str:
        """Get base URL for the service."""
        return f"http://{self.host}:{self.port}"


class ServiceRegistryClient:
    """Client for interacting with Service Registry."""

    def __init__(self, registry_url: str = "http://service-registry:8000"):
        self.registry_url = registry_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=10.0)

    async def register(self, service_info: ServiceInfo) -> bool:
        """Register a service with the registry."""
        try:
            response = await self.client.post(
                f"{self.registry_url}/register",
                json=service_info.dict()
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Failed to register service: {e}")
            return False

    async def deregister(self, service_name: str) -> bool:
        """Deregister a service from the registry."""
        try:
            response = await self.client.delete(
                f"{self.registry_url}/services/{service_name}"
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get information about a specific service."""
        try:
            response = await self.client.get(
                f"{self.registry_url}/services/{service_name}"
            )
            response.raise_for_status()
            return ServiceInfo(**response.json())
        except Exception:
            return None

    async def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services."""
        try:
            response = await self.client.get(f"{self.registry_url}/services")
            response.raise_for_status()
            return [ServiceInfo(**s) for s in response.json()]
        except Exception:
            return []

    async def find_by_capability(self, capability: str) -> List[ServiceInfo]:
        """Find services by capability."""
        try:
            response = await self.client.get(
                f"{self.registry_url}/services/capability/{capability}"
            )
            response.raise_for_status()
            return [ServiceInfo(**s) for s in response.json()]
        except Exception:
            return []

    async def heartbeat(self, service_name: str) -> bool:
        """Send heartbeat for a service."""
        try:
            response = await self.client.post(
                f"{self.registry_url}/heartbeat/{service_name}"
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
