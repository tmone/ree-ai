"""
Field Presence Validation
Checks for required and recommended fields based on intent
"""

from typing import Dict, Any, List
from shared.utils.i18n import t
from services.validation.models.validation import ValidationResult, ValidationSeverity


# Required fields by intent
REQUIRED_FIELDS = {
    'POST_SALE': ['property_type', 'listing_type', 'price', 'district', 'contact_phone'],
    'POST_RENT': ['property_type', 'listing_type', 'price', 'district', 'contact_phone'],
}

# Recommended fields for better listing quality
RECOMMENDED_FIELDS = ['area', 'bedrooms', 'description', 'images', 'title']


def validate_required_fields(
    entities: Dict[str, Any],
    intent: str,
    language: str = 'vi'
) -> ValidationResult:
    """
    Check all required fields are present based on intent

    Args:
        entities: Extracted property attributes
        intent: User intent (POST_SALE, POST_RENT, etc.)
        language: User's preferred language

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
        errors = [
            t("validation.field_presence_missing_required", language=language, field=field)
            for field in missing
        ]
        return ValidationResult(
            valid=False,
            errors=errors,
            severity=ValidationSeverity.CRITICAL,
            suggestions=[
                {
                    "field": field,
                    "message": t(
                        "validation.field_presence_please_provide",
                        language=language,
                        field=field
                    )
                }
                for field in missing
            ]
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_recommended_fields(
    entities: Dict[str, Any],
    language: str = 'vi'
) -> ValidationResult:
    """
    Check recommended fields for better listing quality

    Args:
        entities: Extracted property attributes
        language: User's preferred language

    Returns:
        ValidationResult with warnings for missing recommended fields
    """
    warnings = []

    for field in RECOMMENDED_FIELDS:
        value = entities.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            warnings.append(
                t("validation.field_presence_consider_adding", language=language, field=field)
            )

    if warnings:
        return ValidationResult(
            valid=True,  # Warnings don't prevent saving
            warnings=warnings,
            severity=ValidationSeverity.WARNING,
            metadata={'missing_recommended': len(warnings)}
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_field_presence(
    entities: Dict[str, Any],
    intent: str,
    language: str = 'vi'
) -> ValidationResult:
    """
    Combined field presence validation (required + recommended)

    Args:
        entities: Extracted property attributes
        intent: User intent
        language: User's preferred language

    Returns:
        Aggregated ValidationResult
    """
    # Check required fields
    required_result = validate_required_fields(entities, intent, language)

    if not required_result.valid:
        # If required fields are missing, return immediately
        return required_result

    # Check recommended fields (only if required fields are present)
    recommended_result = validate_recommended_fields(entities, language)

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
