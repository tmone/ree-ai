"""
Favorites models for REE AI platform

Allows buyers to save and organize favorite properties.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    """Add property to favorites"""
    property_id: str
    notes: Optional[str] = Field(None, max_length=500)  # User's private notes


class FavoriteUpdate(BaseModel):
    """Update favorite notes"""
    notes: Optional[str] = Field(None, max_length=500)


class Favorite(BaseModel):
    """Favorite property"""
    id: int
    user_id: str
    property_id: str
    notes: Optional[str] = None
    created_at: datetime


class FavoriteWithProperty(BaseModel):
    """Favorite with property details"""
    id: int
    user_id: str
    property_id: str
    notes: Optional[str] = None
    created_at: datetime

    # Property details (embedded)
    property: Optional[dict] = None  # Will contain PropertyDocument


class FavoriteListResponse(BaseModel):
    """List of user's favorites"""
    favorites: List[FavoriteWithProperty]
    total: int
    page: int = 1
    page_size: int = 20
