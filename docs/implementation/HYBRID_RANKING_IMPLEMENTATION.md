# Hybrid Ranking Implementation Plan

**CTO Architecture Priority 3: Hybrid Search with Weighted Ranking**

## Overview

Combine BM25 (keyword matching) + Vector Search (semantic similarity) using weighted formula for optimal search results.

## Formula

```
final_score = alpha * normalized_bm25_score + (1-alpha) * normalized_vector_score
```

**Parameters:**
- `alpha`: Weight for BM25 (default: 0.3)
- `(1-alpha)`: Weight for vector search (default: 0.7)
- Semantic search typically more important for real estate (view, atmosphere, lifestyle)

## Architecture

### Current State
- `/search` endpoint: BM25 only (services/db_gateway/main.py:194)
- `/vector-search` endpoint: Vector only (services/db_gateway/main.py:417)
- Both return separate results with different scoring scales

### Target State
- New `/hybrid-search` endpoint
- Executes both searches in parallel
- Normalizes scores to [0,1] range
- Combines with weighted formula
- Returns merged, re-ranked results

## Implementation Steps

### Step 1: Score Normalization (REQUIRED)

BM25 and vector scores use different scales. Must normalize before combining:

**Min-Max Normalization:**
```python
def normalize_scores(results: List[Dict]) -> List[Dict]:
    """Normalize scores to [0, 1] range"""
    if not results:
        return results

    scores = [r['score'] for r in results]
    min_score = min(scores)
    max_score = max(scores)
    score_range = max_score - min_score

    if score_range == 0:
        # All scores identical
        for r in results:
            r['normalized_score'] = 1.0
    else:
        for r in results:
            r['normalized_score'] = (r['score'] - min_score) / score_range

    return results
```

### Step 2: Parallel Search Execution

```python
import asyncio

async def execute_hybrid_search(query: str, filters: SearchFilters, alpha: float = 0.3):
    """Execute BM25 and vector search in parallel"""

    # Run both searches concurrently
    bm25_task = execute_bm25_search(query, filters)
    vector_task = execute_vector_search(query, filters)

    bm25_results, vector_results = await asyncio.gather(
        bm25_task,
        vector_task,
        return_exceptions=True
    )

    # Handle errors gracefully
    if isinstance(bm25_results, Exception):
        logger.warning(f"BM25 search failed: {bm25_results}")
        bm25_results = []

    if isinstance(vector_results, Exception):
        logger.warning(f"Vector search failed: {vector_results}")
        vector_results = []

    # Fallback if one search fails
    if not bm25_results and not vector_results:
        return []
    elif not bm25_results:
        return vector_results
    elif not vector_results:
        return bm25_results

    # Normalize scores
    bm25_results = normalize_scores(bm25_results)
    vector_results = normalize_scores(vector_results)

    # Combine results
    return combine_results(bm25_results, vector_results, alpha)
```

### Step 3: Result Merging

```python
def combine_results(bm25_results: List[Dict], vector_results: List[Dict], alpha: float):
    """Merge results from both searches using weighted formula"""

    # Build lookup maps
    bm25_map = {r['property_id']: r for r in bm25_results}
    vector_map = {r['property_id']: r for r in vector_results}

    # Get all unique property IDs
    all_property_ids = set(bm25_map.keys()) | set(vector_map.keys())

    merged_results = []
    for prop_id in all_property_ids:
        bm25_result = bm25_map.get(prop_id)
        vector_result = vector_map.get(prop_id)

        # Calculate hybrid score
        bm25_score = bm25_result['normalized_score'] if bm25_result else 0.0
        vector_score = vector_result['normalized_score'] if vector_result else 0.0

        hybrid_score = alpha * bm25_score + (1 - alpha) * vector_score

        # Use property data from whichever source has it
        property_data = bm25_result or vector_result

        merged_results.append({
            **property_data,
            'hybrid_score': hybrid_score,
            'bm25_score': bm25_score,
            'vector_score': vector_score,
            'score': hybrid_score  # Final score
        })

    # Sort by hybrid score descending
    merged_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

    return merged_results
```

### Step 4: New API Endpoint

**File: `services/db_gateway/main.py`**

```python
@app.post("/hybrid-search", response_model=SearchResponse)
async def hybrid_search_properties(
    request: SearchRequest,
    alpha: float = Query(0.3, ge=0.0, le=1.0, description="BM25 weight (0.0-1.0)")
):
    """
    Hybrid search combining BM25 (keyword) + Vector (semantic) with weighted ranking.

    Formula: final_score = alpha * bm25_score + (1-alpha) * vector_score

    Args:
        request: Search request with query and filters
        alpha: Weight for BM25 score (default: 0.3)
               - alpha=1.0: Pure BM25 (keyword matching)
               - alpha=0.0: Pure vector (semantic)
               - alpha=0.3: Balanced (recommended for real estate)

    Returns:
        Merged and re-ranked results
    """
    if not opensearch_client:
        raise HTTPException(status_code=503, detail="OpenSearch not available")

    try:
        start_time = time.time()

        logger.info(
            f"🔍 Hybrid Search: query='{request.query}', alpha={alpha}, "
            f"filters={request.filters}"
        )

        # Execute hybrid search
        results = await execute_hybrid_search(
            query=request.query,
            filters=request.filters,
            alpha=alpha,
            limit=request.limit
        )

        execution_time = (time.time() - start_time) * 1000

        logger.info(
            f"✅ Hybrid search completed: {len(results)} results "
            f"in {execution_time:.2f}ms (alpha={alpha})"
        )

        return SearchResponse(
            results=results[:request.limit],
            total=len(results),
            execution_time_ms=execution_time,
            metadata={
                "search_type": "hybrid",
                "alpha": alpha,
                "bm25_weight": alpha,
                "vector_weight": 1 - alpha
            }
        )

    except Exception as e:
        logger.error(f"❌ Hybrid search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Hybrid search operation failed"
        )
```

## Testing Plan

### Test 1: Keyword-Heavy Query
**Query:** "căn hộ 2 phòng ngủ quận 1 giá 5 tỷ"
**Expected:** BM25 should dominate (exact match on structured attributes)
**Recommended alpha:** 0.5-0.7

### Test 2: Semantic Query
**Query:** "nhà view đẹp gần trường học yên tĩnh phù hợp gia đình"
**Expected:** Vector search should dominate (lifestyle/atmosphere)
**Recommended alpha:** 0.2-0.3

### Test 3: Mixed Query
**Query:** "biệt thự 4 phòng có hồ bơi view đẹp"
**Expected:** Both contribute (structured: "4 phòng" + semantic: "view đẹp")
**Recommended alpha:** 0.3-0.4

### Test 4: Edge Cases
- Empty BM25 results but valid vector results
- Empty vector results but valid BM25 results
- No results from either
- Duplicate properties in both result sets

## Performance Optimization

### Parallel Execution
- BM25 and vector search run concurrently
- Total latency ≈ max(bm25_time, vector_time) + merging_overhead

### Caching
- Cache normalized scores for repeated queries
- Cache merged results with alpha as cache key

### Index Optimization
- Ensure both `properties` and `properties_vector` indices are optimized
- Use appropriate replica and shard settings

## Configuration

### Environment Variables
```bash
HYBRID_SEARCH_ALPHA=0.3  # Default BM25 weight
HYBRID_SEARCH_CACHE_TTL=300  # Cache for 5 minutes
```

### Per-Query Override
```bash
POST /hybrid-search
{
  "query": "căn hộ view đẹp",
  "alpha": 0.4  # Override default
}
```

## Monitoring & Analytics

### Metrics to Track
- Average alpha value used
- BM25 vs Vector contribution to final results
- Query types that benefit most from hybrid approach
- User click-through rates by search type

### A/B Testing
- Split traffic between pure vector and hybrid
- Measure engagement metrics (clicks, inquiries, time on page)
- Tune alpha based on real user behavior

## Migration Path

### Phase 1: Add Endpoint (Week 1)
- Implement `/hybrid-search` endpoint
- Keep existing `/search` and `/vector-search` unchanged
- Test with sample queries

### Phase 2: Gradual Rollout (Week 2)
- 10% traffic to hybrid search
- Monitor performance and accuracy
- Collect user feedback

### Phase 3: Full Migration (Week 3)
- Redirect `/search` to use hybrid internally
- Keep original endpoints for backward compatibility
- Update orchestrator to use hybrid by default

## Success Criteria

✅ Hybrid search latency < 100ms (95th percentile)
✅ Relevance score improvement > 15% vs pure BM25
✅ User engagement (CTR) improvement > 10%
✅ Zero downtime during migration
✅ Graceful fallback if one search type fails

## Next Steps (Priority 4: Re-ranking Service)

After hybrid ranking is stable, add ML-based re-ranking:
1. User behavior signals (clicks, views, inquiries)
2. Property freshness decay
3. Seller reputation score
4. Location popularity trends

See: `RE_RANKING_SERVICE_SPEC.md` (Priority 4)

---

**Status:** READY FOR IMPLEMENTATION
**Estimated Effort:** 3-4 days
**Dependencies:** Both BM25 and vector indices must be functional
**Risk Level:** MEDIUM (requires careful score normalization)
