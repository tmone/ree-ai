"""
Saved Searches models for REE AI platform

Allows buyers to save search criteria and receive notifications
when new properties match their criteria.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from shared.models.db_gateway import SearchFilters


class SavedSearchCreate(BaseModel):
    """Create a saved search"""
    search_name: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[SearchFilters] = None

    # Notification settings
    notify_new_listings: bool = True
    notify_price_drops: bool = True


class SavedSearchUpdate(BaseModel):
    """Update saved search"""
    search_name: Optional[str] = Field(None, min_length=1, max_length=100)
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None
    notify_new_listings: Optional[bool] = None
    notify_price_drops: Optional[bool] = None


class SavedSearch(BaseModel):
    """Saved search"""
    id: int
    user_id: str
    search_name: str
    query: str
    filters: Optional[Dict[str, Any]] = None
    notify_new_listings: bool
    notify_price_drops: bool
    created_at: datetime
    updated_at: datetime
    last_notified_at: Optional[datetime] = None

    # Metadata
    new_matches_count: int = 0  # New properties since last check


class SavedSearchListResponse(BaseModel):
    """List of user's saved searches"""
    saved_searches: List[SavedSearch]
    total: int


class SavedSearchMatch(BaseModel):
    """Property matching a saved search"""
    saved_search_id: int
    property_id: str
    match_score: float  # Relevance score
    created_at: datetime
    notified: bool = False
