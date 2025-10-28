"""
Service Registry - Central service discovery
This is the FIRST service that must start
All other services register themselves here
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
import asyncio

import sys
sys.path.insert(0, '/app')

from core.service_registry import ServiceRegistry, ServiceInfo
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global registry
registry = ServiceRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    logger.info("🚀 Service Registry starting up...")
    logger.info("This is the central service discovery system")

    # Start health check background task
    health_task = asyncio.create_task(registry.start_health_checks())

    yield

    logger.info("👋 Service Registry shutting down...")
    health_task.cancel()


app = FastAPI(
    title="REE AI - Service Registry",
    description="Central service discovery and registration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    name: str
    host: str
    port: int
    version: str
    capabilities: List[str] = []
    metadata: dict = {}


class DeregisterRequest(BaseModel):
    service_name: str


@app.get("/")
async def root():
    """Root endpoint"""
    stats = registry.get_stats()
    return {
        "service": "service-registry",
        "status": "healthy",
        "version": "1.0.0",
        "stats": stats
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/register")
async def register_service(request: RegisterRequest):
    """
    Register a new service

    Called by services on startup
    """
    logger.info(f"📝 Registration request from: {request.name}")

    service = ServiceInfo(
        name=request.name,
        host=request.host,
        port=request.port,
        version=request.version,
        capabilities=request.capabilities,
        metadata=request.metadata
    )

    success = await registry.register(service)

    if success:
        logger.info(f"✅ Service registered: {request.name} at http://{request.host}:{request.port}")
        return {
            "status": "registered",
            "service": request.name,
            "url": f"http://{request.host}:{request.port}"
        }
    else:
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/deregister")
async def deregister_service(request: DeregisterRequest):
    """
    Deregister a service

    Called by services on shutdown
    """
    logger.info(f"📝 Deregistration request from: {request.service_name}")

    success = await registry.deregister(request.service_name)

    if success:
        logger.info(f"✅ Service deregistered: {request.service_name}")
        return {"status": "deregistered", "service": request.service_name}
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/heartbeat")
async def heartbeat(service_name: str):
    """
    Receive heartbeat from service

    Services should send heartbeats periodically
    """
    success = await registry.heartbeat(service_name)

    if success:
        return {"status": "ok", "service": service_name}
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.get("/services")
async def list_services(
    capability: Optional[str] = None,
    status: Optional[str] = "healthy"
):
    """
    List all registered services

    Query params:
    - capability: Filter by capability (e.g., "text_processing")
    - status: Filter by status (e.g., "healthy", "unhealthy")
    """
    services = await registry.list_services(capability=capability, status=status)

    return {
        "count": len(services),
        "services": [
            {
                "name": s.name,
                "url": s.base_url,
                "version": s.version,
                "capabilities": s.capabilities,
                "status": s.status,
                "last_heartbeat": s.last_heartbeat.isoformat()
            }
            for s in services
        ]
    }


@app.get("/services/{service_name}")
async def get_service(service_name: str):
    """Get specific service info"""
    service = await registry.get_service(service_name)

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {
        "name": service.name,
        "url": service.base_url,
        "version": service.version,
        "capabilities": service.capabilities,
        "status": service.status,
        "last_heartbeat": service.last_heartbeat.isoformat(),
        "metadata": service.metadata
    }


@app.get("/stats")
async def get_stats():
    """Get registry statistics"""
    return registry.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
