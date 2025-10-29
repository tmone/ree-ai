"""
Admin Dashboard API Service
Backend API for the Admin Dashboard
- System health monitoring
- Service status
- User management
- Analytics & metrics
- Configuration management
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import httpx
import asyncpg

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from shared.utils.logger import get_logger
from shared.config import get_settings

# Logger & Settings
logger = get_logger(__name__)
settings = get_settings()

# App
app = FastAPI(
    title="REE AI - Admin Dashboard",
    description="Admin dashboard for system monitoring and management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database pool
db_pool: Optional[asyncpg.Pool] = None


# ============================================================
# MODELS
# ============================================================

class ServiceStatus(BaseModel):
    """Service status"""
    name: str
    url: str
    status: str  # "healthy", "unhealthy", "unknown"
    response_time_ms: Optional[float] = None
    last_checked: datetime
    error: Optional[str] = None


class SystemHealth(BaseModel):
    """Overall system health"""
    status: str  # "healthy", "degraded", "down"
    total_services: int
    healthy_services: int
    unhealthy_services: int
    services: List[ServiceStatus]
    timestamp: datetime


class UserStats(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_week: int


class ServiceMetrics(BaseModel):
    """Service metrics"""
    service_name: str
    total_requests: int
    success_rate: float
    avg_response_time_ms: float
    error_count: int


class SystemMetrics(BaseModel):
    """System-wide metrics"""
    timestamp: datetime
    total_requests_24h: int
    total_errors_24h: int
    avg_response_time_ms: float
    top_services: List[ServiceMetrics]


# ============================================================
# SERVICE REGISTRY
# ============================================================

SERVICES = {
    "service_registry": "http://service-registry:8000",
    "api_gateway": "http://api-gateway:8080",
    "auth_service": "http://auth-service:8080",
    "core_gateway": "http://core-gateway:8080",
    "db_gateway": "http://db-gateway:8080",
    "orchestrator": "http://orchestrator:8080",
    "rag_service": "http://rag-service:8080",
    "semantic_chunking": "http://semantic-chunking:8080",
    "classification": "http://classification:8080",
    "attribute_extraction": "http://attribute-extraction:8080",
    "completeness_check": "http://completeness-check:8080",
    "price_suggestion": "http://price-suggestion:8080",
    "reranking": "http://reranking:8080",
}


# ============================================================
# DATABASE
# ============================================================

async def init_db():
    """Initialize database connection"""
    global db_pool

    try:
        db_pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=2,
            max_size=10
        )
        logger.info("✅ Database initialized")

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")


async def close_db():
    """Close database connection"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Database connection closed")


# ============================================================
# HEALTH CHECKS
# ============================================================

async def check_service_health(name: str, url: str) -> ServiceStatus:
    """Check health of a single service"""
    start_time = datetime.now()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return ServiceStatus(
                    name=name,
                    url=url,
                    status="healthy",
                    response_time_ms=response_time,
                    last_checked=datetime.now()
                )
            else:
                return ServiceStatus(
                    name=name,
                    url=url,
                    status="unhealthy",
                    response_time_ms=response_time,
                    last_checked=datetime.now(),
                    error=f"HTTP {response.status_code}"
                )

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return ServiceStatus(
            name=name,
            url=url,
            status="unhealthy",
            response_time_ms=response_time,
            last_checked=datetime.now(),
            error=str(e)
        )


# ============================================================
# ENDPOINTS - HEALTH MONITORING
# ============================================================

@app.get("/api/health/system", response_model=SystemHealth)
async def get_system_health():
    """Get overall system health"""
    logger.info("🏥 Checking system health...")

    # Check all services
    service_statuses = []
    for name, url in SERVICES.items():
        status = await check_service_health(name, url)
        service_statuses.append(status)

    # Calculate overall health
    healthy_count = sum(1 for s in service_statuses if s.status == "healthy")
    total_count = len(service_statuses)

    if healthy_count == total_count:
        overall_status = "healthy"
    elif healthy_count >= total_count * 0.7:
        overall_status = "degraded"
    else:
        overall_status = "down"

    logger.info(f"✅ System health: {overall_status} ({healthy_count}/{total_count})")

    return SystemHealth(
        status=overall_status,
        total_services=total_count,
        healthy_services=healthy_count,
        unhealthy_services=total_count - healthy_count,
        services=service_statuses,
        timestamp=datetime.now()
    )


