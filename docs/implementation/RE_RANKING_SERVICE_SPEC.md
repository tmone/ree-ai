# Re-ranking Service Specification

**CTO Architecture Priority 4: ML-Based Re-ranking Layer**

## Overview

Post-processing layer that re-ranks search results using business logic, user behavior signals, and contextual factors beyond pure text/semantic matching.

## Purpose

While hybrid search (Priority 3) provides good initial ranking, re-ranking layer adds:
- **Personalization**: User preferences and history
- **Business Rules**: Boost verified listings, premium properties
- **Freshness**: Decay old listings
- **Quality Signals**: Seller reputation, completeness score
- **Contextual Factors**: Time of day, user location, device type

## Architecture

```
[User Query] → [Hybrid Search] → [Top K Results] → [Re-ranking Service] → [Final Ranked Results]
                  (Priority 3)      (e.g., top 50)      (Priority 4)         (e.g., top 20)
```

### Service Location
```
services/
  └── reranking/
      ├── Dockerfile
      ├── requirements.txt
      ├── main.py              # FastAPI service
      ├── models/
      │   ├── features.py      # Feature extraction
      │   └── ranker.py        # LambdaMART/LightGBM model
      └── config/
          └── weights.yaml     # Feature weights configuration
```

## Feature Categories

### 1. Property Quality Features (40% weight)

#### Completeness Score (10%)
```python
def calculate_completeness(property: Dict) -> float:
    """Score based on information richness"""
    required_fields = ['title', 'description', 'price', 'area', 'district']
    optional_fields = ['images', 'videos', 'virtual_tour', 'contact_phone']

    required_score = sum(1 for f in required_fields if property.get(f)) / len(required_fields)
    optional_score = sum(1 for f in optional_fields if property.get(f)) / len(optional_fields)

    return 0.7 * required_score + 0.3 * optional_score
```

#### Image Quality (10%)
- Number of images (normalized 0-10 images)
- Image resolution if available
- Has virtual tour bonus

#### Description Quality (10%)
- Length (optimal: 200-500 chars)
- Contains keywords (location, amenities, pricing details)
- Professional language (no excessive emojis/caps)

#### Verification Status (10%)
- Verified: 1.0
- Pending: 0.5
- Unverified: 0.0

### 2. Seller Reputation Features (20% weight)

#### Historical Performance (15%)
```python
def calculate_seller_score(seller_id: str) -> float:
    """Score based on seller's track record"""
    seller_stats = get_seller_stats(seller_id)

    # Response rate (to inquiries)
    response_rate = seller_stats['responses'] / seller_stats['inquiries'] if seller_stats['inquiries'] > 0 else 0.5

    # Average response time (hours)
    avg_response_time = seller_stats['avg_response_time_hours']
    response_time_score = 1.0 / (1.0 + avg_response_time / 24)  # Decay by days

    # Successful closures
    closure_rate = seller_stats['closed_deals'] / seller_stats['total_listings'] if seller_stats['total_listings'] > 0 else 0.3

    return 0.4 * response_rate + 0.3 * response_time_score + 0.3 * closure_rate
```

#### Account Age (5%)
- New seller (<1 month): 0.5
- Established (1-6 months): 0.75
- Veteran (>6 months): 1.0

### 3. Freshness Features (15% weight)

#### Listing Age Decay (10%)
```python
def calculate_freshness_score(days_since_posted: int) -> float:
    """Exponential decay based on listing age"""
    half_life_days = 30  # Property loses half relevance after 30 days
    return 2 ** (-days_since_posted / half_life_days)
```

#### Recent Update Boost (5%)
- Updated within 7 days: +0.2 bonus
- Price reduced recently: +0.3 bonus

### 4. Engagement Features (15% weight)

#### User Behavior Signals (10%)
```python
def calculate_engagement_score(property_id: str, time_window_days: int = 7) -> float:
    """Score based on recent user engagement"""
    stats = get_property_stats(property_id, time_window_days)

    # Normalize by time window
    views_per_day = stats['views'] / time_window_days
    inquiries_per_day = stats['inquiries'] / time_window_days
    favorites_per_day = stats['favorites'] / time_window_days

    # Weighted combination
    return (
        0.3 * min(views_per_day / 10, 1.0) +      # Cap at 10 views/day
        0.4 * min(inquiries_per_day / 2, 1.0) +   # Cap at 2 inquiries/day
        0.3 * min(favorites_per_day / 1, 1.0)     # Cap at 1 favorite/day
    )
```

