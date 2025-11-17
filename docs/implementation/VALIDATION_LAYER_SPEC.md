# Validation Layer Specification

**Part of CTO Architecture Priority 2: Attribute Extraction Enhancements**

## Overview

Post-extraction validation layer that verifies extracted attributes for consistency, completeness, and logical validity before saving to database.

## Purpose

Prevent bad data from entering the system by catching:
- **Logical Inconsistencies**: Price too low/high for area, bedrooms > total rooms
- **Missing Critical Fields**: No price, no location, no contact info
- **Format Errors**: Invalid phone numbers, malformed addresses
- **Business Rule Violations**: Minimum property listing requirements
- **Suspicious Patterns**: Duplicate listings, spam indicators

## Architecture

```
[User Input] → [Attribute Extraction] → [Validation Layer] → [Database]
                  (Priority 2)           (This Spec)          (if valid)
                                              ↓
                                      [Validation Errors] → [User Feedback]
```

## Validation Categories

### 1. Field Presence Validation

#### Required Fields
```python
REQUIRED_FIELDS = {
    'POST_SALE': ['property_type', 'listing_type', 'price', 'district', 'contact_phone'],
    'POST_RENT': ['property_type', 'listing_type', 'price', 'district', 'contact_phone'],
}

def validate_required_fields(entities: Dict, intent: str) -> ValidationResult:
    """Check all required fields are present"""
    required = REQUIRED_FIELDS.get(intent, [])
    missing = [f for f in required if not entities.get(f)]

    if missing:
        return ValidationResult(
            valid=False,
            errors=[f"Missing required field: {f}" for f in missing],
            severity='critical'
        )
    return ValidationResult(valid=True)
```

#### Recommended Fields
```python
RECOMMENDED_FIELDS = ['area', 'bedrooms', 'description', 'images']

def validate_recommended_fields(entities: Dict) -> List[str]:
    """Check recommended fields for better listing quality"""
    warnings = []
    for field in RECOMMENDED_FIELDS:
        if not entities.get(field):
            warnings.append(f"Consider adding {field} for better visibility")
    return warnings
```

### 2. Data Type & Format Validation

#### Numeric Range Validation
```python
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
    }
}

def validate_numeric_ranges(entities: Dict) -> ValidationResult:
    """Validate all numeric fields are within reasonable ranges"""
    errors = []

    for field, rules in VALIDATION_RULES.items():
        value = entities.get(field)
        if value is None:
            continue

        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be numeric, got {type(value).__name__}")
            continue

        if value < rules['min']:
            errors.append(
                f"{field} too low: {value} {rules.get('unit', '')} "
                f"(minimum: {rules['min']} {rules.get('unit', '')})"
            )

        if value > rules['max']:
            errors.append(
                f"{field} too high: {value} {rules.get('unit', '')} "
                f"(maximum: {rules['max']} {rules.get('unit', '')})"
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        severity='error'
    )
```

#### Contact Format Validation
```python
import re

PHONE_PATTERNS = [
    r'^0\d{9}$',        # Vietnamese: 0901234567
    r'^\+84\d{9}$',     # International: +84901234567
    r'^\d{10}$'         # Alternative: 0901234567
]

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False

    phone = re.sub(r'[\s\-\(\)]', '', phone)  # Remove formatting
    return any(re.match(pattern, phone) for pattern in PHONE_PATTERNS)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_contact_info(entities: Dict) -> ValidationResult:
    """Validate contact information formats"""
    errors = []

    phone = entities.get('contact_phone')
    if phone and not validate_phone_number(phone):
        errors.append(f"Invalid phone number format: {phone}")

    email = entities.get('contact_email')
    if email and not validate_email(email):
        errors.append(f"Invalid email format: {email}")

    # Must have at least one contact method
    if not phone and not email:
        errors.append("Must provide at least phone number or email")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        severity='error'
    )
```

### 3. Logical Consistency Validation

