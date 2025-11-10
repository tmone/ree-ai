"""
Base Pydantic models with common validators

This module provides reusable base models and validation logic
for consistent API contracts across all services.

Usage:
    from shared.models.base import QueryRequest, PaginationParams

    # Inherit from base models to get automatic validation
    class SearchRequest(QueryRequest, PaginationParams):
        filters: Optional[Dict[str, Any]] = None

    # Use in FastAPI endpoints
    @app.post("/search")
    async def search(request: SearchRequest):
        # request.query is already validated (3-1000 chars, non-empty)
        # request.limit is validated (1-100)
        # request.offset is validated (>= 0)
        ...
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class QueryRequest(BaseModel):
    """
    Base model for query requests with validation

    Enforces:
    - Query length: 3-1000 characters
    - No empty/whitespace-only queries
    - Automatic trimming of leading/trailing whitespace
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-trim strings
        validate_assignment=True  # Validate on assignment
    )

    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="User query (3-1000 characters)",
        examples=["Tìm căn hộ 2 phòng ngủ quận 1"]
    )

    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        """Ensure query is not just whitespace"""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


class PaginationParams(BaseModel):
    """
    Reusable pagination parameters with validation

    Enforces:
    - Limit: 1-100 results per page
    - Offset: >= 0 (starting position)
    """

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Results per page (1-100)",
        examples=[5, 10, 20]
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Starting offset (0-indexed)",
        examples=[0, 10, 20]
    )


class TimestampedModel(BaseModel):
    """
    Base model with automatic timestamp fields

    Use for database models that track creation/modification time
    """

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Record creation timestamp"
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        description="Record last update timestamp"
    )


class UserIdentifiable(BaseModel):
    """
    Base model for requests requiring user identification

    Enforces:
    - user_id is required
    - user_id is not empty
    """

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User ID (required for user-specific operations)",
        examples=["user_123", "abc-def-ghi"]
    )

    @field_validator('user_id')
    @classmethod
    def user_id_not_empty(cls, v: str) -> str:
        """Ensure user_id is not just whitespace"""
        if not v or not v.strip():
            raise ValueError("user_id cannot be empty or whitespace only")
        return v.strip()


class FiltersModel(BaseModel):
    """
    Base model for search filters with validation

    Provides common filter validation and sanitization
    """

    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Search filters (key-value pairs)",
        examples=[
            {"district": "Quận 1", "price_max": 5000000000},
            {"property_type": "căn hộ", "bedrooms": 2}
        ]
    )

    @field_validator('filters')
    @classmethod
    def sanitize_filters(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Sanitize filters:
        - Remove None values
        - Remove empty strings
        - Return None if all filters removed
        """
        if not v:
            return None

        # Remove None and empty string values
        sanitized = {
            k: val for k, val in v.items()
            if val is not None and val != ""
        }

        return sanitized if sanitized else None


class ConversationRequest(UserIdentifiable):
    """
    Base model for conversation-related requests

    Includes both user_id and conversation_id with validation
    """

    conversation_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Conversation ID (optional, will use user_id if not provided)",
        examples=["conv_123", "abc-def-ghi"]
    )


class PropertyFilters(FiltersModel):
    """
    Specialized filters for property search

    Provides validation for common property search criteria
    """

    # Override filters with property-specific structure
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Property search filters",
        examples=[
            {
                "property_type": "căn hộ",
                "city": "Hồ Chí Minh",
                "district": "Quận 1",
                "price_min": 1000000000,
                "price_max": 5000000000,
                "bedrooms": 2,
                "area_min": 50,
                "area_max": 100
            }
        ]
    )

    @field_validator('filters')
    @classmethod
    def validate_property_filters(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate property-specific filters

        Checks:
        - Price range: min <= max
        - Area range: min <= max
        - Bedrooms: positive integer
        """
        if not v:
            return None

        # First sanitize (remove None/empty)
        v = cls.sanitize_filters(v)
        if not v:
            return None

        # Validate price range
        price_min = v.get("price_min")
        price_max = v.get("price_max")
        if price_min is not None and price_max is not None:
            if price_min > price_max:
                raise ValueError(f"price_min ({price_min}) cannot be greater than price_max ({price_max})")

        # Validate area range
        area_min = v.get("area_min")
        area_max = v.get("area_max")
        if area_min is not None and area_max is not None:
            if area_min > area_max:
                raise ValueError(f"area_min ({area_min}) cannot be greater than area_max ({area_max})")

        # Validate bedrooms
        bedrooms = v.get("bedrooms")
        if bedrooms is not None:
            if not isinstance(bedrooms, int) or bedrooms < 0:
                raise ValueError(f"bedrooms must be a non-negative integer, got {bedrooms}")

        return v


class ErrorResponse(BaseModel):
    """
    Standard error response format

    Use for consistent error responses across all services
    """

    error: str = Field(
        ...,
        description="Error code (machine-readable)",
        examples=["PROPERTY_NOT_FOUND", "INVALID_QUERY", "SERVICE_UNAVAILABLE"]
    )

    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Property with ID 'abc123' not found", "Query is too short"]
    )

    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context for debugging",
        examples=[{"property_id": "abc123"}, {"min_length": 3, "actual_length": 2}]
    )

    status_code: int = Field(
        ...,
        description="HTTP status code",
        examples=[400, 404, 500]
    )


class HealthCheckResponse(BaseModel):
    """
    Standard health check response

    Use for /health endpoints across all services
    """

    status: str = Field(
        ...,
        description="Health status",
        examples=["healthy", "unhealthy", "degraded"]
    )

    service: str = Field(
        ...,
        description="Service name",
        examples=["rag_service", "orchestrator", "db_gateway"]
    )

    version: str = Field(
        ...,
        description="Service version",
        examples=["1.0.0", "2.1.3"]
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp"
    )

    dependencies: Optional[Dict[str, str]] = Field(
        default=None,
        description="Status of dependent services",
        examples=[
            {"db_gateway": "healthy", "core_gateway": "healthy"},
            {"opensearch": "unhealthy", "postgres": "healthy"}
        ]
    )
