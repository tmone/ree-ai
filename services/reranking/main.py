"""
Reranking Service
Reranks search results based on user query relevance
- Uses semantic similarity for intelligent reordering
- Supports multiple reranking strategies (semantic, hybrid, popularity)
- Calculates relevance scores for each property
- Provides reranking explanations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from shared.utils.logger import get_logger
from shared.config import get_settings

# Logger & Settings
logger = get_logger(__name__)
settings = get_settings()

# App
app = FastAPI(
    title="REE AI - Reranking Service",
    description="Rerank search results based on query relevance",
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

class RerankingStrategy(str, Enum):
    """Reranking strategies"""
    SEMANTIC = "semantic"  # Pure semantic similarity
    HYBRID = "hybrid"  # Semantic + popularity + recency
    POPULARITY = "popularity"  # Based on views/likes
    RECENCY = "recency"  # Most recent first


class PropertyItem(BaseModel):
    """Property item for reranking"""
    property_id: str = Field(..., description="Property ID")
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    price_vnd: Optional[float] = None
    area_sqm: Optional[float] = None
    location: Optional[str] = None

    # Optional metadata for hybrid ranking
    views: int = Field(0, description="Number of views")
    likes: int = Field(0, description="Number of likes")
    created_at: Optional[str] = None

    # Combined text representation
    def to_text(self) -> str:
        """Convert property to text for semantic comparison"""
        parts = []
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.property_type:
            parts.append(f"Type: {self.property_type}")
        if self.price_vnd:
            parts.append(f"Price: {self.price_vnd:,.0f} VND")
        if self.area_sqm:
            parts.append(f"Area: {self.area_sqm} m2")
        if self.location:
            parts.append(f"Location: {self.location}")
        return " | ".join(parts)


class RankedProperty(BaseModel):
    """Reranked property with score"""
    property_id: str
    original_position: int
    new_position: int
    relevance_score: float = Field(..., description="Relevance score (0-1)")

    # Score breakdown
    semantic_score: float = Field(0.0, description="Semantic similarity score")
    popularity_score: float = Field(0.0, description="Popularity score")
    recency_score: float = Field(0.0, description="Recency score")

    # Explanation
    explanation: str = Field("", description="Why this property was ranked here")

    # Original property data
    property_data: PropertyItem


class RerankingRequest(BaseModel):
    """Reranking request"""
    query: str = Field(..., description="User search query")
    properties: List[PropertyItem] = Field(..., description="Properties to rerank")
    strategy: RerankingStrategy = Field(
        RerankingStrategy.SEMANTIC,
        description="Reranking strategy"
    )
    top_k: Optional[int] = Field(
        None,
        description="Return only top K results (optional)"
    )


class RerankingResponse(BaseModel):
    """Reranking response"""
    success: bool
    query: str
    strategy: RerankingStrategy
    total_properties: int
    reranked_properties: List[RankedProperty]
    processing_time_ms: float
    model: str
    explanation: str = Field("", description="Overall reranking explanation")
    error: Optional[str] = None


# ============================================================
# LLM CONFIGURATION
# ============================================================

# Core Gateway URL
USE_REAL = os.getenv("USE_REAL_CORE_GATEWAY", "false").lower() == "true"
CORE_GATEWAY_URL = "http://core-gateway:8080" if USE_REAL else "http://mock-core-gateway:1080"

logger.info(f"🔧 Mode: {'REAL' if USE_REAL else 'MOCK'}")
logger.info(f"🔧 Core Gateway: {CORE_GATEWAY_URL}")


def get_llm():
    """Get LLM instance"""
    if USE_REAL:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=f"{CORE_GATEWAY_URL}/v1"
        )
    else:
        # Mock mode - return None
        return None


def get_embeddings():
    """Get embeddings model"""
    if USE_REAL:
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=f"{CORE_GATEWAY_URL}/v1"
        )
    else:
        # Mock mode - return None
        return None


# ============================================================
# RERANKING LOGIC
# ============================================================

def calculate_semantic_score(query: str, property_text: str, embeddings) -> float:
    """Calculate semantic similarity score"""
    try:
        # Get embeddings
        query_embedding = embeddings.embed_query(query)
        property_embedding = embeddings.embed_query(property_text)

        # Calculate cosine similarity
        import math
        dot_product = sum(a * b for a, b in zip(query_embedding, property_embedding))
        query_norm = math.sqrt(sum(a * a for a in query_embedding))
        property_norm = math.sqrt(sum(b * b for b in property_embedding))

        similarity = dot_product / (query_norm * property_norm)

        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        score = (similarity + 1) / 2

        return score
    except Exception as e:
        logger.error(f"❌ Semantic score calculation failed: {str(e)}")
        return 0.5  # Default neutral score


def calculate_popularity_score(views: int, likes: int) -> float:
    """Calculate popularity score"""
    # Simple popularity scoring (can be made more sophisticated)
    # Score based on engagement
    engagement = views + (likes * 10)  # Likes count more than views

    # Normalize using log scale (to prevent outliers from dominating)
    import math
    if engagement > 0:
        score = math.log10(engagement + 1) / 5  # Scale to roughly 0-1
        return min(score, 1.0)
    return 0.0


def calculate_recency_score(created_at: Optional[str]) -> float:
    """Calculate recency score"""
    if not created_at:
        return 0.5  # Neutral score if no date

    try:
        from datetime import datetime, timedelta
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(created.tzinfo)

        days_old = (now - created).days

        # Score decreases with age
        # New (0-7 days): 1.0
        # Recent (7-30 days): 0.8-1.0
        # Moderate (30-90 days): 0.5-0.8
        # Old (90+ days): 0.0-0.5

        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8 + (0.2 * (30 - days_old) / 23)
        elif days_old <= 90:
            return 0.5 + (0.3 * (90 - days_old) / 60)
        else:
            return max(0.0, 0.5 - (days_old - 90) / 365)
    except Exception as e:
        logger.error(f"❌ Recency score calculation failed: {str(e)}")
        return 0.5


async def rerank_semantic(
    query: str,
    properties: List[PropertyItem],
    embeddings
) -> List[RankedProperty]:
    """Rerank using semantic similarity"""
    logger.info("🔍 Reranking using SEMANTIC strategy")

    ranked = []

    for idx, prop in enumerate(properties):
        property_text = prop.to_text()
        semantic_score = calculate_semantic_score(query, property_text, embeddings)

        explanation = f"Semantic match score: {semantic_score:.2f}. "
        if semantic_score > 0.8:
            explanation += "Highly relevant to your query."
        elif semantic_score > 0.6:
            explanation += "Good match for your search."
        elif semantic_score > 0.4:
            explanation += "Moderate relevance."
        else:
            explanation += "Lower relevance but might be of interest."

        ranked.append(RankedProperty(
            property_id=prop.property_id,
            original_position=idx,
            new_position=0,  # Will be updated after sorting
            relevance_score=semantic_score,
            semantic_score=semantic_score,
            explanation=explanation,
            property_data=prop
        ))

    # Sort by relevance score
    ranked.sort(key=lambda x: x.relevance_score, reverse=True)

    # Update positions
    for new_pos, item in enumerate(ranked):
        item.new_position = new_pos

    return ranked


async def rerank_hybrid(
    query: str,
    properties: List[PropertyItem],
    embeddings
) -> List[RankedProperty]:
    """Rerank using hybrid approach (semantic + popularity + recency)"""
    logger.info("🔍 Reranking using HYBRID strategy")

    ranked = []

    for idx, prop in enumerate(properties):
        property_text = prop.to_text()

        # Calculate individual scores
        semantic_score = calculate_semantic_score(query, property_text, embeddings)
        popularity_score = calculate_popularity_score(prop.views, prop.likes)
        recency_score = calculate_recency_score(prop.created_at)

        # Weighted combination
        # Semantic is most important (60%), popularity (25%), recency (15%)
        weights = {"semantic": 0.60, "popularity": 0.25, "recency": 0.15}

        relevance_score = (
            semantic_score * weights["semantic"] +
            popularity_score * weights["popularity"] +
            recency_score * weights["recency"]
        )

        # Build explanation
        explanation_parts = []
        explanation_parts.append(f"Semantic: {semantic_score:.2f}")
        explanation_parts.append(f"Popularity: {popularity_score:.2f}")
        explanation_parts.append(f"Recency: {recency_score:.2f}")
        explanation = f"Hybrid score ({', '.join(explanation_parts)}). "

        if relevance_score > 0.8:
            explanation += "Excellent match!"
        elif relevance_score > 0.6:
            explanation += "Good fit for your search."
        else:
            explanation += "Moderate relevance."

        ranked.append(RankedProperty(
            property_id=prop.property_id,
            original_position=idx,
            new_position=0,
            relevance_score=relevance_score,
            semantic_score=semantic_score,
            popularity_score=popularity_score,
            recency_score=recency_score,
            explanation=explanation,
            property_data=prop
        ))

    # Sort by relevance score
    ranked.sort(key=lambda x: x.relevance_score, reverse=True)

    # Update positions
    for new_pos, item in enumerate(ranked):
        item.new_position = new_pos

    return ranked


async def rerank_popularity(
    query: str,
    properties: List[PropertyItem]
) -> List[RankedProperty]:
    """Rerank by popularity"""
    logger.info("🔍 Reranking using POPULARITY strategy")

    ranked = []

    for idx, prop in enumerate(properties):
        popularity_score = calculate_popularity_score(prop.views, prop.likes)

        explanation = f"Popularity score: {popularity_score:.2f} "
        explanation += f"({prop.views} views, {prop.likes} likes). "

        if popularity_score > 0.7:
            explanation += "Very popular property!"
        elif popularity_score > 0.5:
            explanation += "Good engagement."
        else:
            explanation += "Newer or less viewed."

        ranked.append(RankedProperty(
            property_id=prop.property_id,
            original_position=idx,
            new_position=0,
            relevance_score=popularity_score,
            popularity_score=popularity_score,
            explanation=explanation,
            property_data=prop
        ))

    # Sort by popularity
    ranked.sort(key=lambda x: x.relevance_score, reverse=True)

    # Update positions
    for new_pos, item in enumerate(ranked):
        item.new_position = new_pos

    return ranked


async def rerank_recency(
    query: str,
    properties: List[PropertyItem]
) -> List[RankedProperty]:
    """Rerank by recency"""
    logger.info("🔍 Reranking using RECENCY strategy")

    ranked = []

    for idx, prop in enumerate(properties):
        recency_score = calculate_recency_score(prop.created_at)

        explanation = f"Recency score: {recency_score:.2f}. "

        if recency_score > 0.8:
            explanation += "Very recent listing!"
        elif recency_score > 0.6:
            explanation += "Recently posted."
        else:
            explanation += "Older listing."

        ranked.append(RankedProperty(
            property_id=prop.property_id,
            original_position=idx,
            new_position=0,
            relevance_score=recency_score,
            recency_score=recency_score,
            explanation=explanation,
            property_data=prop
        ))

    # Sort by recency
    ranked.sort(key=lambda x: x.relevance_score, reverse=True)

    # Update positions
    for new_pos, item in enumerate(ranked):
        item.new_position = new_pos

    return ranked


async def rerank_mock(
    query: str,
    properties: List[PropertyItem],
    strategy: RerankingStrategy
) -> List[RankedProperty]:
    """Mock reranking for development"""
    logger.info("🎭 Using MOCK reranking")

    import random

    ranked = []

    for idx, prop in enumerate(properties):
        # Random scores for mock
        relevance_score = random.uniform(0.5, 0.95)
        semantic_score = random.uniform(0.4, 0.9)
        popularity_score = random.uniform(0.3, 0.8)
        recency_score = random.uniform(0.5, 1.0)

        ranked.append(RankedProperty(
            property_id=prop.property_id,
            original_position=idx,
            new_position=0,
            relevance_score=relevance_score,
            semantic_score=semantic_score,
            popularity_score=popularity_score,
            recency_score=recency_score,
            explanation=f"Mock score: {relevance_score:.2f} (strategy: {strategy})",
            property_data=prop
        ))

    # Sort by relevance
    ranked.sort(key=lambda x: x.relevance_score, reverse=True)

    # Update positions
    for new_pos, item in enumerate(ranked):
        item.new_position = new_pos

    return ranked


# ============================================================
# ENDPOINTS
# ============================================================

@app.post("/rerank", response_model=RerankingResponse)
async def rerank_properties(request: RerankingRequest):
    """
    Rerank properties based on query relevance

    Example:
    ```json
    {
        "query": "2 bedroom apartment near district 1",
        "properties": [
            {
                "property_id": "prop_001",
                "title": "Luxury 2BR Apartment",
                "description": "Beautiful 2 bedroom apartment...",
                "property_type": "apartment",
                "price_vnd": 5000000000,
                "area_sqm": 80,
                "location": "District 1",
                "views": 150,
                "likes": 12,
                "created_at": "2025-10-15T10:00:00Z"
            }
        ],
        "strategy": "hybrid",
        "top_k": 10
    }
    ```
    """
    start_time = datetime.now()

    try:
        logger.info(f"📊 Reranking {len(request.properties)} properties")
        logger.info(f"🔍 Query: {request.query}")
        logger.info(f"📈 Strategy: {request.strategy}")

        # Validate input
        if not request.properties:
            raise HTTPException(status_code=400, detail="No properties provided")

        # Rerank based on strategy
        if USE_REAL:
            embeddings = get_embeddings()

            if request.strategy == RerankingStrategy.SEMANTIC:
                ranked = await rerank_semantic(request.query, request.properties, embeddings)
            elif request.strategy == RerankingStrategy.HYBRID:
                ranked = await rerank_hybrid(request.query, request.properties, embeddings)
            elif request.strategy == RerankingStrategy.POPULARITY:
                ranked = await rerank_popularity(request.query, request.properties)
            elif request.strategy == RerankingStrategy.RECENCY:
                ranked = await rerank_recency(request.query, request.properties)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")
        else:
            # Mock mode
            ranked = await rerank_mock(request.query, request.properties, request.strategy)

        # Apply top_k filter if specified
        if request.top_k:
            ranked = ranked[:request.top_k]

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Generate overall explanation
        strategy_explanations = {
            RerankingStrategy.SEMANTIC: "Results ranked by semantic similarity to your query.",
            RerankingStrategy.HYBRID: "Results ranked using a combination of semantic relevance, popularity, and recency.",
            RerankingStrategy.POPULARITY: "Results ranked by popularity (views and likes).",
            RerankingStrategy.RECENCY: "Results ranked by how recently they were posted."
        }

        explanation = strategy_explanations.get(
            request.strategy,
            "Results reranked based on selected strategy."
        )

        logger.info(f"✅ Reranking completed in {processing_time:.0f}ms")
        logger.info(f"📊 Top result: {ranked[0].property_id} (score: {ranked[0].relevance_score:.2f})")

        return RerankingResponse(
            success=True,
            query=request.query,
            strategy=request.strategy,
            total_properties=len(ranked),
            reranked_properties=ranked,
            processing_time_ms=processing_time,
            model="gpt-4o-mini" if USE_REAL else "mock",
            explanation=explanation
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Reranking failed: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return RerankingResponse(
            success=False,
            query=request.query,
            strategy=request.strategy,
            total_properties=0,
            reranked_properties=[],
            processing_time_ms=processing_time,
            model="gpt-4o-mini" if USE_REAL else "mock",
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reranking",
        "mode": "real" if USE_REAL else "mock",
        "core_gateway": CORE_GATEWAY_URL,
        "strategies": [s.value for s in RerankingStrategy],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Reranking Service",
        "version": "1.0.0",
        "description": "Rerank search results based on query relevance",
        "strategies": {
            "semantic": "Pure semantic similarity matching",
            "hybrid": "Semantic + popularity + recency (recommended)",
            "popularity": "Most popular properties first",
            "recency": "Most recent properties first"
        },
        "endpoints": {
            "rerank": "POST /rerank",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Reranking Service starting...")
    logger.info(f"🔧 Mode: {'REAL' if USE_REAL else 'MOCK'}")
    logger.info(f"🔧 Core Gateway: {CORE_GATEWAY_URL}")
    logger.info(f"📈 Available strategies: {[s.value for s in RerankingStrategy]}")
    logger.info("✅ Reranking Service ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
