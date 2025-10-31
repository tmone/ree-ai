"""Service Registry - Central service discovery and registration."""
from typing import Dict, List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.service_registry import ServiceInfo
from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings


class ServiceRegistry:
    """Service Registry for dynamic service discovery."""

    def __init__(self):
        self.name = "service_registry"
        self.version = "1.0.0"
        self.logger = setup_logger(self.name, level=settings.LOG_LEVEL)

        # In-memory service storage (use Redis in production)
        self.services: Dict[str, ServiceInfo] = {}

        # FastAPI app
        self.app = FastAPI(
            title="Service Registry",
            version=self.version,
            description="Central service discovery and registration"
        )

        # Add CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.setup_routes()

    def setup_routes(self):
        """Setup API routes."""

        @self.app.get("/")
        async def root():
            return {
                "service": self.name,
                "version": self.version,
                "registered_services": len(self.services)
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "service": self.name,
                "version": self.version,
                "registered_services": len(self.services)
            }

        @self.app.post("/register")
        async def register_service(service_info: ServiceInfo):
            """Register a new service."""
            service_info.registered_at = datetime.now()
            service_info.last_heartbeat = datetime.now()

            self.services[service_info.name] = service_info
            self.logger.info(
                f"{LogEmoji.SUCCESS} Registered service: {service_info.name} "
                f"at {service_info.host}:{service_info.port}"
            )

            return {
                "status": "registered",
                "service": service_info.name,
                "capabilities": service_info.capabilities
            }

        @self.app.delete("/services/{service_name}")
        async def deregister_service(service_name: str):
            """Deregister a service."""
            if service_name in self.services:
                del self.services[service_name]
                self.logger.info(f"{LogEmoji.INFO} Deregistered service: {service_name}")
                return {"status": "deregistered", "service": service_name}

            raise HTTPException(status_code=404, detail="Service not found")

        @self.app.get("/services")
        async def get_all_services():
            """Get all registered services."""
            return list(self.services.values())

        @self.app.get("/services/{service_name}")
        async def get_service(service_name: str):
            """Get information about a specific service."""
            if service_name in self.services:
                return self.services[service_name]

            raise HTTPException(status_code=404, detail="Service not found")

        @self.app.get("/services/capability/{capability}")
        async def find_by_capability(capability: str):
            """Find services by capability."""
            matching_services = [
                service for service in self.services.values()
                if capability in service.capabilities
            ]
            return matching_services

        @self.app.post("/heartbeat/{service_name}")
        async def heartbeat(service_name: str):
            """Update service heartbeat."""
            if service_name in self.services:
                self.services[service_name].last_heartbeat = datetime.now()
                return {"status": "ok", "service": service_name}

            raise HTTPException(status_code=404, detail="Service not found")

    def run(self):
        """Run the service registry."""
        self.logger.info(f"{LogEmoji.STARTUP} Starting Service Registry v{self.version}")
        uvicorn.run(self.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    registry = ServiceRegistry()
    registry.run()