#### Cross-Field Validation
```python
def validate_logical_consistency(entities: Dict) -> ValidationResult:
    """Check logical relationships between fields"""
    warnings = []
    errors = []

    # Price per m² reasonableness check
    price = entities.get('price')
    area = entities.get('area')
    if price and area:
        price_per_sqm = price / area

        # District-specific price ranges (Ho Chi Minh City example)
        district_price_ranges = {
            'District 1': (50_000_000, 200_000_000),  # Premium downtown
            'District 7': (40_000_000, 150_000_000),  # Expat area
            'District 12': (10_000_000, 40_000_000),  # Outskirts
        }

        district = entities.get('district')
        if district in district_price_ranges:
            min_price, max_price = district_price_ranges[district]

            if price_per_sqm < min_price * 0.5:  # 50% below minimum
                warnings.append(
                    f"Price seems low for {district}: "
                    f"{price_per_sqm:,.0f} VND/m² (typical: {min_price:,.0f}-{max_price:,.0f})"
                )

            if price_per_sqm > max_price * 2:  # 200% above maximum
                warnings.append(
                    f"Price seems high for {district}: "
                    f"{price_per_sqm:,.0f} VND/m² (typical: {min_price:,.0f}-{max_price:,.0f})"
                )

    # Bedrooms vs bathrooms ratio
    bedrooms = entities.get('bedrooms', 0)
    bathrooms = entities.get('bathrooms', 0)
    if bedrooms and bathrooms:
        if bathrooms > bedrooms + 2:
            warnings.append(
                f"Unusual bathroom count: {bathrooms} bathrooms for {bedrooms} bedrooms"
            )

    # Area vs bedrooms correlation
    if area and bedrooms:
        area_per_bedroom = area / bedrooms if bedrooms > 0 else area

        if area_per_bedroom < 8:  # Less than 8m² per bedroom
            warnings.append(
                f"Small area for bedroom count: {area}m² for {bedrooms} bedrooms"
            )

        if area_per_bedroom > 100:  # More than 100m² per bedroom
            warnings.append(
                f"Large area for bedroom count: {area}m² for {bedrooms} bedrooms - "
                f"consider verifying bedroom count"
            )

    # Floor vs total floors
    floor = entities.get('floor')
    total_floors = entities.get('total_floors')
    if floor is not None and total_floors:
        if floor > total_floors:
            errors.append(
                f"Floor number ({floor}) cannot exceed total floors ({total_floors})"
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        severity='warning' if warnings and not errors else 'error'
    )
```

### 4. Spam & Fraud Detection

#### Suspicious Pattern Detection
```python
def validate_spam_indicators(entities: Dict, user_id: str) -> ValidationResult:
    """Detect potential spam or fraudulent listings"""
    spam_score = 0
    reasons = []

    # Check for excessive caps in title/description
    title = entities.get('title', '')
    description = entities.get('description', '')

    if sum(1 for c in title if c.isupper()) / max(len(title), 1) > 0.5:
        spam_score += 20
        reasons.append("Excessive uppercase in title")

    # Check for repeated punctuation
    if re.search(r'[!?]{3,}', title + description):
        spam_score += 15
        reasons.append("Excessive punctuation")

    # Check for common spam keywords
    spam_keywords = ['đảm bảo', 'chắc chắn', 'nhanh tay', 'giới hạn', 'cơ hội duy nhất']
    spam_count = sum(1 for keyword in spam_keywords if keyword in description.lower())
    if spam_count >= 3:
        spam_score += 25
        reasons.append(f"Multiple spam keywords detected ({spam_count})")

    # Check for duplicate phone across multiple listings
    phone = entities.get('contact_phone')
    if phone:
        recent_listings = get_recent_listings_by_phone(phone, days=1)
        if len(recent_listings) > 10:  # More than 10 listings per day
            spam_score += 40
            reasons.append("Suspicious posting frequency")

    # Check price = 0 or unrealistic
    price = entities.get('price', 0)
    if price == 0:
        spam_score += 30
        reasons.append("Price cannot be zero")

    # Spam threshold
    is_spam = spam_score >= 50

    return ValidationResult(
        valid=not is_spam,
        errors=["Listing flagged as potential spam"] if is_spam else [],
        warnings=reasons if spam_score > 0 and not is_spam else [],
        metadata={'spam_score': spam_score},
        severity='critical' if is_spam else 'warning'
    )
```

### 5. Duplicate Detection

```python
def validate_duplicate_listing(entities: Dict, user_id: str) -> ValidationResult:
    """Check if this property was already posted recently"""

    # Build fingerprint
    fingerprint_fields = ['district', 'area', 'price', 'bedrooms', 'property_type']
    fingerprint = hash(tuple(entities.get(f) for f in fingerprint_fields))

    # Check for similar listings from same user in last 7 days
    recent_listings = search_similar_listings(
        user_id=user_id,
        fingerprint=fingerprint,
        days=7
    )

    if recent_listings:
        return ValidationResult(
            valid=False,
            errors=[
                f"Similar listing already exists (ID: {recent_listings[0]['property_id']}). "
                "Please update existing listing instead of creating duplicate."
            ],
            severity='error',
            metadata={'duplicate_id': recent_listings[0]['property_id']}
        )

    return ValidationResult(valid=True)
```

## Validation Response Model

