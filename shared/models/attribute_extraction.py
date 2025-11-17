"""
Pydantic models for Attribute Extraction Service
Handles multi-language extraction with master data mapping
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MatchMethod(str, Enum):
    """How the attribute was matched to master data"""
    EXACT = "exact"              # Exact match with master data name
    ALIAS = "alias"              # Matched via name_variants/aliases
    FUZZY = "fuzzy"              # Fuzzy string matching
    LLM_NORMALIZED = "llm"       # LLM normalized the value before matching


class LanguageCode(str, Enum):
    """Supported languages for translations"""
    ENGLISH = "en"
    VIETNAMESE = "vi"
    CHINESE = "zh"
    KOREAN = "ko"
    JAPANESE = "ja"


class MappedAttribute(BaseModel):
    """
    Attribute successfully mapped to master data
    Returns both canonical English value and user's language translation
    """
    property_name: str = Field(
        ...,
        description="Attribute type (e.g., 'district', 'amenity', 'property_type')"
    )
    table: str = Field(
        ...,
        description="Master data table name (e.g., 'districts', 'amenities')"
    )
    id: int = Field(
        ...,
        description="Foreign key ID in master data table"
    )
    value: str = Field(
        ...,
        description="Canonical English value from master data"
    )
    value_translated: str = Field(
        ...,
        description="Translated value in user's language"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from matching (0.0 to 1.0)"
    )
    match_method: MatchMethod = Field(
        ...,
        description="How this attribute was matched"
    )
    original_input: Optional[str] = Field(
        None,
        description="Original text extracted from user input"
    )
    # CTO Architecture Priority 2: Enhanced tracking
    source_span: Optional[Dict[str, int]] = Field(
        None,
        description="Character positions in original text {'start': 0, 'end': 10}"
    )
    normalized_value: Optional[str] = Field(
        None,
        description="Standardized value (e.g., '5000000000' for '5 tỷ')"
    )
    unit: Optional[str] = Field(
        None,
        description="Unit of measurement (e.g., 'VND', 'm2', 'sqm')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "property_name": "district",
                "table": "districts",
                "id": 1,
                "value": "district_1",
                "value_translated": "Quận 1",
                "confidence": 1.0,
                "match_method": "exact",
                "original_input": "Q1"
            }
        }


class NewAttribute(BaseModel):
    """
    New attribute not found in master data - requires admin review
    """
    property_name: str = Field(
        ...,
        description="Attribute type this should belong to"
    )
    table: Optional[str] = Field(
        None,
        description="Always null for new items"
    )
    id: Optional[int] = Field(
        None,
        description="Always null for new items"
    )
    value: str = Field(
        ...,
        description="Normalized English value (LLM-translated if needed)"
    )
    value_original: str = Field(
        ...,
        description="Original value from user input"
    )
    suggested_table: Optional[str] = Field(
        None,
        description="Recommended master data table to add this to"
    )
    suggested_category: Optional[str] = Field(
        None,
        description="Recommended category within the table"
    )
    suggested_translations: Dict[str, str] = Field(
        default_factory=dict,
        description="Suggested translations for different languages {lang_code: translation}"
    )
    extraction_context: Optional[str] = Field(
        None,
        description="Surrounding text for context"
    )
    requires_admin_review: bool = Field(
        True,
        description="Flags that admin approval is needed"
    )
    frequency: int = Field(
        1,
        description="How many times this value appeared in extraction"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "property_name": "amenity",
                "table": None,
                "id": None,
                "value": "wine_cellar",
                "value_original": "hầm rượu",
                "suggested_table": "amenities",
                "suggested_category": "private_amenity",
                "suggested_translations": {
                    "vi": "Hầm rượu",
                    "en": "Wine cellar"
                },
                "extraction_context": "Biệt thự có hầm rượu riêng",
                "requires_admin_review": True,
                "frequency": 1
            }
        }


class RawExtraction(BaseModel):
    """
    Raw extracted data before normalization
    Includes numeric fields and unstructured text
    """
    text: str = Field(..., description="Original input text")

    # Numeric attributes (no master data needed)
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    area: Optional[float] = Field(None, gt=0, description="Property area in m²")
    price: Optional[float] = Field(None, gt=0, description="Price in VND")
    floor: Optional[int] = Field(None, ge=0, description="Floor number")
    total_floors: Optional[int] = Field(None, ge=1, description="Total floors in building")

    # CTO Architecture Priority 2: Enhanced extraction metadata
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Extraction confidence score")
    numeric_source_spans: Optional[Dict[str, Dict[str, int]]] = Field(
        None,
        description="Source positions for numeric fields {'price': {'start': 10, 'end': 15}}"
    )

    # Free-form text fields
    title: Optional[str] = Field(None, description="Property title")
    description: Optional[str] = Field(None, description="Full property description")

    # Metadata
    extracted_at: datetime = Field(
        default_factory=datetime.now,
        description="When extraction was performed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Căn hộ 2PN Quận 1, 80m2, có hồ bơi",
                "bedrooms": 2,
                "bathrooms": None,
                "area": 80.0,
                "price": None,
                "floor": None,
                "total_floors": None,
                "title": None,
                "description": None
            }
        }


class ExtractionResponse(BaseModel):
    """
    Complete extraction response with 3-tier structure:
    1. raw: Unstructured data and numeric fields
    2. mapped: Attributes matched to master data with translations
    3. new: Unmatched attributes requiring admin review
    """
    request_language: LanguageCode = Field(
        ...,
        description="Auto-detected language from user input"
    )
    raw: RawExtraction = Field(
        ...,
        description="Raw extracted data before master data mapping"
    )
    mapped: List[MappedAttribute] = Field(
        default_factory=list,
        description="Attributes successfully mapped to master data"
    )
    new: List[NewAttribute] = Field(
        default_factory=list,
        description="New attributes not found in master data"
    )
    extraction_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this extraction was completed"
    )
    extractor_version: str = Field(
        "1.0.0",
        description="Version of extraction service"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="Time taken for extraction in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_language": "vi",
                "raw": {
                    "text": "Căn hộ 2PN Quận 1, hướng Đông, có hồ bơi, gym",
                    "bedrooms": 2,
                    "bathrooms": None,
                    "area": None,
                    "price": None
                },
                "mapped": [
                    {
                        "property_name": "property_type",
                        "table": "property_types",
                        "id": 1,
                        "value": "apartment",
                        "value_translated": "Căn hộ",
                        "confidence": 0.98,
                        "match_method": "exact"
                    },
                    {
                        "property_name": "district",
                        "table": "districts",
                        "id": 1,
                        "value": "district_1",
                        "value_translated": "Quận 1",
                        "confidence": 1.0,
                        "match_method": "fuzzy"
                    }
                ],
                "new": [
                    {
                        "property_name": "amenity",
                        "value": "wine_cellar",
                        "value_original": "hầm rượu",
                        "suggested_table": "amenities",
                        "suggested_translations": {"vi": "Hầm rượu"}
                    }
                ],
                "extraction_timestamp": "2025-01-13T10:30:00Z",
                "extractor_version": "1.0.0",
                "processing_time_ms": 1250.5
            }
        }


class ExtractionRequest(BaseModel):
    """
    Request to extract attributes from text
    """
    text: str = Field(
        ...,
        min_length=1,
        description="Text to extract property attributes from"
    )
    language: Optional[LanguageCode] = Field(
        None,
        description="Override auto-detection with specific language"
    )
    user_id: Optional[str] = Field(
        None,
        description="User ID for tracking and learning"
    )
    confidence_threshold: float = Field(
        0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for auto-mapping (default 0.8)"
    )
    include_suggestions: bool = Field(
        True,
        description="Include AI suggestions for new attributes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Cần bán căn hộ 2PN tại Vinhomes Central Park Quận Bình Thạnh, 80m2, view sông, full nội thất",
                "language": "vi",
                "confidence_threshold": 0.8,
                "include_suggestions": True
            }
        }


class MasterDataLookupRequest(BaseModel):
    """
    Request to lookup master data with translations
    """
    table: str = Field(..., description="Master data table name")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Filter conditions"
    )
    language: LanguageCode = Field(
        LanguageCode.VIETNAMESE,
        description="Language for translations"
    )
    include_translations: bool = Field(
        True,
        description="Include all available translations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "table": "amenities",
                "filters": {"category": "shared_amenity"},
                "language": "vi",
                "include_translations": True
            }
        }


class MasterDataItem(BaseModel):
    """
    Single master data item with translations
    """
    id: int
    name: str = Field(..., description="Canonical English name")
    code: str
    translated_name: Optional[str] = Field(
        None,
        description="Name in requested language"
    )
    translations: Optional[Dict[str, str]] = Field(
        None,
        description="All available translations {lang_code: text}"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional table-specific fields"
    )


class MasterDataLookupResponse(BaseModel):
    """
    Response from master data lookup
    """
    table: str
    language: LanguageCode
    items: List[MasterDataItem]
    total_count: int


class PendingMasterDataApproval(BaseModel):
    """
    Admin action to approve/reject pending master data
    """
    pending_id: int = Field(..., description="ID from pending_master_data table")
    action: str = Field(..., description="'approve' or 'reject'")
    master_data_id: Optional[int] = Field(
        None,
        description="If mapped to existing item instead of creating new"
    )
    translations: Optional[Dict[str, str]] = Field(
        None,
        description="Admin-provided translations if approving"
    )
    admin_notes: Optional[str] = Field(
        None,
        description="Admin comments"
    )
    reviewed_by: str = Field(..., description="Admin user ID")


class PendingMasterDataListResponse(BaseModel):
    """
    List of pending master data items for admin review
    """
    items: List[NewAttribute]
    total_count: int
    high_frequency_items: List[NewAttribute] = Field(
        default_factory=list,
        description="Items that appear frequently (should prioritize)"
    )
