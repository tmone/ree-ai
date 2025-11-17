"""
Field Presence Validation
Checks for required and recommended fields based on intent
"""

from typing import Dict, Any, List
from services.validation.models.validation import ValidationResult, ValidationSeverity


# Required fields by intent
REQUIRED_FIELDS = {
    'POST_SALE': ['property_type', 'listing_type', 'price', 'district', 'contact_phone'],
    'POST_RENT': ['property_type', 'listing_type', 'price', 'district', 'contact_phone'],
}

# Recommended fields for better listing quality
RECOMMENDED_FIELDS = ['area', 'bedrooms', 'description', 'images', 'title']


def validate_required_fields(entities: Dict[str, Any], intent: str) -> ValidationResult:
    """
    Check all required fields are present based on intent

    Args:
        entities: Extracted property attributes
        intent: User intent (POST_SALE, POST_RENT, etc.)

    Returns:
        ValidationResult with errors for missing required fields
    """
    required = REQUIRED_FIELDS.get(intent, [])
    missing = []

    for field in required:
        value = entities.get(field)
        # Check if field is missing, None, or empty string
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)

    if missing:
        errors = [f"Missing required field: {field}" for field in missing]
        return ValidationResult(
            valid=False,
            errors=errors,
            severity=ValidationSeverity.CRITICAL,
            suggestions=[
                {
                    "field": field,
                    "message": f"Please provide {field} to continue"
                }
                for field in missing
            ]
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_recommended_fields(entities: Dict[str, Any]) -> ValidationResult:
    """
    Check recommended fields for better listing quality

    Args:
        entities: Extracted property attributes

    Returns:
        ValidationResult with warnings for missing recommended fields
    """
    warnings = []

    for field in RECOMMENDED_FIELDS:
        value = entities.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            warnings.append(f"Consider adding '{field}' for better visibility and user engagement")

    if warnings:
        return ValidationResult(
            valid=True,  # Warnings don't prevent saving
            warnings=warnings,
            severity=ValidationSeverity.WARNING,
            metadata={'missing_recommended': len(warnings)}
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_field_presence(entities: Dict[str, Any], intent: str) -> ValidationResult:
    """
    Combined field presence validation (required + recommended)

    Args:
        entities: Extracted property attributes
        intent: User intent

    Returns:
        Aggregated ValidationResult
    """
    # Check required fields
    required_result = validate_required_fields(entities, intent)

    if not required_result.valid:
        # If required fields are missing, return immediately
        return required_result

    # Check recommended fields (only if required fields are present)
    recommended_result = validate_recommended_fields(entities)

    # Combine results
    return ValidationResult(
        valid=required_result.valid,
        errors=required_result.errors + recommended_result.errors,
        warnings=required_result.warnings + recommended_result.warnings,
        severity=required_result.severity if not required_result.valid else recommended_result.severity,
        suggestions=required_result.suggestions + recommended_result.suggestions,
        metadata={
            **required_result.metadata,
            **recommended_result.metadata
        }
    )
