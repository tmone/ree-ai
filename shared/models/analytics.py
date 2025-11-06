"""
Analytics models for REE AI platform

Track user actions and provide insights for sellers and platform admins.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class ActionType(str, Enum):
    """Types of user actions to track"""
    VIEW = "view"  # Viewed property details
    FAVORITE = "favorite"  # Added to favorites
    UNFAVORITE = "unfavorite"  # Removed from favorites
    CONTACT = "contact"  # Contacted seller
    SEARCH = "search"  # Performed search
    SHARE = "share"  # Shared property


class UserAction(BaseModel):
    """Single user action"""
    id: int
    user_id: str
    action_type: ActionType
    property_id: Optional[str] = None  # NULL for search actions
    metadata: Optional[Dict[str, Any]] = None  # Search query, filters, etc.
    created_at: datetime


class UserActionCreate(BaseModel):
    """Create user action (for tracking)"""
    action_type: ActionType
    property_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PropertyViewStats(BaseModel):
    """Property view statistics"""
    property_id: str
    total_views: int
    unique_views: int
    views_by_day: List[Dict[str, Any]]  # [{"date": "2025-01-15", "count": 50}]
    avg_time_on_page: float  # seconds
    bounce_rate: float  # 0.0 to 1.0


class UserBehaviorStats(BaseModel):
    """User behavior statistics"""
    user_id: str
    total_searches: int
    total_views: int
    total_favorites: int
    total_contacts: int
    avg_searches_per_session: float
    preferred_property_types: List[str]
    preferred_districts: List[str]
    price_range: Dict[str, float]  # {"min": 2000000000, "max": 5000000000}


class PlatformStats(BaseModel):
    """Platform-wide statistics"""
    period: str  # "last_7_days", "last_30_days", "all_time"
    total_users: int
    new_users: int
    active_users: int
    total_sellers: int
    total_buyers: int
    active_listings: int
    new_listings: int
    total_searches: int
    total_views: int
    total_inquiries: int
    avg_searches_per_user: float
    top_search_terms: List[Dict[str, Any]]  # [{"term": "căn hộ quận 7", "count": 1500}]
    top_districts: List[Dict[str, Any]]
    top_property_types: List[Dict[str, Any]]