@app.get("/api/health/service/{service_name}", response_model=ServiceStatus)
async def get_service_health(service_name: str):
    """Get health of specific service"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = SERVICES[service_name]
    status = await check_service_health(service_name, url)

    return status


# ============================================================
# ENDPOINTS - USER MANAGEMENT
# ============================================================

@app.get("/api/users/stats", response_model=UserStats)
async def get_user_stats():
    """Get user statistics"""
    try:
        if not db_pool:
            raise HTTPException(status_code=503, detail="Database not available")

        async with db_pool.acquire() as conn:
            # Total users
            total = await conn.fetchval("SELECT COUNT(*) FROM users")

            # Active users (logged in last 7 days)
            active = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE updated_at > NOW() - INTERVAL '7 days'
            """)

            # New users today
            today = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE created_at::date = CURRENT_DATE
            """)

            # New users this week
            week = await conn.fetchval("""
                SELECT COUNT(*) FROM users
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)

            return UserStats(
                total_users=total or 0,
                active_users=active or 0,
                new_users_today=today or 0,
                new_users_week=week or 0
            )

    except Exception as e:
        logger.error(f"❌ Failed to get user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users")
async def list_users(limit: int = 50, offset: int = 0):
    """List users"""
    try:
        if not db_pool:
            raise HTTPException(status_code=503, detail="Database not available")

        async with db_pool.acquire() as conn:
            users = await conn.fetch("""
                SELECT user_id, email, full_name, role, is_active, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)

            return {
                "users": [dict(u) for u in users],
                "limit": limit,
                "offset": offset
            }

    except Exception as e:
        logger.error(f"❌ Failed to list users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ENDPOINTS - METRICS
# ============================================================

@app.get("/api/metrics/system", response_model=SystemMetrics)
async def get_system_metrics():
    """Get system-wide metrics"""
    # Mock data for now - integrate with Prometheus in production
    return SystemMetrics(
        timestamp=datetime.now(),
        total_requests_24h=15234,
        total_errors_24h=45,
        avg_response_time_ms=125.5,
        top_services=[
            ServiceMetrics(
                service_name="api_gateway",
                total_requests=5234,
                success_rate=99.1,
                avg_response_time_ms=45.2,
                error_count=15
            ),
            ServiceMetrics(
                service_name="orchestrator",
                total_requests=3421,
                success_rate=98.8,
                avg_response_time_ms=178.3,
                error_count=20
            ),
            ServiceMetrics(
                service_name="rag_service",
                total_requests=2156,
                success_rate=99.5,
                avg_response_time_ms=523.1,
                error_count=10
            )
        ]
    )


# ============================================================
# ENDPOINTS - CONFIGURATION
# ============================================================

@app.get("/api/config")
async def get_configuration():
    """Get system configuration"""
    return {
        "environment": "production" if not settings.DEBUG else "development",
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "services": {
            "core_gateway": {
                "mode": "real" if settings.USE_REAL_CORE_GATEWAY else "mock"
            },
            "db_gateway": {
                "mode": "real" if settings.USE_REAL_DB_GATEWAY else "mock"
            }
        },
        "database": {
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB
        }
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    """Admin Dashboard Home"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>REE AI - Admin Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; margin: 0; }
        .subtitle { color: #666; margin-top: 5px; }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card h2 { margin-top: 0; color: #333; }
        .api-link {
            display: block;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            margin: 10px 0;
            text-decoration: none;
            color: #0066cc;
        }
        .api-link:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎛️ REE AI Admin Dashboard</h1>
        <p class="subtitle">System Monitoring & Management</p>
    </div>

    <div class="cards">
        <div class="card">
            <h2>🏥 Health Monitoring</h2>
            <a class="api-link" href="/api/health/system">System Health</a>
            <a class="api-link" href="/api/health/service/api_gateway">API Gateway Status</a>
        </div>

        <div class="card">
            <h2>👥 User Management</h2>
            <a class="api-link" href="/api/users/stats">User Statistics</a>
            <a class="api-link" href="/api/users">User List</a>
        </div>

        <div class="card">
            <h2>📊 Metrics</h2>
            <a class="api-link" href="/api/metrics/system">System Metrics</a>
            <a class="api-link" href="http://localhost:9090" target="_blank">Prometheus ↗</a>
            <a class="api-link" href="http://localhost:3001" target="_blank">Grafana ↗</a>
        </div>

        <div class="card">
            <h2>⚙️ Configuration</h2>
            <a class="api-link" href="/api/config">System Configuration</a>
            <a class="api-link" href="/docs">API Documentation</a>
        </div>
    </div>
</body>
</html>
    """)


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "admin_dashboard",
        "database": "connected" if db_pool else "disconnected",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# STARTUP & SHUTDOWN
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Admin Dashboard starting...")
    await init_db()
    logger.info("✅ Admin Dashboard ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Admin Dashboard shutting down...")
    await close_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
