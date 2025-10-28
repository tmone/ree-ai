"""
DB Gateway Service
Central gateway for all database operations
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from typing import List

from shared.models.db_gateway import SearchRequest, SearchResponse, Property
from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 DB Gateway starting up...")
    logger.info(f"PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    logger.info(f"OpenSearch: {settings.OPENSEARCH_HOST}:{settings.OPENSEARCH_PORT}")
    # TODO: Initialize DB connections here
    yield
    logger.info("👋 DB Gateway shutting down...")
    # TODO: Close DB connections here


app = FastAPI(
    title="REE AI - DB Gateway",
    description="Central gateway for database operations",
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


# Mock data for MVP testing
MOCK_PROPERTIES: List[Property] = [
    Property(
        id="prop_001",
        title="Căn hộ 2 phòng ngủ Quận 1 view đẹp",
        price=8500000000,
        location="Quận 1, TP.HCM",
        bedrooms=2,
        area=75.5,
        description="Căn hộ đẹp, nội thất cao cấp, view sông Sài Gòn",
        property_type="apartment",
        score=0.95
    ),
    Property(
        id="prop_002",
        title="Nhà phố 3 tầng Quận 3",
        price=12000000000,
        location="Quận 3, TP.HCM",
        bedrooms=3,
        area=120.0,
        description="Nhà mới xây, thiết kế hiện đại",
        property_type="house",
        score=0.88
    ),
    Property(
        id="prop_003",
        title="Căn hộ 2PN Quận 7 giá tốt",
        price=6000000000,
        location="Quận 7, TP.HCM",
        bedrooms=2,
        area=68.0,
        description="Căn hộ giá rẻ, thích hợp gia đình trẻ",
        property_type="apartment",
        score=0.82
    ),
    Property(
        id="prop_004",
        title="Biệt thự Quận 2 view sông",
        price=25000000000,
        location="Quận 2, TP.HCM",
        bedrooms=5,
        area=250.0,
        description="Biệt thự sang trọng, khu an ninh cao cấp",
        property_type="villa",
        score=0.75
    ),
    Property(
        id="prop_005",
        title="Căn hộ 1PN Quận 1 gần trung tâm",
        price=5500000000,
        location="Quận 1, TP.HCM",
        bedrooms=1,
        area=45.0,
        description="Căn hộ mini, thích hợp người độc thân",
        property_type="apartment",
        score=0.70
    ),
]


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "db-gateway",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "postgres_configured": bool(settings.POSTGRES_HOST),
        "opensearch_configured": bool(settings.OPENSEARCH_HOST),
        "mock_data_count": len(MOCK_PROPERTIES)
    }


@app.post("/search", response_model=SearchResponse)
async def search_properties(request: SearchRequest):
    """
    Search properties using hybrid search (Vector + BM25)
    For MVP: Returns mock data with simple filtering
    """
    start_time = time.time()

    try:
        logger.info(f"🔍 Search Request: query='{request.query}', filters={request.filters}")

        # Simple mock filtering
        results = MOCK_PROPERTIES.copy()

        # Filter by region
        if request.filters.region:
            results = [
                p for p in results
                if request.filters.region.lower() in p.location.lower()
            ]

        # Filter by price range
        if request.filters.min_price is not None:
            results = [p for p in results if p.price >= request.filters.min_price]
        if request.filters.max_price is not None:
            results = [p for p in results if p.price <= request.filters.max_price]

        # Filter by bedrooms
        if request.filters.bedrooms is not None:
            results = [p for p in results if p.bedrooms == request.filters.bedrooms]

        # Filter by property type
        if request.filters.property_type:
            results = [
                p for p in results
                if p.property_type.lower() == request.filters.property_type.lower()
            ]

        # Pagination
        total = len(results)
        results = results[request.offset:request.offset + request.limit]

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Search Results: {len(results)} properties, {elapsed_ms}ms")

        return SearchResponse(
            results=results,
            total=total,
            took_ms=elapsed_ms
        )

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Search Error: {str(e)} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/properties/{property_id}", response_model=Property)
async def get_property(property_id: str):
    """Get single property by ID"""
    try:
        logger.info(f"🔍 Get Property: id={property_id}")

        # Find in mock data
        for prop in MOCK_PROPERTIES:
            if prop.id == property_id:
                logger.info(f"✅ Property found: {prop.title}")
                return prop

        logger.warning(f"⚠️ Property not found: {property_id}")
        raise HTTPException(status_code=404, detail="Property not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
