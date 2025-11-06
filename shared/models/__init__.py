"""Shared Pydantic models for inter-service communication."""

from shared.models.core_gateway import (
    LLMRequest,
    LLMResponse,
    Message,
    ModelType,
)

from shared.models.db_gateway import (
    SearchRequest,
    SearchResponse,
    PropertyResult,
    SearchFilters,
    ConversationMessage,
    SaveConversationRequest,
    GetConversationRequest,
    ConversationResponse,
    PropertyDocument,
    IndexDocumentRequest,
    IndexDocumentResponse,
)

from shared.models.orchestrator import (
    ChatRequest,
    ChatResponse,
    Intent,
)

# New user type models
from shared.models.users import (
    User,
    UserType,
    UserRole,
    UserPreferences,
    UserRegistration,
    UserLogin,
    UserUpdate,
    UpdatePreferences,
    UserResponse,
    AuthTokens,
)

# Enhanced property models
from shared.models.properties import (
    PropertyStatus,
    VerificationStatus,
    ListingType,
    PropertyType,
    PropertyCreate,
    PropertyUpdate,
    PropertyListResponse,
    PropertyStatusUpdate,
    PropertyAnalytics,
    ImageUploadRequest,
    BulkPropertyUpload,
)

# Favorites models
from shared.models.favorites import (
    FavoriteCreate,
    FavoriteUpdate,
    Favorite,
    FavoriteWithProperty,
    FavoriteListResponse,
)

# Saved searches models
from shared.models.saved_searches import (
    SavedSearchCreate,
    SavedSearchUpdate,
    SavedSearch,
    SavedSearchListResponse,
    SavedSearchMatch,
)

# Inquiries models
from shared.models.inquiries import (
    InquiryStatus,
    InquiryCreate,
    InquiryResponse,
    InquiryStatusUpdate,
    Inquiry,
    InquiryWithDetails,
    InquiryListResponse,
    InquiryStats,
)

# Analytics models
from shared.models.analytics import (
    ActionType,
    UserAction,
    UserActionCreate,
    PropertyViewStats,
    UserBehaviorStats,
    PlatformStats,
)

__all__ = [
    # Core Gateway
    "LLMRequest",
    "LLMResponse",
    "Message",
    "ModelType",
    # DB Gateway
    "SearchRequest",
    "SearchResponse",
    "PropertyResult",
    "SearchFilters",
    "ConversationMessage",
    "SaveConversationRequest",
    "GetConversationRequest",
    "ConversationResponse",
    "PropertyDocument",
    "IndexDocumentRequest",
    "IndexDocumentResponse",
    # Orchestrator
    "ChatRequest",
    "ChatResponse",
    "Intent",
    # Users
    "User",
    "UserType",
    "UserRole",
    "UserPreferences",
    "UserRegistration",
    "UserLogin",
    "UserUpdate",
    "UpdatePreferences",
    "UserResponse",
    "AuthTokens",
    # Properties
    "PropertyStatus",
    "VerificationStatus",
    "ListingType",
    "PropertyType",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyListResponse",
    "PropertyStatusUpdate",
    "PropertyAnalytics",
    "ImageUploadRequest",
    "BulkPropertyUpload",
    # Favorites
    "FavoriteCreate",
    "FavoriteUpdate",
    "Favorite",
    "FavoriteWithProperty",
    "FavoriteListResponse",
    # Saved Searches
    "SavedSearchCreate",
    "SavedSearchUpdate",
    "SavedSearch",
    "SavedSearchListResponse",
    "SavedSearchMatch",
    # Inquiries
    "InquiryStatus",
    "InquiryCreate",
    "InquiryResponse",
    "InquiryStatusUpdate",
    "Inquiry",
    "InquiryWithDetails",
    "InquiryListResponse",
    "InquiryStats",
    # Analytics
    "ActionType",
    "UserAction",
    "UserActionCreate",
    "PropertyViewStats",
    "UserBehaviorStats",
    "PlatformStats",
]