#### CTR (Click-Through Rate) from Search (5%)
- Historical CTR for this property in search results

### 5. Personalization Features (10% weight)

#### User Preference Matching (7%)
```python
def calculate_preference_match(user_id: str, property: Dict) -> float:
    """Score based on user's search history and preferences"""
    user_prefs = get_user_preferences(user_id)

    # Price range affinity
    price_match = 1.0 if user_prefs['min_price'] <= property['price'] <= user_prefs['max_price'] else 0.5

    # District preference
    district_match = 1.0 if property['district'] in user_prefs['preferred_districts'] else 0.7

    # Property type preference
    type_match = 1.0 if property['property_type'] in user_prefs['preferred_types'] else 0.8

    return 0.4 * price_match + 0.3 * district_match + 0.3 * type_match
```

#### Previous Interactions (3%)
- User viewed this property before: +0.5 bonus
- User favorited this property: +1.0 bonus
- User contacted seller: -0.5 penalty (avoid duplicates)

## API Interface

### Request
```python
class RerankRequest(BaseModel):
    """Request to re-rank search results"""
    query: str
    results: List[PropertyResult]  # Results from hybrid search
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None  # Additional context

class PropertyResult(BaseModel):
    property_id: str
    score: float  # Original hybrid search score
    # ... all property fields
```

### Response
```python
class RerankResponse(BaseModel):
    """Re-ranked results with explanations"""
    results: List[PropertyResult]
    rerank_metadata: Dict[str, Any]

class PropertyResult(BaseModel):
    property_id: str
    final_score: float  # After re-ranking
    original_score: float  # From hybrid search
    rerank_features: Dict[str, float]  # Feature scores for explainability
```

### Example
```bash
POST /rerank
{
  "query": "căn hộ 2 phòng quận 1",
  "user_id": "user_123",
  "results": [
    {
      "property_id": "prop_456",
      "score": 0.85,
      "title": "Căn hộ 2PN tại Vinhomes...",
      ...
    },
    ...
  ]
}

Response:
{
  "results": [
    {
      "property_id": "prop_789",  # May have lower hybrid score but higher rerank score
      "final_score": 0.92,
      "original_score": 0.80,
      "rerank_features": {
        "completeness": 0.95,
        "seller_reputation": 0.88,
        "freshness": 0.90,
        "engagement": 0.85,
        "personalization": 0.75
      }
    },
    ...
  ],
  "rerank_metadata": {
    "model_version": "1.0.0",
    "feature_weights": {...},
    "processing_time_ms": 15.3
  }
}
```

## Implementation

### Phase 1: Rule-Based Reranking (Week 1)
```python
def rerank_results(results: List[Dict], user_id: str) -> List[Dict]:
    """Simple rule-based reranking"""

    for result in results:
        # Start with original hybrid score
        base_score = result['score']

        # Calculate feature scores
        completeness = calculate_completeness(result)
        seller_score = calculate_seller_score(result['owner_id'])
        freshness = calculate_freshness_score(result['days_since_posted'])
        engagement = calculate_engagement_score(result['property_id'])
        personalization = calculate_preference_match(user_id, result) if user_id else 0.5

        # Weighted combination
        rerank_score = (
            0.40 * completeness +
            0.20 * seller_score +
            0.15 * freshness +
            0.15 * engagement +
            0.10 * personalization
        )

        # Blend with original score (50/50)
        result['final_score'] = 0.5 * base_score + 0.5 * rerank_score
        result['rerank_features'] = {
            'completeness': completeness,
            'seller_reputation': seller_score,
            'freshness': freshness,
            'engagement': engagement,
            'personalization': personalization
        }

    # Sort by final score
    results.sort(key=lambda x: x['final_score'], reverse=True)
    return results
```

### Phase 2: ML-Based Ranking (Week 2-3)
Use LightGBM/LambdaMART with Learning-to-Rank:

