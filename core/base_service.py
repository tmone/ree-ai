"""Base service class with auto-registration and standard endpoints."""
import asyncio
import signal
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.service_registry import ServiceInfo, ServiceRegistryClient
from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings


class BaseService:
    """
    Base class for all microservices in REE AI platform.

    Features:
    - Auto-registration with Service Registry
    - Standard health check endpoints
    - Graceful shutdown handling
    - Structured logging
    - CORS middleware
    """

    def __init__(
        self,
        name: str,
        version: str,
        capabilities: List[str],
        port: int = 8080,
        host: str = "0.0.0.0"
    ):
        self.name = name
        self.version = version
        self.capabilities = capabilities
        self.port = port
        self.host = host

        # Setup logger
        self.logger = setup_logger(name, level=settings.LOG_LEVEL)

        # Service registry client
        self.registry_client = ServiceRegistryClient(settings.SERVICE_REGISTRY_URL)

        # FastAPI app with lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.on_startup()
            yield
            # Shutdown
            await self.on_shutdown()

        self.app = FastAPI(
            title=name,
            version=version,
            lifespan=lifespan
        )

        # Add CORS middleware
        # NOTE: Cannot use wildcard "*" with credentials=True
        # Support both dev (Vite on 5173) and production (Open WebUI on 3000)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",  # Open WebUI production
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup custom routes FIRST (to be implemented by subclasses)
        # This allows services to override default routes like "/"
        self.setup_routes()

        # Setup standard routes AFTER custom routes
        # Custom routes defined in setup_routes() will take precedence
        self._setup_standard_routes()

    def _setup_standard_routes(self):
        """
        Setup standard health check and info endpoints.

        Note: No root ("/") route is defined here to allow services
        to define their own custom root routes (e.g., web dashboards).
        API services can use /health and /info for service discovery.
        """

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
                "name": self.name,
                "version": self.version,
                "capabilities": self.capabilities,
                "port": self.port
            }

    def setup_routes(self):
        """
        Setup custom routes for the service.
        Override this method in subclasses.
        """
        pass

    async def on_startup(self):
        """Service startup logic."""
        self.logger.info(f"{LogEmoji.STARTUP} Starting {self.name} v{self.version}")

        # Register with service registry
        service_info = ServiceInfo(
            name=self.name,
            version=self.version,
            host=self.name.replace("_", "-"),  # Docker service name
            port=self.port,
            capabilities=self.capabilities
        )

        success = await self.registry_client.register(service_info)
        if success:
            self.logger.info(f"{LogEmoji.SUCCESS} Registered with Service Registry")
        else:
            self.logger.warning(f"{LogEmoji.WARNING} Failed to register with Service Registry")

        # Start heartbeat task
        asyncio.create_task(self._heartbeat_loop())

        self.logger.info(f"{LogEmoji.SUCCESS} {self.name} started successfully on port {self.port}")

    async def on_shutdown(self):
        """Service shutdown logic."""
        self.logger.info(f"{LogEmoji.WARNING} Shutting down {self.name}")

        # Deregister from service registry
        await self.registry_client.deregister(self.name)

        # Close registry client
        await self.registry_client.close()

        self.logger.info(f"{LogEmoji.SUCCESS} {self.name} shutdown complete")

    async def _heartbeat_loop(self):
        """Send periodic heartbeat to service registry."""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                await self.registry_client.heartbeat(self.name)
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Heartbeat failed: {e}")

    def run(self):
        """Run the service."""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=settings.LOG_LEVEL.lower()
        )


class SimpleService:
    """
    Simplified service without registry integration.
    Use for standalone services or testing.
    """

    def __init__(
        self,
        name: str,
        version: str,
        port: int = 8080,
        host: str = "0.0.0.0"
    ):
        self.name = name
        self.version = version
        self.port = port
        self.host = host

        # Setup logger
        self.logger = setup_logger(name, level=settings.LOG_LEVEL)

        # FastAPI app
        self.app = FastAPI(title=name, version=version)

        # Add CORS middleware
        # NOTE: Cannot use wildcard "*" with credentials=True
        # Support both dev (Vite on 5173) and production (Open WebUI on 3000)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",  # Open WebUI production
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Standard routes
        @self.app.get("/")
        async def root():
            return {"service": self.name, "version": self.version, "status": "running"}

        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "service": self.name, "version": self.version}

        # Setup custom routes
        self.setup_routes()

    def setup_routes(self):
        """Override this in subclasses."""
        pass

    def run(self):
        """Run the service."""
        self.logger.info(f"{LogEmoji.STARTUP} Starting {self.name} v{self.version} on port {self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)
