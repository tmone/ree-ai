"""
Pydantic models for re-ranking service
CTO Priority 4: Re-ranking Service
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PropertyResult(BaseModel):
    """Property result from hybrid search"""
    property_id: str
    score: float = Field(..., description="Original hybrid search score")

    # Property attributes
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    listing_type: Optional[str] = None
    price: Optional[float] = None
    area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None

    # Location
    city: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None
    street_address: Optional[str] = None

    # Media
    images: Optional[List[str]] = Field(default_factory=list)
    videos: Optional[List[str]] = Field(default_factory=list)
    virtual_tour_url: Optional[str] = None

    # Contact
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    owner_id: Optional[str] = None

    # Metadata
    verified: Optional[bool] = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Additional fields
    amenities: Optional[List[str]] = Field(default_factory=list)
    legal_status: Optional[str] = None
    furniture: Optional[str] = None


class RerankRequest(BaseModel):
    """Request to re-rank search results"""
    query: str = Field(..., description="Original search query")
    results: List[PropertyResult] = Field(..., description="Results from hybrid search")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    language: str = Field("vi", description="User's preferred language (vi, en, th, ja)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class FeatureScores(BaseModel):
    """Individual feature scores for explainability"""
    completeness: float = Field(..., ge=0.0, le=1.0)
    seller_reputation: float = Field(..., ge=0.0, le=1.0)
    freshness: float = Field(..., ge=0.0, le=1.0)
    engagement: float = Field(..., ge=0.0, le=1.0)
    personalization: float = Field(..., ge=0.0, le=1.0)

    # Weighted score (for debugging)
    weighted_rerank_score: float = Field(..., ge=0.0, le=1.0)


class RankedPropertyResult(PropertyResult):
    """Property result with re-ranking scores"""
    final_score: float = Field(..., description="Final score after re-ranking")
    original_score: float = Field(..., description="Original hybrid search score")
    rerank_features: FeatureScores = Field(..., description="Feature scores breakdown")


class RerankMetadata(BaseModel):
    """Metadata about re-ranking process"""
    model_version: str = "1.0.0-rule-based"
    feature_weights: Dict[str, float]
    processing_time_ms: float
    properties_reranked: int
    phase: str = "Phase 1: Rule-based"


class RerankResponse(BaseModel):
    """Re-ranked results with explanations"""
    results: List[RankedPropertyResult]
    rerank_metadata: RerankMetadata
