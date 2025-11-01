"""
DB Gateway Service - NOW WITH REAL POSTGRES INTEGRATION
Central gateway for all database operations
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import re
from typing import List, Optional
import asyncpg

from shared.models.db_gateway import SearchRequest, SearchResponse, PropertyResult, SearchFilters
from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global database connection pool
db_pool: Optional[asyncpg.Pool] = None


def parse_vietnamese_price(price_str: str) -> float:
    """
    Parse Vietnamese price format to numeric value
    Examples: "5 tỷ" -> 5000000000, "3,5 tỷ" -> 3500000000, "Giá thỏa thuận" -> 0
    """
    if not price_str or price_str == "Giá thỏa thuận":
        return 0.0

    # Remove all whitespace
    price_str = price_str.strip()

    # Extract number and unit
    # Match patterns like "5 tỷ", "3,5 tỷ", "500 triệu", "18 tỷ"
    match = re.search(r'([\d,\.]+)\s*(tỷ|triệu|trieu|ty)?', price_str, re.IGNORECASE)
    if not match:
        return 0.0

    number_str = match.group(1).replace(',', '.')
    unit = match.group(2).lower() if match.group(2) else ''

    try:
        number = float(number_str)
    except:
        return 0.0

    # Convert to VND
    if 'tỷ' in unit or 'ty' in unit:
        return number * 1_000_000_000  # billion
    elif 'triệu' in unit or 'trieu' in unit:
        return number * 1_000_000  # million
    else:
        return number


def parse_area(area_str: str) -> float:
    """
    Parse area format to numeric value
    Examples: "62,5 m²" -> 62.5, "120 m²" -> 120.0
    """
    if not area_str:
        return 0.0

    # Extract number from string like "62,5 m²" or "120 m²"
    match = re.search(r'([\d,\.]+)', area_str)
    if not match:
        return 0.0

    number_str = match.group(1).replace(',', '.')
    try:
        return float(number_str)
    except:
        return 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global db_pool

    logger.info("🚀 DB Gateway starting up (REAL POSTGRES MODE)...")
    logger.info(f"PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    logger.info(f"Database: {settings.POSTGRES_DB}")

    # Initialize Postgres connection pool
    try:
        db_pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=2,
            max_size=10,
            command_timeout=30
        )

        # Test connection
        async with db_pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM properties")
            logger.info(f"✅ Connected to Postgres! Found {count} properties in database")

    except Exception as e:
        logger.error(f"❌ Failed to connect to Postgres: {e}")
        logger.warning("⚠️  Continuing with limited functionality")

    yield

    # Cleanup
    logger.info("👋 DB Gateway shutting down...")
    if db_pool:
        await db_pool.close()
        logger.info("Closed database connection pool")


app = FastAPI(
    title="REE AI - DB Gateway",
    description="Central gateway for database operations (REAL DATA)",
    version="2.0.0",
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


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "db-gateway",
        "status": "healthy",
        "version": "2.0.0",
        "mode": "REAL_DATA"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    property_count = 0
    postgres_healthy = False

    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                property_count = await conn.fetchval("SELECT COUNT(*) FROM properties")
                postgres_healthy = True
        except Exception as e:
            logger.error(f"Health check error: {e}")

    return {
        "status": "healthy" if postgres_healthy else "degraded",
        "postgres_connected": postgres_healthy,
        "opensearch_configured": bool(settings.OPENSEARCH_HOST),
        "real_data_count": property_count,
        "mode": "REAL_DATA"
    }


@app.post("/search", response_model=SearchResponse)
async def search_properties(request: SearchRequest):
    """
    Search properties using Postgres full-text search
    Returns REAL property data from crawled database
    """
    start_time = time.time()

    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        logger.info(f"🔍 Search Request: query='{request.query}', filters={request.filters}")

        # Build SQL query
        conditions = []
        params = []
        param_count = 1

        # Simple text search across title, location, description
        if request.query:
            conditions.append(f"""
                (title ILIKE ${param_count} OR
                 location ILIKE ${param_count} OR
                 description ILIKE ${param_count})
            """)
            params.append(f"%{request.query}%")
            param_count += 1

        # Filter by region/location
        if request.filters and request.filters.region:
            conditions.append(f"location ILIKE ${param_count}")
            params.append(f"%{request.filters.region}%")
            param_count += 1

        # Filter by property type
        if request.filters and request.filters.property_type:
            conditions.append(f"property_type = ${param_count}")
            params.append(request.filters.property_type)
            param_count += 1

        # Build WHERE clause
        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        # Execute query
        query_sql = f"""
            SELECT id, title, price, location, bedrooms, bathrooms, area,
                   description, property_type, url
            FROM properties
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT {request.limit}
        """

        async with db_pool.acquire() as conn:
            rows = await conn.fetch(query_sql, *params)

        # Convert to Property objects
        results = []
        for row in rows:
            # Parse price and area
            price = parse_vietnamese_price(row['price']) if row['price'] else 0.0
            area = parse_area(row['area']) if row['area'] else 0.0

            # Apply filters (if filters provided)
            if request.filters:
                if request.filters.min_price and price < request.filters.min_price:
                    continue
                if request.filters.max_price and price > request.filters.max_price:
                    continue
                if request.filters.min_bedrooms and row['bedrooms'] < request.filters.min_bedrooms:
                    continue
                if request.filters.min_area and area < request.filters.min_area:
                    continue
                if request.filters.max_area and area > request.filters.max_area:
                    continue

            results.append(PropertyResult(
                property_id=str(row['id']),
                title=row['title'],
                price=price,
                description=row['description'] or "",
                property_type=row['property_type'] or "",
                bedrooms=row['bedrooms'] or 0,
                bathrooms=row['bathrooms'] or 0,
                area=area,
                district=row['location'] or "",  # Using location as district for now
                city="",  # TODO: Extract city from location
                score=0.9  # Simple scoring for now
            ))

        # Apply limit after filtering
        results = results[:request.limit]

        execution_time = (time.time() - start_time) * 1000

        logger.info(f"✅ Search completed: {len(results)} results in {execution_time:.2f}ms")

        return SearchResponse(
            results=results,
            total=len(results),
            execution_time_ms=execution_time
        )

    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/properties/{property_id}")
async def get_property(property_id: int):
    """Get a single property by ID"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT id, title, price, location, bedrooms, bathrooms, area,
                          description, property_type, url, source
                   FROM properties WHERE id = $1""",
                property_id
            )

        if not row:
            raise HTTPException(status_code=404, detail="Property not found")

        price = parse_vietnamese_price(row['price']) if row['price'] else 0.0
        area = parse_area(row['area']) if row['area'] else 0.0

        return {
            "id": row['id'],
            "title": row['title'],
            "price": price,
            "price_formatted": row['price'],
            "location": row['location'],
            "bedrooms": row['bedrooms'],
            "bathrooms": row['bathrooms'],
            "area": area,
            "area_formatted": row['area'],
            "description": row['description'],
            "property_type": row['property_type'],
            "url": row['url'],
            "source": row['source']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get property failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        async with db_pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM properties")
            by_type = await conn.fetch(
                "SELECT property_type, COUNT(*) as count FROM properties GROUP BY property_type"
            )
            by_location = await conn.fetch(
                """SELECT
                    CASE
                        WHEN location LIKE '%Hồ Chí Minh%' THEN 'Hồ Chí Minh'
                        WHEN location LIKE '%Hà Nội%' THEN 'Hà Nội'
                        WHEN location LIKE '%Đà Nẵng%' THEN 'Đà Nẵng'
                        ELSE 'Khác'
                    END as region,
                    COUNT(*) as count
                FROM properties
                GROUP BY region
                ORDER BY count DESC"""
            )

        return {
            "total_properties": total,
            "by_type": {row['property_type']: row['count'] for row in by_type},
            "by_region": {row['region']: row['count'] for row in by_location}
        }

    except Exception as e:
        logger.error(f"❌ Get stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
