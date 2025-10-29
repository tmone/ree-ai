"""
API Gateway Service - Layer 0
- Rate limiting
- Authentication/Authorization
- Request routing
- Response caching
- Metrics collection
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import defaultdict
import asyncio

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from jose import jwt, JWTError

from shared.utils.logger import get_logger
from shared.config import get_settings

# Logger
logger = get_logger(__name__)
settings = get_settings()

# App
app = FastAPI(
    title="REE AI - API Gateway",
    description="API Gateway with rate limiting, authentication, and routing",
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


# ============================================================
# MODELS
# ============================================================

class TokenData(BaseModel):
    """JWT Token data"""
    user_id: str
    email: Optional[str] = None
    role: str = "user"
    exp: Optional[datetime] = None


class RateLimitConfig(BaseModel):
    """Rate limit configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000


class ServiceRoute(BaseModel):
    """Service routing configuration"""
    name: str
    url: str
    path_prefix: str
    requires_auth: bool = True
    rate_limit: Optional[RateLimitConfig] = None


# ============================================================
# RATE LIMITER
# ============================================================

class RateLimiter:
    """In-memory rate limiter (use Redis in production)"""

    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        client_id: str,
        config: RateLimitConfig
    ) -> tuple[bool, Optional[str]]:
        """Check if request is within rate limits"""
        async with self.lock:
            now = datetime.now()

            # Clean old requests
            if client_id in self.requests:
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if now - req_time < timedelta(days=1)
                ]

            recent_requests = self.requests[client_id]

            # Check per-minute limit
            minute_ago = now - timedelta(minutes=1)
            minute_count = sum(1 for t in recent_requests if t > minute_ago)
            if minute_count >= config.requests_per_minute:
                return False, "Rate limit exceeded: requests per minute"

            # Check per-hour limit
            hour_ago = now - timedelta(hours=1)
            hour_count = sum(1 for t in recent_requests if t > hour_ago)
            if hour_count >= config.requests_per_hour:
                return False, "Rate limit exceeded: requests per hour"

            # Check per-day limit
            day_count = len(recent_requests)
            if day_count >= config.requests_per_day:
                return False, "Rate limit exceeded: requests per day"

            # Add current request
            self.requests[client_id].append(now)

            return True, None


# Global rate limiter
rate_limiter = RateLimiter()


# ============================================================
# SERVICE REGISTRY
# ============================================================

# Service routes configuration
SERVICE_ROUTES: Dict[str, ServiceRoute] = {
    "orchestrator": ServiceRoute(
        name="orchestrator",
        url="http://orchestrator:8080",
        path_prefix="/orchestrate",
        requires_auth=True,
        rate_limit=RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            requests_per_day=5000
        )
    ),
    "rag": ServiceRoute(
        name="rag_service",
        url="http://rag-service:8080",
        path_prefix="/rag",
        requires_auth=True,
        rate_limit=RateLimitConfig(
            requests_per_minute=20,
            requests_per_hour=300,
            requests_per_day=3000
        )
    ),
    "classification": ServiceRoute(
        name="classification",
        url="http://classification:8080",
        path_prefix="/classify",
        requires_auth=True,
        rate_limit=RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
    ),
    "semantic_chunking": ServiceRoute(
        name="semantic_chunking",
        url="http://semantic-chunking:8080",
        path_prefix="/chunk",
        requires_auth=True,
        rate_limit=RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
    ),
    "db_gateway": ServiceRoute(
        name="db_gateway",
        url="http://db-gateway:8080",
        path_prefix="/db",
        requires_auth=True,
        rate_limit=RateLimitConfig(
            requests_per_minute=100,
            requests_per_hour=2000,
            requests_per_day=20000
        )
    ),
}


# ============================================================
# AUTHENTICATION
# ============================================================

def verify_token(authorization: Optional[str] = Header(None)) -> TokenData:
    """Verify JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )

        # Decode JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        token_data = TokenData(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("role", "user"),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )

        return token_data

    except (ValueError, JWTError) as e:
        logger.error(f"❌ Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


async def verify_rate_limit(
    request: Request,
    token_data: TokenData,
    route: ServiceRoute
):
    """Verify rate limits"""
    if not route.rate_limit:
        return

    # Use user_id as client identifier
    client_id = token_data.user_id

    allowed, error = await rate_limiter.check_rate_limit(
        client_id,
        route.rate_limit
    )

    if not allowed:
        logger.warning(f"⚠️ Rate limit exceeded for user {client_id}: {error}")
        raise HTTPException(
            status_code=429,
            detail=error,
            headers={"Retry-After": "60"}
        )


# ============================================================
# ROUTING
# ============================================================

@app.api_route(
    "/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def route_request(
    service_name: str,
    path: str,
    request: Request,
    token_data: Optional[TokenData] = Depends(verify_token)
):
    """Route requests to appropriate services"""

    # Find service route
    route = SERVICE_ROUTES.get(service_name)
    if not route:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )

    # Check authentication
    if route.requires_auth and not token_data:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    # Check rate limits
    if token_data:
        await verify_rate_limit(request, token_data, route)

    # Forward request
    try:
        target_url = f"{route.url}/{path}"

        logger.info(f"🔀 Routing {request.method} {service_name}/{path} → {target_url}")

        # Get request body
        body = await request.body()

        # Forward headers (exclude host)
        headers = dict(request.headers)
        headers.pop("host", None)

        # Add user context
        if token_data:
            headers["X-User-ID"] = token_data.user_id
            headers["X-User-Role"] = token_data.role

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                params=request.query_params
            )

            return JSONResponse(
                content=response.json() if response.headers.get("content-type") == "application/json" else {"data": response.text},
                status_code=response.status_code,
                headers=dict(response.headers)
            )

    except httpx.TimeoutException:
        logger.error(f"⏱️ Timeout calling {service_name}")
        raise HTTPException(
            status_code=504,
            detail="Gateway timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"❌ Error calling {service_name}: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="Bad gateway"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# HEALTH & METRICS
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api_gateway",
        "timestamp": datetime.now().isoformat(),
        "routes": len(SERVICE_ROUTES)
    }


@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics"""
    total_requests = sum(len(reqs) for reqs in rate_limiter.requests.values())

    return {
        "total_clients": len(rate_limiter.requests),
        "total_requests": total_requests,
        "services": len(SERVICE_ROUTES),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/routes")
async def list_routes():
    """List all available routes"""
    return {
        "routes": [
            {
                "service": name,
                "path_prefix": route.path_prefix,
                "requires_auth": route.requires_auth,
                "rate_limit": route.rate_limit.dict() if route.rate_limit else None
            }
            for name, route in SERVICE_ROUTES.items()
        ]
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 API Gateway starting...")
    logger.info(f"📊 Loaded {len(SERVICE_ROUTES)} service routes")
    logger.info("✅ API Gateway ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
