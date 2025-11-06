"""
Property models for REE AI platform

Enhanced property models with ownership, status tracking, and analytics.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PropertyStatus(str, Enum):
    """Property listing status"""
    DRAFT = "draft"  # Being created, not published
    PENDING = "pending"  # Awaiting moderation
    ACTIVE = "active"  # Published and visible
    SOLD = "sold"  # Property sold
    RENTED = "rented"  # Property rented
    PAUSED = "paused"  # Temporarily hidden by owner
    EXPIRED = "expired"  # Listing expired
    REJECTED = "rejected"  # Rejected by moderation


class VerificationStatus(str, Enum):
    """Property verification status"""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ListingType(str, Enum):
    """Type of listing"""
    SALE = "sale"
    RENT = "rent"


class PropertyType(str, Enum):
    """Property type (English master data)"""
    APARTMENT = "apartment"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    LAND = "land"
    OFFICE = "office"
    COMMERCIAL = "commercial"


class PropertyDocument(BaseModel):
    """
    Complete property document for OpenSearch.
    Uses flexible JSON schema to support unlimited attributes.
    """
    property_id: str
    owner_id: str  # User who posted this property

    # Basic info (English master data)
    title: str
    description: str
    property_type: str  # apartment, villa, townhouse, etc.
    listing_type: ListingType

    # Location (English)
    district: Optional[str] = None
    ward: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = "Ho Chi Minh City"

    # Core attributes
    price: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    floor: Optional[int] = None

    # Flexible attributes (unlimited additional fields)
    # Examples: swimming_pool, gym, parking, view, direction, furniture, etc.
    attributes: Optional[Dict[str, Any]] = None

    # Media
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    virtual_tour_url: Optional[str] = None

    # Status & Moderation
    status: PropertyStatus = PropertyStatus.DRAFT
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    rejection_reason: Optional[str] = None

    # SEO
    slug: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

    # Analytics
    views_count: int = 0
    favorites_count: int = 0
    inquiries_count: int = 0

    # Contact info (seller's choice)
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    show_contact_info: bool = True  # Privacy setting

    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Embedding for semantic search
    embedding: Optional[List[float]] = None


class PropertyCreate(BaseModel):
    """Request to create a new property"""
    # Basic info
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    property_type: str
    listing_type: ListingType

    # Location
    district: str
    ward: Optional[str] = None
    street: Optional[str] = None
    city: str = "Ho Chi Minh City"

    # Price
    price: float = Field(..., gt=0)

    # Core attributes
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[int] = Field(None, ge=0, le=20)
    area: Optional[float] = Field(None, gt=0, le=10000)
    floor: Optional[int] = Field(None, ge=0, le=100)

    # Flexible attributes
    attributes: Optional[Dict[str, Any]] = None

    # Contact preferences
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    show_contact_info: bool = True

    # Save as draft or publish immediately
    publish_immediately: bool = False


class PropertyUpdate(BaseModel):
    """Request to update property"""
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    price: Optional[float] = Field(None, gt=0)
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[int] = Field(None, ge=0, le=20)
    area: Optional[float] = Field(None, gt=0, le=10000)
    floor: Optional[int] = Field(None, ge=0, le=100)
    attributes: Optional[Dict[str, Any]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    show_contact_info: Optional[bool] = None


class PropertyListResponse(BaseModel):
    """Response for property list"""
    properties: List[PropertyDocument]
    total: int
    page: int = 1
    page_size: int = 20


class PropertyStatusUpdate(BaseModel):
    """Update property status"""
    status: PropertyStatus
    reason: Optional[str] = None  # Required for rejection


class PropertyAnalytics(BaseModel):
    """Property analytics"""
    property_id: str
    period: str  # "last_7_days", "last_30_days", "all_time"
    views: int
    unique_views: int
    favorites: int
    inquiries: int
    inquiry_response_rate: float
    avg_time_on_page: str  # "2m 35s"
    traffic_sources: Dict[str, int]  # {"search": 850, "direct": 200}


class ImageUploadRequest(BaseModel):
    """Request to upload property images"""
    property_id: str
    image_urls: List[str] = Field(..., min_items=1, max_items=10)


class BulkPropertyUpload(BaseModel):
    """Bulk property upload for agencies"""
    properties: List[PropertyCreate] = Field(..., max_items=100)
    auto_publish: bool = False
