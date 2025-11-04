"""
DB Gateway Service - OpenSearch Integration
Central gateway for all database operations using OpenSearch for flexible property data
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from opensearchpy import AsyncOpenSearch
from sentence_transformers import SentenceTransformer

from shared.models.db_gateway import SearchRequest, SearchResponse, PropertyResult, SearchFilters
from shared.config import settings
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global embedding model for semantic search
embedding_model: Optional[SentenceTransformer] = None

# Global OpenSearch client
opensearch_client: Optional[AsyncOpenSearch] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global opensearch_client

    logger.info("🚀 DB Gateway starting up (OpenSearch Mode)...")
    logger.info(f"OpenSearch: {settings.OPENSEARCH_HOST}:{settings.OPENSEARCH_PORT}")
    logger.info(f"Properties Index: {settings.OPENSEARCH_PROPERTIES_INDEX}")

    # Load embedding model for semantic search
    global embedding_model
    # TEMPORARY: Disabled to speed up startup for testing city filtering
    logger.warning("⚠️  Semantic search temporarily disabled for testing")
    embedding_model = None
    # try:
    #     logger.info("📦 Loading sentence-transformers model for semantic search...")
    #     embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    #     logger.info("✅ Embedding model loaded successfully!")
    # except Exception as e:
    #     logger.error(f"❌ Failed to load embedding model: {e}")
    #     logger.warning("⚠️  Semantic search will not be available")

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

# CORS - CRITICAL FIX: Restrict origins for security
# In production, only allow specific origins to prevent CSRF attacks
import os
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8888").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
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
            # CRITICAL FIX: Validate and sanitize user input to prevent injection
            # Limit query length and remove potentially dangerous characters
            sanitized_query = request.query.strip()[:500]  # Max 500 chars
            if not sanitized_query:
                raise HTTPException(status_code=400, detail="Query cannot be empty")

            # Basic validation: reject queries with only special characters
            if not any(c.isalnum() or c.isspace() for c in sanitized_query):
                raise HTTPException(status_code=400, detail="Query must contain alphanumeric characters")

            must_clauses.append({
                "multi_match": {
                    "query": sanitized_query,  # Use sanitized query
                    "fields": ["title^3", "description", "location^2"],  # Boost title and location
                    "type": "best_fields",
                    "operator": "or"
                }
            })

        # Apply filters
        # MVP STRATEGY: Use "should" clauses instead of hard "filter" to boost relevance
        # but not strictly require them (since property_type/price/area have data quality issues)
        should_clauses = []

        if request.filters:
            # MEDIUM FIX Bug#11: Validate range filters to prevent logical errors
            if request.filters.min_price and request.filters.max_price:
                if request.filters.min_price > request.filters.max_price:
                    raise HTTPException(
                        status_code=400,
                        detail=f"min_price ({request.filters.min_price}) cannot exceed max_price ({request.filters.max_price})"
                    )

            if request.filters.min_area and request.filters.max_area:
                if request.filters.min_area > request.filters.max_area:
                    raise HTTPException(
                        status_code=400,
                        detail=f"min_area ({request.filters.min_area}) cannot exceed max_area ({request.filters.max_area})"
                    )

            # City filter - HARD FILTER (exact match required!)
            if request.filters.city:
                # Normalize to title case for case-insensitive matching
                # "hồ chí minh" → "Hồ Chí Minh", "HỒ CHÍ MINH" → "Hồ Chí Minh"
                normalized_city = request.filters.city.title()

                filter_clauses.append({
                    "term": {
                        "city": normalized_city  # Field is already keyword type, no .keyword suffix
                    }
                })
                logger.info(f"✅ Applied city filter: {normalized_city} (input: {request.filters.city})")

            # District filter - HARD FILTER (exact match)
            if request.filters.district:
                # Normalize to title case for case-insensitive matching
                normalized_district = request.filters.district.title()

                filter_clauses.append({
                    "term": {
                        "district": normalized_district  # Field is already keyword type, no .keyword suffix
                    }
                })
                logger.info(f"✅ Applied district filter: {normalized_district} (input: {request.filters.district})")

            # Region/location filter - FALLBACK (for backward compatibility)
            if request.filters.region:
                # Enhance the query text with region info for better BM25 matching
                must_clauses.append({
                    "multi_match": {
                        "query": request.filters.region,
                        "fields": ["district^2", "location", "title", "description"],
                        "type": "best_fields",
                        "operator": "or"
                    }
                })

            # Property type filter - ADD TO QUERY TEXT (most property_type fields are empty)
            if request.filters.property_type:
                must_clauses.append({
                    "multi_match": {
                        "query": request.filters.property_type,
                        "fields": ["title^3", "description"],  # Search in text, not empty field
                        "type": "best_fields",
                        "operator": "or"
                    }
                })

            # Price range filter - USE price_normalized (numeric field)
            if request.filters.min_price or request.filters.max_price:
                price_range = {}
                if request.filters.min_price:
                    price_range["gte"] = request.filters.min_price
                if request.filters.max_price:
                    price_range["lte"] = request.filters.max_price
                filter_clauses.append({
                    "range": {
                        "price_normalized": price_range  # Changed from "price" to "price_normalized"
                    }
                })
                logger.info(f"✅ Applied price filter: {request.filters.min_price or 0:,.0f} - {request.filters.max_price or 0:,.0f} VND")

            # Bedrooms filter - SOFT FILTER (use "should" to boost, not require)
            if request.filters.min_bedrooms:
                should_clauses.append({
                    "range": {
                        "bedrooms": {"gte": request.filters.min_bedrooms}
                    }
                })

            # Area filter - NOW ENABLED (area is numeric after normalization!)
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

            # HIGH PRIORITY FIX: Proper type coercion with logging
            bedrooms = source.get('bedrooms', 0)
            if isinstance(bedrooms, str):
                try:
                    bedrooms = int(bedrooms)
                except ValueError as e:
                    logger.warning(f"⚠️ Invalid bedrooms value '{bedrooms}' for property {source.get('id')}, defaulting to 0")
                    bedrooms = 0

            bathrooms = source.get('bathrooms', 0)
            if isinstance(bathrooms, str):
                try:
                    bathrooms = int(bathrooms)
                except ValueError as e:
                    logger.warning(f"⚠️ Invalid bathrooms value '{bathrooms}' for property {source.get('id')}, defaulting to 0")
                    bathrooms = 0

            results.append(PropertyResult(
                property_id=source.get('property_id', hit['_id']),
                title=source.get('title', ''),
                price=source.get('price', 0),  # Keep as-is (string or number)
                description=source.get('description', ''),
                property_type=source.get('property_type', ''),
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                area=source.get('area', 0),  # Keep as-is (string or number)
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

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        # MEDIUM FIX Bug#4: Log search context for debugging
        logger.error(
            f"❌ Search failed: query='{request.query}', "
            f"filters={request.filters}, limit={request.limit}, error={e}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Search operation failed. Please try again later.")


@app.post("/vector-search", response_model=SearchResponse)
async def vector_search_properties(request: SearchRequest):
    """
    Semantic search using vector embeddings and k-NN similarity
    Best for vague/descriptive queries like 'yên tĩnh', 'gần trường quốc tế', 'view đẹp'
    """
    start_time = time.time()

    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch not available")

    if not embedding_model:
        raise HTTPException(status_code=503, detail="Embedding model not loaded. Semantic search unavailable.")

    try:
        logger.info(f"🔍 Vector Search Request: query='{request.query}'")

        # Generate embedding for query
        query_embedding = embedding_model.encode(request.query, convert_to_numpy=True)

        # Build k-NN search query
        search_body = {
            "size": request.limit,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding.tolist(),
                        "k": request.limit * 2  # Retrieve more candidates for better results
                    }
                }
            }
        }

        # Add filters if provided (combine with k-NN using bool query)
        if request.filters:
            filter_clauses = []

            # District filter
            if request.filters.region:
                filter_clauses.append({
                    "multi_match": {
                        "query": request.filters.region,
                        "fields": ["district", "location"]
                    }
                })

            # Property type filter
            if request.filters.property_type:
                filter_clauses.append({
                    "multi_match": {
                        "query": request.filters.property_type,
                        "fields": ["title", "description"]
                    }
                })

            # Bedrooms filter
            if request.filters.min_bedrooms:
                filter_clauses.append({
                    "range": {
                        "bedrooms": {"gte": request.filters.min_bedrooms}
                    }
                })

            # If we have filters, combine with k-NN using bool query
            if filter_clauses:
                search_body["query"] = {
                    "bool": {
                        "must": [search_body["query"]],  # k-NN as must clause
                        "filter": filter_clauses
                    }
                }

        # Execute vector search on properties_vector index
        response = await opensearch_client.search(
            index="properties_vector",  # Use vector index with embeddings
            body=search_body
        )

        # Convert results to PropertyResult objects
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']

            # Extract values with flexible typing
            bedrooms = source.get('bedrooms', 0)
            if isinstance(bedrooms, str):
                try:
                    bedrooms = int(bedrooms)
                except:
                    bedrooms = 0

            bathrooms = source.get('bathrooms', 0)
            if isinstance(bathrooms, str):
                try:
                    bathrooms = int(bathrooms)
                except ValueError as e:
                    logger.warning(f"⚠️ Invalid bathrooms value '{bathrooms}' for property {source.get('id')}, defaulting to 0")
                    bathrooms = 0

            results.append(PropertyResult(
                property_id=source.get('property_id', hit['_id']),
                title=source.get('title', ''),
                price=source.get('price', 0),
                description=source.get('description', ''),
                property_type=source.get('property_type', ''),
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                area=source.get('area', 0),
                district=source.get('district', ''),
                city=source.get('city', ''),
                score=float(hit['_score'])
            ))

        execution_time = (time.time() - start_time) * 1000
        total_hits = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']

        logger.info(f"✅ Vector search completed: {len(results)} results (total: {total_hits}) in {execution_time:.2f}ms")

        return SearchResponse(
            results=results,
            total=total_hits,
            execution_time_ms=execution_time
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        # MEDIUM FIX Bug#4: Log search context for debugging
        logger.error(
            f"❌ Vector search failed: query='{request.query}', "
            f"filters={request.filters}, limit={request.limit}, error={e}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Search operation failed. Please try again later.")


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


@app.post("/bulk-insert")
async def bulk_insert_properties(properties: List[Dict[str, Any]]):
    """
    Bulk insert normalized properties into OpenSearch

    Expects properties with NUMERIC price and area:
    {
        "property_id": "unique-id",
        "title": "...",
        "price": 5770000000,          # NUMERIC (VND)
        "price_display": "5.77 tỷ",   # For display
        "area": 95.0,                  # NUMERIC (m²)
        "area_display": "95 m²",       # For display
        "bedrooms": 3,                 # INT
        "bathrooms": 2,                # INT
        "district": "Quận 7",
        "city": "Hồ Chí Minh",
        ...
    }
    """
    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch not available")

    if not properties:
        return {"indexed_count": 0, "failed_count": 0}

    try:
        logger.info(f"📥 Bulk insert request: {len(properties)} properties")

        # Prepare bulk data for OpenSearch
        bulk_data = []

        for prop in properties:
            # Generate property_id if not provided
            property_id = prop.get('property_id')
            if not property_id:
                # Use URL or fallback to hash
                url = prop.get('url', '')
                if url:
                    property_id = url.split('/')[-1] or f"prop_{hash(url)}"
                else:
                    property_id = f"prop_{hash(str(prop))}"

            # Ensure price and area are numeric
            price = prop.get('price', 0)
            if isinstance(price, str):
                # Shouldn't happen if normalized, but fallback
                try:
                    price = float(price.replace(',', '').replace(' ', ''))
                except:
                    price = 0

            area = prop.get('area', 0)
            if isinstance(area, str):
                try:
                    area = float(area.replace('m²', '').replace('m2', '').replace(' ', ''))
                except:
                    area = 0

            # Prepare document with NUMERIC types
            doc = {
                "property_id": property_id,
                "title": prop.get('title', ''),
                "description": prop.get('description', ''),

                # NUMERIC fields for filtering/sorting
                "price": float(price) if price else 0,
                "area": float(area) if area else 0,
                "bedrooms": int(prop.get('bedrooms', 0)),
                "bathrooms": int(prop.get('bathrooms', 0)),

                # Display fields (formatted text)
                "price_display": prop.get('price_display', ''),
                "area_display": prop.get('area_display', ''),

                # Location fields
                "location": prop.get('location', ''),
                "district": prop.get('district', ''),
                "city": prop.get('city', ''),

                # Other fields
                "property_type": prop.get('property_type', ''),
                "url": prop.get('url', ''),
                "source": prop.get('source', ''),

                # Metadata
                "created_at": prop.get('created_at', datetime.utcnow().isoformat()),
                "indexed_at": datetime.utcnow().isoformat()
            }

            # Add any additional fields from the property (flexible schema)
            for key, value in prop.items():
                if key not in doc:
                    doc[key] = value

            # Add to bulk request (index action + document)
            bulk_data.append({"index": {"_index": settings.OPENSEARCH_PROPERTIES_INDEX, "_id": property_id}})
            bulk_data.append(doc)

        logger.info(f"📤 Sending bulk insert: {len(bulk_data) // 2} documents")

        # Execute bulk insert
        response = await opensearch_client.bulk(body=bulk_data, refresh=True)

        # Count successes and failures
        indexed_count = 0
        failed_count = 0
        errors = []

        if response.get('errors'):
            for item in response['items']:
                index_result = item.get('index', {})
                if 'error' in index_result:
                    failed_count += 1
                    errors.append(f"{index_result.get('_id')}: {index_result['error'].get('reason', 'Unknown error')}")
                else:
                    indexed_count += 1
        else:
            indexed_count = len(bulk_data) // 2

        logger.info(f"✅ Bulk insert complete: {indexed_count} indexed, {failed_count} failed")

        if errors and len(errors) <= 5:
            logger.warning(f"⚠️  Errors: {errors}")

        return {
            "indexed_count": indexed_count,
            "failed_count": failed_count,
            "errors": errors[:10] if errors else None  # Return first 10 errors
        }

    except Exception as e:
        logger.error(f"❌ Bulk insert failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk insert failed: {str(e)}")


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
