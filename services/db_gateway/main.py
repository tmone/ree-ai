"""
DB Gateway Service - OpenSearch Integration
Central gateway for all database operations using OpenSearch for flexible property data
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from typing import List, Optional, Dict, Any
from opensearchpy import AsyncOpenSearch

from shared.models.db_gateway import SearchRequest, SearchResponse, PropertyResult, SearchFilters
from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global OpenSearch client
opensearch_client: Optional[AsyncOpenSearch] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global opensearch_client

    logger.info("🚀 DB Gateway starting up (OpenSearch Mode)...")
    logger.info(f"OpenSearch: {settings.OPENSEARCH_HOST}:{settings.OPENSEARCH_PORT}")
    logger.info(f"Properties Index: {settings.OPENSEARCH_PROPERTIES_INDEX}")

    # Initialize OpenSearch client
    try:
        opensearch_client = AsyncOpenSearch(
            hosts=[{
                'host': settings.OPENSEARCH_HOST,
                'port': settings.OPENSEARCH_PORT
            }],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD) if settings.OPENSEARCH_USER else None,
            use_ssl=settings.OPENSEARCH_USE_SSL,
            verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
            ssl_show_warn=False
        )

        # Test connection and check if index exists
        cluster_info = await opensearch_client.info()
        logger.info(f"✅ Connected to OpenSearch cluster: {cluster_info['cluster_name']}")

        # Check if properties index exists
        index_exists = await opensearch_client.indices.exists(index=settings.OPENSEARCH_PROPERTIES_INDEX)
        if index_exists:
            count_response = await opensearch_client.count(index=settings.OPENSEARCH_PROPERTIES_INDEX)
            property_count = count_response['count']
            logger.info(f"✅ Properties index exists! Found {property_count} properties")
        else:
            logger.warning(f"⚠️  Properties index '{settings.OPENSEARCH_PROPERTIES_INDEX}' does not exist yet")
            logger.info("   Index will be created when first property is added")

    except Exception as e:
        logger.error(f"❌ Failed to connect to OpenSearch: {e}")
        logger.warning("⚠️  Continuing with limited functionality")

    yield

    # Cleanup
    logger.info("👋 DB Gateway shutting down...")
    if opensearch_client:
        await opensearch_client.close()
        logger.info("Closed OpenSearch connection")


app = FastAPI(
    title="REE AI - DB Gateway",
    description="Central gateway for database operations using OpenSearch for flexible property data",
    version="3.0.0",
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
        "version": "3.0.0",
        "mode": "OPENSEARCH",
        "storage": "flexible_json"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    property_count = 0
    opensearch_healthy = False
    index_exists = False

    if opensearch_client:
        try:
            # Check cluster health
            await opensearch_client.info()
            opensearch_healthy = True

            # Check if index exists and get count
            index_exists = await opensearch_client.indices.exists(index=settings.OPENSEARCH_PROPERTIES_INDEX)
            if index_exists:
                count_response = await opensearch_client.count(index=settings.OPENSEARCH_PROPERTIES_INDEX)
                property_count = count_response['count']
        except Exception as e:
            logger.error(f"Health check error: {e}")

    return {
        "status": "healthy" if opensearch_healthy else "degraded",
        "opensearch_connected": opensearch_healthy,
        "properties_index_exists": index_exists,
        "property_count": property_count,
        "index_name": settings.OPENSEARCH_PROPERTIES_INDEX,
        "mode": "OPENSEARCH_FLEXIBLE_JSON"
    }


@app.post("/search", response_model=SearchResponse)
async def search_properties(request: SearchRequest):
    """
    Search properties using OpenSearch BM25 full-text search
    Returns flexible JSON property documents with unlimited attributes
    """
    start_time = time.time()

    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch not available")

    try:
        logger.info(f"🔍 Search Request: query='{request.query}', filters={request.filters}")

        # Build OpenSearch query using BM25
        must_clauses = []
        filter_clauses = []

        # BM25 full-text search across title and description
        if request.query:
            must_clauses.append({
                "multi_match": {
                    "query": request.query,
                    "fields": ["title^3", "description", "location^2"],  # Boost title and location
                    "type": "best_fields",
                    "operator": "or"
                }
            })

        # Apply filters
        if request.filters:
            # Region/location filter
            if request.filters.region:
                filter_clauses.append({
                    "match": {
                        "district": request.filters.region
                    }
                })

            # Property type filter
            if request.filters.property_type:
                filter_clauses.append({
                    "term": {
                        "property_type": request.filters.property_type
                    }
                })

            # Price range filter
            if request.filters.min_price or request.filters.max_price:
                price_range = {}
                if request.filters.min_price:
                    price_range["gte"] = request.filters.min_price
                if request.filters.max_price:
                    price_range["lte"] = request.filters.max_price
                filter_clauses.append({
                    "range": {
                        "price": price_range
                    }
                })

            # Bedrooms filter
            if request.filters.min_bedrooms:
                filter_clauses.append({
                    "range": {
                        "bedrooms": {"gte": request.filters.min_bedrooms}
                    }
                })

            # Area filter
            if request.filters.min_area or request.filters.max_area:
                area_range = {}
                if request.filters.min_area:
                    area_range["gte"] = request.filters.min_area
                if request.filters.max_area:
                    area_range["lte"] = request.filters.max_area
                filter_clauses.append({
                    "range": {
                        "area": area_range
                    }
                })

        # Build the complete query
        search_body = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            },
            "size": request.limit,
            "sort": [
                {"_score": {"order": "desc"}},  # Sort by relevance score
                {"created_at": {"order": "desc"}}  # Then by recency
            ]
        }

        # Execute search
        response = await opensearch_client.search(
            index=settings.OPENSEARCH_PROPERTIES_INDEX,
            body=search_body
        )

        # Convert results to PropertyResult objects
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']

            results.append(PropertyResult(
                property_id=source.get('property_id', hit['_id']),
                title=source.get('title', ''),
                price=float(source.get('price', 0)),
                description=source.get('description', ''),
                property_type=source.get('property_type', ''),
                bedrooms=int(source.get('bedrooms', 0)),
                bathrooms=int(source.get('bathrooms', 0)),
                area=float(source.get('area', 0)),
                district=source.get('district', ''),
                city=source.get('city', ''),
                score=float(hit['_score'])
            ))

        execution_time = (time.time() - start_time) * 1000
        total_hits = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']

        logger.info(f"✅ Search completed: {len(results)} results (total: {total_hits}) in {execution_time:.2f}ms")

        return SearchResponse(
            results=results,
            total=total_hits,
            execution_time_ms=execution_time
        )

    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/properties/{property_id}")
async def get_property(property_id: str):
    """Get a single property by ID from OpenSearch"""
    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch not available")

    try:
        # Try to get document by property_id field first
        search_result = await opensearch_client.search(
            index=settings.OPENSEARCH_PROPERTIES_INDEX,
            body={
                "query": {
                    "term": {
                        "property_id": property_id
                    }
                },
                "size": 1
            }
        )

        if search_result['hits']['total']['value'] > 0:
            source = search_result['hits']['hits'][0]['_source']
        else:
            # Fallback: try to get by document _id
            try:
                doc = await opensearch_client.get(
                    index=settings.OPENSEARCH_PROPERTIES_INDEX,
                    id=property_id
                )
                source = doc['_source']
            except:
                raise HTTPException(status_code=404, detail="Property not found")

        # Return all fields from the flexible JSON document
        # This allows unlimited attributes without schema changes
        return {
            "property_id": source.get('property_id', property_id),
            "title": source.get('title', ''),
            "price": source.get('price', 0),
            "description": source.get('description', ''),
            "property_type": source.get('property_type', ''),
            "bedrooms": source.get('bedrooms', 0),
            "bathrooms": source.get('bathrooms', 0),
            "area": source.get('area', 0),
            "district": source.get('district', ''),
            "city": source.get('city', ''),
            "url": source.get('url', ''),
            "source": source.get('source', ''),
            # Include ALL other flexible attributes from OpenSearch
            **{k: v for k, v in source.items() if k not in [
                'property_id', 'title', 'price', 'description', 'property_type',
                'bedrooms', 'bathrooms', 'area', 'district', 'city', 'url', 'source'
            ]}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get property failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics using OpenSearch aggregations"""
    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch not available")

    try:
        # Check if index exists
        index_exists = await opensearch_client.indices.exists(index=settings.OPENSEARCH_PROPERTIES_INDEX)
        if not index_exists:
            return {
                "total_properties": 0,
                "by_type": {},
                "by_district": {},
                "by_city": {}
            }

        # Use OpenSearch aggregations to get statistics
        response = await opensearch_client.search(
            index=settings.OPENSEARCH_PROPERTIES_INDEX,
            body={
                "size": 0,  # We only want aggregations, not documents
                "aggs": {
                    "by_type": {
                        "terms": {
                            "field": "property_type.keyword",
                            "size": 50
                        }
                    },
                    "by_district": {
                        "terms": {
                            "field": "district.keyword",
                            "size": 50
                        }
                    },
                    "by_city": {
                        "terms": {
                            "field": "city.keyword",
                            "size": 50
                        }
                    }
                }
            }
        )

        # Extract aggregation results
        total = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
        by_type = {bucket['key']: bucket['doc_count'] for bucket in response['aggregations']['by_type']['buckets']}
        by_district = {bucket['key']: bucket['doc_count'] for bucket in response['aggregations']['by_district']['buckets']}
        by_city = {bucket['key']: bucket['doc_count'] for bucket in response['aggregations']['by_city']['buckets']}

        return {
            "total_properties": total,
            "by_type": by_type,
            "by_district": by_district,
            "by_city": by_city
        }

    except Exception as e:
        logger.error(f"❌ Get stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
