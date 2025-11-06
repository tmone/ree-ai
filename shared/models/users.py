"""
User models for REE AI platform

Supports two primary user types:
- Seller/Landlord: Posts and manages property listings
- Buyer/Tenant: Searches and discovers properties
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserType(str, Enum):
    """User type classification"""
    SELLER = "seller"
    BUYER = "buyer"
    BOTH = "both"  # Can both post and search


class UserRole(str, Enum):
    """System role for permissions"""
    PENDING = "pending"  # Awaiting email verification
    USER = "user"  # Verified user
    ADMIN = "admin"  # Platform administrator


class UserPreferences(BaseModel):
    """User preferences and settings"""
    language: str = "vi"  # en, vi, zh
    currency: str = "VND"
    notifications_enabled: bool = True
    email_notifications: bool = True
    search_notifications: bool = True  # For saved searches
    price_drop_alerts: bool = True
    theme: str = "light"  # light, dark


class User(BaseModel):
    """Complete user model"""
    id: str
    email: EmailStr
    username: Optional[str] = None

    # User classification
    user_type: UserType
    role: UserRole = UserRole.PENDING

    # Profile
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    # Seller-specific fields
    company_name: Optional[str] = None  # For real estate agencies
    license_number: Optional[str] = None  # Real estate license
    verified: bool = False  # Email/phone verification

    # Settings
    preferences: Optional[UserPreferences] = None
    info: Optional[Dict[str, Any]] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None


class UserRegistration(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    user_type: UserType
    phone_number: Optional[str] = None
    company_name: Optional[str] = None  # For sellers


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company_name: Optional[str] = None
    license_number: Optional[str] = None


class UpdatePreferences(BaseModel):
    """Update user preferences"""
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None
    search_notifications: Optional[bool] = None
    price_drop_alerts: Optional[bool] = None


class UserResponse(BaseModel):
    """User response (no password)"""
    id: str
    email: str
    username: Optional[str] = None
    user_type: UserType
    role: UserRole
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company_name: Optional[str] = None
    verified: bool
    preferences: Optional[UserPreferences] = None
    created_at: datetime
    last_active_at: Optional[datetime] = None


class AuthTokens(BaseModel):
    """Authentication tokens"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse
