"""
Data Type & Format Validation
Validates numeric ranges, contact information formats, and data types
"""

import re
from typing import Dict, Any
from services.validation.models.validation import ValidationResult, ValidationSeverity


# Numeric validation rules
VALIDATION_RULES = {
    'price': {
        'min': 100_000_000,      # 100M VND (~$4K USD)
        'max': 100_000_000_000,  # 100B VND (~$4M USD)
        'unit': 'VND'
    },
    'area': {
        'min': 10,    # 10 m²
        'max': 10000, # 10,000 m² (1 hectare)
        'unit': 'm²'
    },
    'bedrooms': {
        'min': 0,
        'max': 20
    },
    'bathrooms': {
        'min': 0,
        'max': 20
    },
    'floor': {
        'min': -5,  # Basement
        'max': 100  # Skyscraper
    },
    'total_floors': {
        'min': 1,
        'max': 100
    }
}

# Phone number patterns
PHONE_PATTERNS = [
    r'^0\d{9}$',        # Vietnamese: 0901234567
    r'^\+84\d{9}$',     # International: +84901234567
    r'^84\d{9}$',       # Alternative: 84901234567
]


def validate_numeric_ranges(entities: Dict[str, Any]) -> ValidationResult:
    """
    Validate all numeric fields are within reasonable ranges

    Args:
        entities: Extracted property attributes

    Returns:
        ValidationResult with errors for out-of-range values
    """
    errors = []

    for field, rules in VALIDATION_RULES.items():
        value = entities.get(field)

        if value is None:
            continue

        # Check type
        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be numeric, got {type(value).__name__}")
            continue

        # Check minimum
        if value < rules['min']:
            unit = rules.get('unit', '')
            errors.append(
                f"{field} too low: {value:,} {unit} "
                f"(minimum: {rules['min']:,} {unit})"
            )

        # Check maximum
        if value > rules['max']:
            unit = rules.get('unit', '')
            errors.append(
                f"{field} too high: {value:,} {unit} "
                f"(maximum: {rules['max']:,} {unit})"
            )

    if errors:
        return ValidationResult(
            valid=False,
            errors=errors,
            severity=ValidationSeverity.ERROR
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format

    Args:
        phone: Phone number string

    Returns:
        True if valid format
    """
    if not phone:
        return False

    # Remove common formatting characters
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)

    return any(re.match(pattern, phone) for pattern in PHONE_PATTERNS)


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address string

    Returns:
        True if valid format
    """
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_contact_info(entities: Dict[str, Any]) -> ValidationResult:
    """
    Validate contact information formats

    Args:
        entities: Extracted property attributes

    Returns:
        ValidationResult with errors for invalid contact info
    """
    errors = []
    warnings = []

    phone = entities.get('contact_phone')
    email = entities.get('contact_email')

    # Validate phone if present
    if phone:
        if not validate_phone_number(phone):
            errors.append(f"Invalid phone number format: {phone}. Expected format: 0901234567 or +84901234567")

    # Validate email if present
    if email:
        if not validate_email(email):
            errors.append(f"Invalid email format: {email}")

    # Must have at least one contact method
    if not phone and not email:
        errors.append("Must provide at least phone number or email for contact")

    # Warning if only one contact method
    if (phone and not email) or (email and not phone):
        warnings.append("Providing both phone and email increases response rate")

    if errors:
        return ValidationResult(
            valid=False,
            errors=errors,
            warnings=warnings,
            severity=ValidationSeverity.ERROR
        )

    if warnings:
        return ValidationResult(
            valid=True,
            warnings=warnings,
            severity=ValidationSeverity.WARNING
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_data_format(entities: Dict[str, Any]) -> ValidationResult:
    """
    Combined data format validation (numeric + contact)

    Args:
        entities: Extracted property attributes

    Returns:
        Aggregated ValidationResult
    """
    # Validate numeric ranges
    numeric_result = validate_numeric_ranges(entities)

    # Validate contact info
    contact_result = validate_contact_info(entities)

    # Aggregate results
    all_errors = numeric_result.errors + contact_result.errors
    all_warnings = numeric_result.warnings + contact_result.warnings

    # Determine overall validity and severity
    overall_valid = numeric_result.valid and contact_result.valid

    if not overall_valid:
        severity = ValidationSeverity.ERROR
    elif all_warnings:
        severity = ValidationSeverity.WARNING
    else:
        severity = ValidationSeverity.INFO

    return ValidationResult(
        valid=overall_valid,
        errors=all_errors,
        warnings=all_warnings,
        severity=severity,
        metadata={
            'numeric_errors': len(numeric_result.errors),
            'contact_errors': len(contact_result.errors)
        }
    )
