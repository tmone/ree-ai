"""
Pydantic models for Validation Service
Post-extraction validation for property attributes
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class ValidationSeverity(str, Enum):
    """Severity levels for validation results"""
    CRITICAL = "critical"  # Cannot proceed
    ERROR = "error"        # Should not proceed
    WARNING = "warning"    # Can proceed with caution
    INFO = "info"         # Informational only


class ValidationError(BaseModel):
    """Individual validation error with field information"""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Error message")
    severity: ValidationSeverity = Field(..., description="Error severity level")
    suggested_value: Optional[Any] = Field(None, description="Suggested correction if available")


class ValidationResult(BaseModel):
    """Result from a single validation category"""
    valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")
    severity: ValidationSeverity = Field(default=ValidationSeverity.INFO, description="Overall severity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional validation metadata")
    suggestions: List[Dict[str, str]] = Field(default_factory=list, description="Suggestions for fixing errors")


class ComprehensiveValidationResponse(BaseModel):
    """Complete validation response from all validators"""
    overall_valid: bool = Field(..., description="Overall validation status")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Extraction confidence (0-100)")
    validation_results: Dict[str, ValidationResult] = Field(
        ...,
        description="Results by category (required_fields, numeric_ranges, etc.)"
    )

    # User-friendly summary
    summary: str = Field(..., description="Human-readable validation summary")
    next_steps: List[str] = Field(default_factory=list, description="Actions user should take")

    # Metadata
    can_save: bool = Field(..., description="Whether property can be saved to database")
    total_errors: int = Field(0, description="Total critical + error count")
    total_warnings: int = Field(0, description="Total warning count")


class ValidationRequest(BaseModel):
    """Request to validate extracted property attributes"""
    intent: str = Field(
        ...,
        description="User intent (POST_SALE, POST_RENT, SEARCH, etc.)"
    )
    entities: Dict[str, Any] = Field(
        ...,
        description="Extracted entities/attributes from property description"
    )
    user_id: Optional[str] = Field(None, description="User ID for duplicate/spam detection")
    conversation_id: Optional[str] = Field(None, description="Conversation context")
    language: str = Field(
        "vi",
        description="User's preferred language (vi, en, th, ja)"
    )
    confidence_threshold: float = Field(
        0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for accepting attributes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "POST_SALE",
                "entities": {
                    "property_type": "apartment",
                    "district": "district_1",
                    "price": 5000000000,
                    "area": 80,
                    "bedrooms": 2,
                    "contact_phone": "0901234567"
                },
                "user_id": "user_123",
                "confidence_threshold": 0.8
            }
        }
