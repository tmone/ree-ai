"""
Base Service Class - All microservices inherit from this
Provides:
- Service registration
- Health checks
- Logging
- Graceful shutdown
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import Optional, List
import httpx
import os
import signal
import sys

from core.service_registry import ServiceInfo
from shared.utils.logger import setup_logger


class BaseService:
    """
    Base class for all microservices

    Usage:
        class MyService(BaseService):
            def __init__(self):
                super().__init__(
                    name="my_service",
                    version="1.0.0",
                    capabilities=["my_capability"]
                )

            def setup_routes(self):
                @self.app.get("/my-endpoint")
                async def my_endpoint():
                    return {"message": "Hello"}

        if __name__ == "__main__":
            service = MyService()
            service.run()
    """

    def __init__(
        self,
        name: str,
        version: str,
        capabilities: List[str] = [],
        port: int = 8080,
        registry_url: str = None
    ):
        self.name = name
        self.version = version
        self.capabilities = capabilities
        self.port = port
        self.registry_url = registry_url or os.getenv(
            "REGISTRY_URL",
            "http://service-registry:8000"
        )

        self.logger = setup_logger(name)

        # Create FastAPI app with lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info(f"🚀 {self.name} v{self.version} starting up...")
            await self.on_startup()
            yield
            # Shutdown
            self.logger.info(f"👋 {self.name} shutting down...")
            await self.on_shutdown()

        self.app = FastAPI(
            title=f"REE AI - {self.name}",
            version=self.version,
            lifespan=lifespan
        )

        # Setup default routes
        self._setup_default_routes()

        # Let subclass setup custom routes
        self.setup_routes()

        # Handle shutdown signals
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _setup_default_routes(self):
        """Setup default routes all services have"""

        @self.app.get("/")
        async def root():
            return {
                "service": self.name,
                "version": self.version,
                "status": "healthy",
                "capabilities": self.capabilities
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "service": self.name,
                "version": self.version
            }

        @self.app.get("/info")
        async def info():
            return {
                "service": self.name,
                "version": self.version,
                "capabilities": self.capabilities,
                "port": self.port
            }

    def setup_routes(self):
        """Override this to add custom routes"""
        pass

    async def on_startup(self):
        """
        Called on service startup
        Override to add custom startup logic
        """
        # Register with service registry
        await self._register_service()

    async def on_shutdown(self):
        """
        Called on service shutdown
        Override to add custom shutdown logic
        """
        # Deregister from service registry
        await self._deregister_service()

    async def _register_service(self):
        """Register this service with the registry"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get service host from environment or use service name
                host = os.getenv("SERVICE_HOST", self.name.replace("_", "-"))

                service_info = ServiceInfo(
                    name=self.name,
                    host=host,
                    port=self.port,
                    version=self.version,
                    capabilities=self.capabilities
                )

                response = await client.post(
                    f"{self.registry_url}/register",
                    json=service_info.dict()
                )

                if response.status_code == 200:
                    self.logger.info(f"✅ Registered with service registry at {self.registry_url}")
                else:
                    self.logger.warning(f"⚠️ Failed to register with service registry: {response.status_code}")

        except Exception as e:
            self.logger.warning(f"⚠️ Could not register with service registry: {e}")
            self.logger.info("Service will run without registration (standalone mode)")

    async def _deregister_service(self):
        """Deregister this service from the registry"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{self.registry_url}/deregister",
                    json={"service_name": self.name}
                )
                self.logger.info(f"✅ Deregistered from service registry")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not deregister: {e}")

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    def run(self, host: str = "0.0.0.0"):
        """Run the service"""
        import uvicorn
        self.logger.info(f"🌐 Starting {self.name} on {host}:{self.port}")
        uvicorn.run(self.app, host=host, port=self.port)


# Example usage in documentation
if __name__ == "__main__":
    # This is just for documentation
    # Real services should inherit from BaseService

    class ExampleService(BaseService):
        def __init__(self):
            super().__init__(
                name="example_service",
                version="1.0.0",
                capabilities=["example"]
            )

        def setup_routes(self):
            @self.app.get("/example")
            async def example_endpoint():
                return {"message": "This is an example"}

    service = ExampleService()
    service.run()
