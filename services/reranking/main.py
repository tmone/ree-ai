"""
Re-ranking Service
CTO Architecture Priority 4: ML-Based Re-ranking Layer

Phase 1: Rule-based reranking with business logic and quality signals
Phase 2: ML-based ranking with LightGBM/LambdaMART (future)
Phase 3: Online learning + A/B testing (future)
"""

import os
import time
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.rerank import (
    RerankRequest,
    RerankResponse,
    RankedPropertyResult,
    FeatureScores,
    RerankMetadata
)
from features.completeness import calculate_property_quality_score
from features.seller_reputation import calculate_seller_reputation_score
from features.freshness import calculate_freshness_score
from features.engagement import calculate_engagement_score
from features.personalization import calculate_personalization_score


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Re-ranking Service",
    description="ML-Based Re-ranking Layer for Search Results (CTO Priority 4)",
    version="1.0.0-phase1"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feature weights configuration (totals to 100%)
FEATURE_WEIGHTS = {
    "property_quality": 0.40,    # 40%
    "seller_reputation": 0.20,   # 20%
    "freshness": 0.15,           # 15%
    "engagement": 0.15,          # 15%
    "personalization": 0.10      # 10%
}

# Blend ratio between original score and rerank score
BLEND_ALPHA = 0.5  # 50% original hybrid score, 50% rerank score


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reranking",
        "version": "1.0.0-phase1",
        "phase": "Phase 1: Rule-based",
        "feature_weights": FEATURE_WEIGHTS
    }


@app.post("/rerank", response_model=RerankResponse)
async def rerank_search_results(request: RerankRequest):
    """
    Re-rank search results using business logic and quality signals

    Args:
        request: RerankRequest with query, results, user_id, context

    Returns:
        RerankResponse: Re-ranked results with feature scores
    """
    start_time = time.time()

    try:
        logger.info(f"Re-ranking {len(request.results)} results for query: '{request.query}'")

        # Process each property
        ranked_results = []

        for property_result in request.results:
            # Convert to dict for feature calculators
            property_data = property_result.model_dump()

            # Calculate all feature scores
            property_quality = calculate_property_quality_score(property_data)
            seller_reputation = calculate_seller_reputation_score(property_data)
            freshness = calculate_freshness_score(property_data)
            engagement = calculate_engagement_score(property_data)
            personalization = calculate_personalization_score(
                property_data,
                user_id=request.user_id
            )

            # Extract total scores from each category
            quality_score = property_quality['property_quality_total']
            seller_score = seller_reputation['seller_reputation_total']
            fresh_score = freshness['freshness_total']
            engage_score = engagement['engagement_total']
            person_score = personalization['personalization_total']

            # Calculate weighted rerank score
            weighted_rerank_score = (
                FEATURE_WEIGHTS['property_quality'] * quality_score +
                FEATURE_WEIGHTS['seller_reputation'] * seller_score +
                FEATURE_WEIGHTS['freshness'] * fresh_score +
                FEATURE_WEIGHTS['engagement'] * engage_score +
                FEATURE_WEIGHTS['personalization'] * person_score
            )

            # Blend with original hybrid search score
            original_score = property_result.score
            final_score = (
                BLEND_ALPHA * original_score +
                (1 - BLEND_ALPHA) * weighted_rerank_score
            )

            # Create feature scores object
            feature_scores = FeatureScores(
                completeness=quality_score,
                seller_reputation=seller_score,
                freshness=fresh_score,
                engagement=engage_score,
                personalization=person_score,
                weighted_rerank_score=weighted_rerank_score
            )

            # Create ranked result
            ranked_result = RankedPropertyResult(
                **property_data,
                final_score=final_score,
                original_score=original_score,
                rerank_features=feature_scores
            )

            ranked_results.append(ranked_result)

        # Sort by final score (descending)
        ranked_results.sort(key=lambda x: x.final_score, reverse=True)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Create metadata
        metadata = RerankMetadata(
            feature_weights=FEATURE_WEIGHTS,
            processing_time_ms=processing_time_ms,
            properties_reranked=len(ranked_results)
        )

        logger.info(f"Re-ranking completed in {processing_time_ms:.2f}ms")

        # Return response
        return RerankResponse(
            results=ranked_results,
            rerank_metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error in re-ranking: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Re-ranking failed: {str(e)}"
        )


@app.get("/weights")
async def get_feature_weights():
    """Get current feature weight configuration"""
    return {
        "feature_weights": FEATURE_WEIGHTS,
        "blend_alpha": BLEND_ALPHA,
        "description": {
            "property_quality": "Completeness, images, description, verification (40%)",
            "seller_reputation": "Historical performance, account age (20%)",
            "freshness": "Listing age decay, recent updates (15%)",
            "engagement": "User behavior, CTR (15%)",
            "personalization": "User preferences, interaction history (10%)",
            "blend_alpha": "Weight for original hybrid score vs rerank score"
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