```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class ValidationSeverity(str, Enum):
    CRITICAL = "critical"  # Cannot proceed
    ERROR = "error"        # Should not proceed
    WARNING = "warning"    # Can proceed with caution
    INFO = "info"         # Informational only

class ValidationError(BaseModel):
    field: str
    message: str
    severity: ValidationSeverity
    suggested_value: Optional[Any] = None

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    severity: ValidationSeverity = ValidationSeverity.INFO
    metadata: Dict[str, Any] = {}

    # Suggestions for fixing errors
    suggestions: List[Dict[str, str]] = []

class ComprehensiveValidationResponse(BaseModel):
    overall_valid: bool
    confidence_score: float  # 0-100 how confident the extraction is
    validation_results: Dict[str, ValidationResult]  # By category

    # User-friendly summary
    summary: str
    next_steps: List[str]
```

## Integration with Property Posting Flow

```python
async def validate_and_save_property(entities: Dict, user_id: str) -> Dict:
    """Validate extracted attributes before saving"""

    # Run all validations
    validations = {
        'required_fields': validate_required_fields(entities, intent='POST_SALE'),
        'numeric_ranges': validate_numeric_ranges(entities),
        'contact_info': validate_contact_info(entities),
        'logical_consistency': validate_logical_consistency(entities),
        'spam_detection': validate_spam_indicators(entities, user_id),
        'duplicate_check': validate_duplicate_listing(entities, user_id)
    }

    # Aggregate results
    critical_errors = []
    errors = []
    warnings = []

    for category, result in validations.items():
        if result.severity == ValidationSeverity.CRITICAL:
            critical_errors.extend(result.errors)
        elif result.severity == ValidationSeverity.ERROR:
            errors.extend(result.errors)
        elif result.severity == ValidationSeverity.WARNING:
            warnings.extend(result.warnings)

    # Decision logic
    can_save = len(critical_errors) == 0 and len(errors) == 0

    if can_save:
        # Save to database
        property_id = await save_property_to_db(entities, user_id)

        return {
            'success': True,
            'property_id': property_id,
            'warnings': warnings,
            'message': 'Property saved successfully' +
                      (f' with {len(warnings)} warnings' if warnings else '')
        }
    else:
        # Return validation errors to user
        return {
            'success': False,
            'errors': critical_errors + errors,
            'warnings': warnings,
            'message': 'Please fix the errors before posting',
            'validations': validations
        }
```

## User Feedback & Corrections

### Interactive Validation
When validation fails, provide actionable feedback:

```python
def generate_user_feedback(validations: Dict) -> str:
    """Generate user-friendly validation feedback in Vietnamese"""

    messages = []

    # Critical errors
    critical = [v for v in validations.values() if v.severity == ValidationSeverity.CRITICAL]
    if critical:
        messages.append("❌ Lỗi nghiêm trọng (cần sửa):")
        for validation in critical:
            for error in validation.errors:
                messages.append(f"  - {translate_to_vietnamese(error)}")

    # Regular errors
    errors = [v for v in validations.values() if v.severity == ValidationSeverity.ERROR]
    if errors:
        messages.append("\n⚠️ Lỗi cần sửa:")
        for validation in errors:
            for error in validation.errors:
                messages.append(f"  - {translate_to_vietnamese(error)}")

    # Warnings
    warnings = [v for v in validations.values() if v.severity == ValidationSeverity.WARNING]
    if warnings:
        messages.append("\nℹ️ Khuyến nghị:")
        for validation in warnings:
            for warning in validation.warnings:
                messages.append(f"  - {translate_to_vietnamese(warning)}")

    return "\n".join(messages)
```

## Testing Strategy

### Unit Tests
```python
def test_price_validation():
    # Too low
    result = validate_numeric_ranges({'price': 50_000_000})
    assert not result.valid
    assert 'too low' in result.errors[0]

    # Valid
    result = validate_numeric_ranges({'price': 5_000_000_000})
    assert result.valid

    # Too high
    result = validate_numeric_ranges({'price': 150_000_000_000})
    assert not result.valid
```

### Integration Tests
- Test full validation pipeline
- Test with real property data
- Test edge cases and boundary conditions

## Performance

- **Latency Target**: <10ms per validation
- **Caching**: Cache master data (districts, price ranges)
- **Async Validation**: Run independent validators in parallel

## Monitoring

- **Validation Failure Rate**: Track % of listings failing validation
- **Common Errors**: Dashboard of top validation errors
- **False Positives**: User appeals of incorrect validation

---

**Status:** SPECIFICATION COMPLETE
**Implementation Time:** 2-3 days
**Dependencies**: Attribute extraction models (Priority 2)
**Priority**: HIGH (prevents bad data ingestion)
