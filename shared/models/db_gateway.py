"""
DB Gateway models for database operations
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PropertyFilter(BaseModel):
    """Filters for property search"""
    region: Optional[str] = Field(None, description="Region/district name")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    property_type: Optional[str] = Field(None, description="Type: apartment, house, villa")

    class Config:
        json_schema_extra = {
            "example": {
                "region": "Quận 1",
                "min_price": 5000000000,
                "max_price": 10000000000,
                "bedrooms": 2,
                "property_type": "apartment"
            }
        }


class Property(BaseModel):
    """Property model"""
    id: str = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    price: float = Field(..., ge=0, description="Price in VND")
    location: str = Field(..., description="Location")
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    area: float = Field(..., ge=0, description="Area in m²")
    description: str = Field(..., description="Full description")
    property_type: str = Field(..., description="Type of property")
    created_at: Optional[datetime] = Field(None, description="Created timestamp")
    score: Optional[float] = Field(None, ge=0, le=1, description="Relevance score")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "prop_123456",
                "title": "Căn hộ 2 phòng ngủ Quận 1",
                "price": 8000000000,
                "location": "Quận 1, TP.HCM",
                "bedrooms": 2,
                "area": 75.5,
                "description": "Căn hộ đẹp, view đẹp...",
                "property_type": "apartment",
                "score": 0.95
            }
        }


class SearchRequest(BaseModel):
    """Request to search properties"""
    query: str = Field(..., description="Search query", min_length=1)
    filters: PropertyFilter = Field(
        default_factory=PropertyFilter,
        description="Filter criteria"
    )
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Tìm nhà 2 phòng ngủ",
                "filters": {
                    "region": "Quận 1",
                    "min_price": 5000000000,
                    "max_price": 10000000000
                },
                "limit": 10,
                "offset": 0
            }
        }


class SearchResponse(BaseModel):
    """Response from property search"""
    results: List[Property] = Field(..., description="List of properties")
    total: int = Field(..., ge=0, description="Total matching results")
    took_ms: int = Field(..., ge=0, description="Time taken in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "prop_123",
                        "title": "Căn hộ 2PN Quận 1",
                        "price": 8000000000,
                        "location": "Quận 1",
                        "bedrooms": 2,
                        "area": 75.5,
                        "description": "...",
                        "property_type": "apartment",
                        "score": 0.95
                    }
                ],
                "total": 5,
                "took_ms": 245
            }
        }