```python
import lightgbm as lgb

def train_ranker(training_data: pd.DataFrame):
    """Train LightGBM ranker on historical click data"""

    features = [
        'completeness_score',
        'seller_reputation',
        'freshness_decay',
        'engagement_score',
        'personalization_score',
        'original_hybrid_score'
    ]

    X = training_data[features]
    y = training_data['relevance_label']  # 0=skip, 1=click, 2=inquiry, 3=favorite

    # Group by query for LambdaMART
    groups = training_data.groupby('query_id').size().values

    ranker = lgb.LGBMRanker(
        objective='lambdarank',
        metric='ndcg',
        n_estimators=100
    )

    ranker.fit(X, y, group=groups)
    return ranker
```

### Phase 3: Online Learning (Week 4)
- A/B test rule-based vs ML ranker
- Collect user feedback (clicks, inquiries, time-on-page)
- Retrain model weekly with new data
- Monitor feature importance drift

## Data Pipeline

### Training Data Collection
```sql
CREATE TABLE search_interactions (
    id UUID PRIMARY KEY,
    user_id VARCHAR,
    query TEXT,
    property_id VARCHAR,
    rank_position INT,          -- Position in search results
    clicked BOOLEAN,
    inquiry_sent BOOLEAN,
    favorited BOOLEAN,
    time_on_page_seconds INT,
    timestamp TIMESTAMP,

    -- Context
    device_type VARCHAR,
    user_location VARCHAR,
    time_of_day VARCHAR,

    -- Property features at time of search
    property_features JSONB
);
```

### Feature Store
Use Redis for real-time feature serving:
```python
# Cache computed features
redis_client.setex(
    f"property_features:{property_id}",
    ttl=3600,  # 1 hour
    value=json.dumps({
        'completeness': 0.95,
        'seller_score': 0.88,
        'engagement_7d': 0.85
    })
)
```

## Testing Strategy

### Unit Tests
- Test each feature calculation function
- Validate score ranges [0, 1]
- Test edge cases (no data, outliers)

### Integration Tests
- End-to-end reranking pipeline
- Performance benchmarks (<20ms per request)
- Load testing (1000 req/s)

### A/B Testing
- Control: Hybrid search only
- Treatment: Hybrid + reranking
- Metrics:
  - CTR (Click-Through Rate)
  - Conversion rate (inquiry / view)
  - Time to inquiry
  - User satisfaction (survey)

## Monitoring & Alerts

### Metrics Dashboard
- **Latency**: P50, P95, P99 response times
- **Feature Distribution**: Track feature score distributions
- **Model Performance**: NDCG@10, MRR (Mean Reciprocal Rank)
- **Business Metrics**: Inquiry rate, conversion rate

### Alerts
- Reranking latency > 50ms (P95)
- Feature calculation errors > 1%
- Model degradation (NDCG drop > 5%)
- Service unavailable (fallback to hybrid only)

## Migration & Rollback

### Gradual Rollout
1. **Week 1**: 5% traffic → Monitor closely
2. **Week 2**: 25% traffic → Collect feedback
3. **Week 3**: 50% traffic → Validate improvements
4. **Week 4**: 100% traffic → Full migration

### Fallback Strategy
If reranking service fails:
1. Return original hybrid search results
2. Log error for investigation
3. Alert on-call engineer
4. Automatically disable reranking after 5 consecutive failures

## Success Criteria

✅ CTR improvement: +15% vs hybrid-only
✅ Inquiry rate improvement: +10%
✅ Latency overhead: <20ms (P95)
✅ Feature coverage: 100% of properties have all features
✅ Model NDCG@10: >0.85

## Cost Analysis

### Infrastructure
- **Service**: 2 instances (HA) = $100/month
- **Redis** (feature cache): $30/month
- **Model Training**: 1x/week GPU = $50/month
- **Total**: ~$180/month

### ROI
- Improved conversion → +10% inquiries
- Better user experience → Increased retention
- **Estimated Value**: +$5,000/month revenue impact

## Next Steps

1. **Week 1**: Implement rule-based reranking + API
2. **Week 2**: Collect interaction data + build training dataset
3. **Week 3**: Train ML ranker + A/B test
4. **Week 4**: Full rollout + monitoring setup

---

**Status:** READY FOR IMPLEMENTATION
**Priority:** MEDIUM (after Hybrid Ranking is stable)
**Dependencies:** Hybrid search (Priority 3), User behavior tracking
**Risk Level:** LOW (graceful fallback to hybrid search)
