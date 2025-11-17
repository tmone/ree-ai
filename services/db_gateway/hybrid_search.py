"""
Hybrid Search Implementation
Combines BM25 (keyword) + Vector (semantic) search with weighted ranking
CTO Architecture Priority 3
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def normalize_scores(results: List[Dict]) -> List[Dict]:
    """
    Normalize scores to [0, 1] range using min-max normalization

    Args:
        results: List of search results with 'score' field

    Returns:
        Results with added 'normalized_score' field
    """
    if not results:
        return results

    scores = [r.get('score', 0) for r in results]
    min_score = min(scores)
    max_score = max(scores)
    score_range = max_score - min_score

    if score_range == 0:
        # All scores identical - normalize to 1.0
        for r in results:
            r['normalized_score'] = 1.0
    else:
        # Min-max normalization: (x - min) / (max - min)
        for r in results:
            original_score = r.get('score', 0)
            r['normalized_score'] = (original_score - min_score) / score_range

    return results


def combine_results(
    bm25_results: List[Dict],
    vector_results: List[Dict],
    alpha: float
) -> List[Dict]:
    """
    Merge BM25 and vector search results using weighted formula

    Formula: hybrid_score = alpha * bm25_score + (1-alpha) * vector_score

    Args:
        bm25_results: Results from BM25 search (normalized)
        vector_results: Results from vector search (normalized)
        alpha: Weight for BM25 score (0.0-1.0)

    Returns:
        Merged and re-ranked results sorted by hybrid score
    """
    # Build lookup maps by property_id
    bm25_map = {r['property_id']: r for r in bm25_results}
    vector_map = {r['property_id']: r for r in vector_results}

    # Get all unique property IDs from both searches
    all_property_ids = set(bm25_map.keys()) | set(vector_map.keys())

    merged_results = []
    for prop_id in all_property_ids:
        bm25_result = bm25_map.get(prop_id)
        vector_result = vector_map.get(prop_id)

        # Get normalized scores (0 if not in that search)
        bm25_score = bm25_result['normalized_score'] if bm25_result else 0.0
        vector_score = vector_result['normalized_score'] if vector_result else 0.0

        # Calculate hybrid score using weighted formula
        hybrid_score = alpha * bm25_score + (1 - alpha) * vector_score

        # Use property data from whichever source has it (prefer BM25 if both)
        property_data = bm25_result or vector_result

        # Build merged result
        merged_results.append({
            **property_data,
            'hybrid_score': hybrid_score,
            'bm25_score': bm25_score,
            'vector_score': vector_score,
            'score': hybrid_score,  # Final score for consistency
            'search_method': 'hybrid'
        })

    # Sort by hybrid score descending
    merged_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

    return merged_results


async def execute_bm25_search(
    opensearch_client,
    query: str,
    filters: Any,
    limit: int = 20
) -> List[Dict]:
    """
    Execute BM25 full-text search on properties index

    Args:
        opensearch_client: OpenSearch client instance
        query: Search query text
        filters: Search filters object
        limit: Maximum results to return

    Returns:
        List of property results with scores
    """
    try:
        # Build BM25 query
        must_clauses = []
        filter_clauses = []

        if query:
            # Sanitize and validate query
            sanitized_query = query.strip()[:500]
            if not sanitized_query:
                return []

            # Multi-match query across text fields
            must_clauses.append({
                "multi_match": {
                    "query": sanitized_query,
                    "fields": ["title^3", "description", "location^2"],
                    "type": "best_fields",
                    "operator": "or"
                }
            })

        # Apply filters if provided
        if filters:
            # City filter (exact match)
            if getattr(filters, 'city', None):
                filter_clauses.append({
                    "term": {
                        "city.keyword": filters.city.title()
                    }
                })

            # District filter (exact match)
            if getattr(filters, 'district', None):
                filter_clauses.append({
                    "term": {
                        "district.keyword": filters.district.title()
                    }
                })

            # Price range filter
            if getattr(filters, 'min_price', None) or getattr(filters, 'max_price', None):
                price_range = {}
                if getattr(filters, 'min_price', None):
                    price_range["gte"] = filters.min_price
                if getattr(filters, 'max_price', None):
                    price_range["lte"] = filters.max_price
                filter_clauses.append({
                    "range": {
                        "price_normalized": price_range
                    }
                })

            # Area range filter
            if getattr(filters, 'min_area', None) or getattr(filters, 'max_area', None):
                area_range = {}
                if getattr(filters, 'min_area', None):
                    area_range["gte"] = filters.min_area
                if getattr(filters, 'max_area', None):
                    area_range["lte"] = filters.max_area
                filter_clauses.append({
                    "range": {
                        "area": area_range
                    }
                })

        # Build complete search body
        search_body = {
            "size": limit,
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            }
        }

        # Execute search
        response = await opensearch_client.search(
            index="properties",
            body=search_body
        )

        # Parse results
        hits = response.get('hits', {}).get('hits', [])
        results = []
        for hit in hits:
            source = hit['_source']
            results.append({
                'property_id': hit['_id'],
                'score': hit['_score'],
                **source
            })

        return results

    except Exception as e:
        logger.error(f"BM25 search error: {e}", exc_info=True)
        raise


async def execute_vector_search(
    opensearch_client,
    embedding_model,
    query: str,
    filters: Any,
    limit: int = 20
) -> List[Dict]:
    """
    Execute vector k-NN search on properties_vector index

    Args:
        opensearch_client: OpenSearch client instance
        embedding_model: Sentence transformer model
        query: Search query text
        filters: Search filters object
        limit: Maximum results to return

    Returns:
        List of property results with scores
    """
    try:
        # Check if vector index exists
        try:
            exists = await opensearch_client.indices.exists(index="properties_vector")
            if not exists:
                logger.warning("Vector index 'properties_vector' does not exist")
                return []
        except:
            logger.warning("Failed to check vector index existence")
            return []

        # Check if embedding model is available
        if not embedding_model:
            logger.warning("Embedding model not available")
            return []

        # Generate query embedding
        query_embedding = embedding_model.encode(query, convert_to_numpy=True)

        # Build k-NN search query
        search_body = {
            "size": limit,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding.tolist(),
                        "k": limit * 2  # Retrieve more candidates
                    }
                }
            }
        }

        # Add filters if provided
        if filters:
            filter_clauses = []

            # District filter
            if getattr(filters, 'district', None):
                filter_clauses.append({
                    "term": {
                        "district.keyword": filters.district.title()
                    }
                })

            # City filter
            if getattr(filters, 'city', None):
                filter_clauses.append({
                    "term": {
                        "city.keyword": filters.city.title()
                    }
                })

            # Combine filters with k-NN
            if filter_clauses:
                search_body["query"] = {
                    "bool": {
                        "must": [
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": query_embedding.tolist(),
                                        "k": limit * 2
                                    }
                                }
                            }
                        ],
                        "filter": filter_clauses
                    }
                }

        # Execute search
        response = await opensearch_client.search(
            index="properties_vector",
            body=search_body
        )

        # Parse results
        hits = response.get('hits', {}).get('hits', [])
        results = []
        for hit in hits:
            source = hit['_source']
            results.append({
                'property_id': hit['_id'],
                'score': hit['_score'],
                **source
            })

        return results

    except Exception as e:
        logger.error(f"Vector search error: {e}", exc_info=True)
        raise


async def execute_hybrid_search(
    opensearch_client,
    embedding_model,
    query: str,
    filters: Any,
    alpha: float = 0.3,
    limit: int = 20
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Execute hybrid search combining BM25 and vector search

    Args:
        opensearch_client: OpenSearch client instance
        embedding_model: Sentence transformer model
        query: Search query text
        filters: Search filters object
        alpha: Weight for BM25 score (default: 0.3)
        limit: Maximum results to return

    Returns:
        Tuple of (merged_results, metadata)
    """
    start_time = time.time()

    logger.info(f"🔍 Hybrid Search: query='{query}', alpha={alpha}")

    # Execute both searches in parallel
    bm25_task = execute_bm25_search(opensearch_client, query, filters, limit)
    vector_task = execute_vector_search(opensearch_client, embedding_model, query, filters, limit)

    # Gather results with exception handling
    results = await asyncio.gather(
        bm25_task,
        vector_task,
        return_exceptions=True
    )

    bm25_results = results[0]
    vector_results = results[1]

    # Handle exceptions gracefully
    if isinstance(bm25_results, Exception):
        logger.warning(f"BM25 search failed: {bm25_results}")
        bm25_results = []

    if isinstance(vector_results, Exception):
        logger.warning(f"Vector search failed: {vector_results}")
        vector_results = []

    # Metadata for debugging
    metadata = {
        "bm25_count": len(bm25_results),
        "vector_count": len(vector_results),
        "alpha": alpha,
        "bm25_weight": alpha,
        "vector_weight": 1 - alpha
    }

    # Fallback if one search fails
    if not bm25_results and not vector_results:
        logger.warning("Both BM25 and vector search returned no results")
        return [], metadata
    elif not bm25_results:
        logger.info("BM25 search failed, using vector results only")
        metadata["fallback"] = "vector_only"
        return vector_results[:limit], metadata
    elif not vector_results:
        logger.info("Vector search failed, using BM25 results only")
        metadata["fallback"] = "bm25_only"
        return bm25_results[:limit], metadata

    # Normalize scores
    bm25_results = normalize_scores(bm25_results)
    vector_results = normalize_scores(vector_results)

    # Combine results using weighted formula
    merged_results = combine_results(bm25_results, vector_results, alpha)

    # Add execution time to metadata
    execution_time = (time.time() - start_time) * 1000
    metadata["execution_time_ms"] = round(execution_time, 2)
    metadata["merged_count"] = len(merged_results)

    logger.info(
        f"✅ Hybrid search complete: {len(merged_results)} results "
        f"(BM25: {len(bm25_results)}, Vector: {len(vector_results)}) "
        f"in {execution_time:.2f}ms"
    )

    return merged_results[:limit], metadata
