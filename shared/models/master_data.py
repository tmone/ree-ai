"""
Master Data Models
Pydantic models for PostgreSQL master data tables
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class MasterDistrict(BaseModel):
    """District master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    city: str
    aliases: List[str] = Field(default_factory=list)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterWard(BaseModel):
    """Ward master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    district_id: int
    aliases: List[str] = Field(default_factory=list)
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterPropertyType(BaseModel):
    """Property type master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    aliases: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    typical_min_area: Optional[float] = None
    typical_max_area: Optional[float] = None
    typical_min_bedrooms: Optional[int] = None
    typical_max_bedrooms: Optional[int] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterTransactionType(BaseModel):
    """Transaction type master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    aliases: List[str] = Field(default_factory=list)
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterAmenity(BaseModel):
    """Amenity master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    aliases: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterFurnitureType(BaseModel):
    """Furniture type master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    aliases: List[str] = Field(default_factory=list)
    level: int = 0
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterDirection(BaseModel):
    """Direction master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    aliases: List[str] = Field(default_factory=list)
    degrees: Optional[int] = None
    feng_shui_score: Optional[int] = None
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterLegalStatus(BaseModel):
    """Legal status master data model"""
    id: Optional[int] = None
    code: str
    name_vi: str
    name_en: str
    aliases: List[str] = Field(default_factory=list)
    trust_level: Optional[int] = None
    description: Optional[str] = None
    active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MasterPriceRange(BaseModel):
    """Price range master data model"""
    id: Optional[int] = None
    district_id: int
    property_type_id: int
    min_price_per_m2: Optional[int] = None
    avg_price_per_m2: Optional[int] = None
    max_price_per_m2: Optional[int] = None
    min_total_price: Optional[int] = None
    avg_total_price: Optional[int] = None
    max_total_price: Optional[int] = None
    sample_count: int = 0
    last_updated: Optional[datetime] = None
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NormalizedEntity(BaseModel):
    """Normalized entity result from master data lookup"""
    original_value: str
    normalized_code: str
    normalized_name_vi: str
    normalized_name_en: str
    confidence: float  # 0.0 - 1.0
    match_type: str  # exact, alias, fuzzy


class ValidationResult(BaseModel):
    """Validation result from master data"""
    field_name: str
    original_value: any
    is_valid: bool
    normalized_entity: Optional[NormalizedEntity] = None
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
