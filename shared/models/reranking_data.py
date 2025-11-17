"""
Pydantic models for Re-ranking Phase 2 data infrastructure
CTO Priority 4 - Phase 2: Data tables for ML-based ranking
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# Seller Stats Model
# ============================================================================

class SellerStats(BaseModel):
    """Seller performance metrics for reputation scoring"""
    seller_id: str

    # Listing metrics
    total_listings: int = 0
    active_listings: int = 0
    closed_deals: int = 0

    # Communication metrics
    total_inquiries: int = 0
    total_responses: int = 0
    avg_response_time_hours: Optional[float] = None

    # Performance scores (auto-calculated by trigger)
    response_rate: float = 0.0
    closure_rate: float = 0.0

    # Account info
    account_created_at: datetime
    last_listing_at: Optional[datetime] = None

    # Metadata
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SellerStatsCreate(BaseModel):
    """Create seller stats"""
    seller_id: str
    total_listings: int = 0
    active_listings: int = 0
    closed_deals: int = 0
    total_inquiries: int = 0
    total_responses: int = 0
    avg_response_time_hours: Optional[float] = None
    account_created_at: Optional[datetime] = None


class SellerStatsUpdate(BaseModel):
    """Update seller stats"""
    total_listings: Optional[int] = None
    active_listings: Optional[int] = None
    closed_deals: Optional[int] = None
    total_inquiries: Optional[int] = None
    total_responses: Optional[int] = None
    avg_response_time_hours: Optional[float] = None
    last_listing_at: Optional[datetime] = None


# ============================================================================
# Property Stats Model
# ============================================================================

class PropertyStats(BaseModel):
    """Property engagement metrics"""
    property_id: str

    # View metrics
    views_total: int = 0
    views_7d: int = 0
    views_30d: int = 0
    last_viewed_at: Optional[datetime] = None

    # Inquiry metrics
    inquiries_total: int = 0
    inquiries_7d: int = 0
    inquiries_30d: int = 0
    last_inquiry_at: Optional[datetime] = None

    # Favorite metrics
    favorites_total: int = 0
    favorites_7d: int = 0
    favorites_30d: int = 0
    last_favorited_at: Optional[datetime] = None

    # CTR metrics
    search_impressions: int = 0
    search_clicks: int = 0
    ctr: float = 0.0

    # Metadata
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PropertyStatsCreate(BaseModel):
    """Create property stats"""
    property_id: str


class PropertyStatsUpdate(BaseModel):
    """Update property stats (increment counters)"""
    views_increment: int = 0
    inquiries_increment: int = 0
    favorites_increment: int = 0
    search_impressions_increment: int = 0
    search_clicks_increment: int = 0


# ============================================================================
# User Preferences Model
# ============================================================================

class UserPreferences(BaseModel):
    """User search preferences for personalization"""
    user_id: str

    # Price preferences
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    avg_clicked_price: Optional[int] = None

    # Location preferences
    preferred_districts: List[str] = Field(default_factory=list)
    preferred_cities: List[str] = Field(default_factory=list)

    # Property type preferences
    preferred_property_types: List[str] = Field(default_factory=list)

    # Size preferences
    preferred_bedrooms: Optional[List[int]] = None
    preferred_bathrooms: Optional[List[int]] = None
    preferred_area_min: Optional[float] = None
    preferred_area_max: Optional[float] = None

    # Search history stats
    total_searches: int = 0
    total_clicks: int = 0
    total_inquiries: int = 0
    total_favorites: int = 0

    # Metadata
    last_search_at: Optional[datetime] = None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesCreate(BaseModel):
    """Create user preferences"""
    user_id: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    preferred_districts: List[str] = Field(default_factory=list)
    preferred_cities: List[str] = Field(default_factory=list)
    preferred_property_types: List[str] = Field(default_factory=list)
    preferred_bedrooms: Optional[List[int]] = None


class UserPreferencesUpdate(BaseModel):
    """Update user preferences"""
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    preferred_districts: Optional[List[str]] = None
    preferred_cities: Optional[List[str]] = None
    preferred_property_types: Optional[List[str]] = None
    preferred_bedrooms: Optional[List[int]] = None
    preferred_bathrooms: Optional[List[int]] = None
    preferred_area_min: Optional[float] = None
    preferred_area_max: Optional[float] = None


# ============================================================================
# Search Interactions Model
# ============================================================================

class SearchInteraction(BaseModel):
    """User interaction with search result"""
    id: UUID
    user_id: Optional[str] = None
    query: str
    session_id: Optional[str] = None

    # Property and ranking
    property_id: str
    rank_position: int

    # Interaction signals
    clicked: bool = False
    inquiry_sent: bool = False
    favorited: bool = False
    time_on_page_seconds: int = 0

    # Context
    device_type: Optional[str] = None
    user_location: Optional[str] = None
    time_of_day: Optional[str] = None

    # Property features snapshot
    property_features: Dict[str, Any] = Field(default_factory=dict)

    # Search metadata
    search_type: str = "hybrid"
    hybrid_score: Optional[float] = None
    rerank_score: Optional[float] = None
    final_score: Optional[float] = None

    # Timestamp
    timestamp: datetime

    class Config:
        from_attributes = True


class SearchInteractionCreate(BaseModel):
    """Create search interaction"""
    user_id: Optional[str] = None
    query: str
    session_id: Optional[str] = None
    property_id: str
    rank_position: int
    clicked: bool = False
    inquiry_sent: bool = False
    favorited: bool = False
    time_on_page_seconds: int = 0
    device_type: Optional[str] = None
    user_location: Optional[str] = None
    time_of_day: Optional[str] = None
    property_features: Dict[str, Any] = Field(default_factory=dict)
    search_type: str = "hybrid"
    hybrid_score: Optional[float] = None
    rerank_score: Optional[float] = None
    final_score: Optional[float] = None


class SearchInteractionUpdate(BaseModel):
    """Update search interaction (e.g., mark as clicked)"""
    clicked: Optional[bool] = None
    inquiry_sent: Optional[bool] = None
    favorited: Optional[bool] = None
    time_on_page_seconds: Optional[int] = None
