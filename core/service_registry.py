"""
Service Registry - Central service discovery for microservices
All services register themselves here on startup
"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import asyncio
import httpx


class ServiceInfo(BaseModel):
    """Service registration information"""
    name: str
    host: str
    port: int
    version: str
    health_endpoint: str = "/health"
    capabilities: List[str] = []
    metadata: Dict = {}
    registered_at: datetime = datetime.now()
    last_heartbeat: datetime = datetime.now()
    status: str = "healthy"  # healthy, unhealthy, unknown

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ServiceRegistry:
    """
    Service Registry for microservices discovery

    Pattern: Service Registry Pattern
    - Services register on startup
    - Send heartbeats periodically
    - Orchestrator queries available services
    """

    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        self._health_check_interval = 30  # seconds
        self._health_check_task = None

    async def register(self, service: ServiceInfo) -> bool:
        """
        Register a new service

        Example:
            await registry.register(ServiceInfo(
                name="semantic_chunking",
                host="semantic-chunking",
                port=8080,
                version="1.0.0",
                capabilities=["text_processing", "chunking"]
            ))
        """
        self._services[service.name] = service
        print(f"✅ Service registered: {service.name} at {service.base_url}")
        return True

    async def deregister(self, service_name: str) -> bool:
        """Deregister a service"""
        if service_name in self._services:
            del self._services[service_name]
            print(f"❌ Service deregistered: {service_name}")
            return True
        return False

    async def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service info by name"""
        return self._services.get(service_name)

    async def list_services(
        self,
        capability: Optional[str] = None,
        status: Optional[str] = "healthy"
    ) -> List[ServiceInfo]:
        """
        List all services, optionally filter by capability

        Example:
            # Get all text processing services
            services = await registry.list_services(capability="text_processing")
        """
        services = list(self._services.values())

        if capability:
            services = [s for s in services if capability in s.capabilities]

        if status:
            services = [s for s in services if s.status == status]

        return services

    async def heartbeat(self, service_name: str) -> bool:
        """Update service heartbeat"""
        if service_name in self._services:
            self._services[service_name].last_heartbeat = datetime.now()
            return True
        return False

    async def check_health(self, service: ServiceInfo) -> bool:
        """Check if service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{service.base_url}{service.health_endpoint}"
                )
                if response.status_code == 200:
                    service.status = "healthy"
                    return True
        except Exception as e:
            print(f"⚠️ Health check failed for {service.name}: {e}")

        service.status = "unhealthy"
        return False

    async def start_health_checks(self):
        """Start periodic health checks for all services"""
        while True:
            for service in self._services.values():
                await self.check_health(service)
            await asyncio.sleep(self._health_check_interval)

    def get_stats(self) -> Dict:
        """Get registry statistics"""
        total = len(self._services)
        healthy = len([s for s in self._services.values() if s.status == "healthy"])
        unhealthy = len([s for s in self._services.values() if s.status == "unhealthy"])

        return {
            "total_services": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "services": {
                name: {
                    "status": service.status,
                    "base_url": service.base_url,
                    "capabilities": service.capabilities
                }
                for name, service in self._services.items()
            }
        }


# Global registry instance
registry = ServiceRegistry()
