"""
Logical Consistency Validation
Cross-field validation and logical relationship checks
"""

from typing import Dict, Any
from shared.utils.i18n import t
from services.validation.models.validation import ValidationResult, ValidationSeverity


# District-specific price ranges (Ho Chi Minh City example - VND per m²)
DISTRICT_PRICE_RANGES = {
    'district_1': (50_000_000, 200_000_000),   # Premium downtown
    'district_2': (40_000_000, 120_000_000),   # Thu Thiem new CBD
    'district_3': (40_000_000, 100_000_000),
    'district_4': (30_000_000, 80_000_000),
    'district_5': (30_000_000, 90_000_000),
    'district_7': (40_000_000, 150_000_000),   # Expat area (Phu My Hung)
    'district_10': (30_000_000, 70_000_000),
    'district_12': (10_000_000, 40_000_000),   # Outskirts
    'binh_thanh': (35_000_000, 90_000_000),
    'tan_binh': (30_000_000, 80_000_000),
    'phu_nhuan': (40_000_000, 100_000_000),
}


def validate_price_per_area(
    entities: Dict[str, Any],
    language: str = 'vi'
) -> ValidationResult:
    """
    Validate price per m² is reasonable for the district

    Args:
        entities: Extracted property attributes
        language: User's preferred language

    Returns:
        ValidationResult with warnings for unusual prices
    """
    price = entities.get('price')
    area = entities.get('area')
    district = entities.get('district')

    warnings = []

    if not (price and area):
        # Cannot check without both values
        return ValidationResult(valid=True, severity=ValidationSeverity.INFO)

    price_per_sqm = price / area

    # Check against district-specific ranges
    if district and district in DISTRICT_PRICE_RANGES:
        min_price, max_price = DISTRICT_PRICE_RANGES[district]

        if price_per_sqm < min_price * 0.5:  # 50% below minimum
            warnings.append(
                t("validation.logical_price_low",
                  language=language,
                  district=district,
                  price_per_sqm=f"{price_per_sqm:,.0f}",
                  min_price=f"{min_price:,.0f}",
                  max_price=f"{max_price:,.0f}")
            )

        if price_per_sqm > max_price * 2:  # 200% above maximum
            warnings.append(
                t("validation.logical_price_high",
                  language=language,
                  district=district,
                  price_per_sqm=f"{price_per_sqm:,.0f}",
                  min_price=f"{min_price:,.0f}",
                  max_price=f"{max_price:,.0f}")
            )

    if warnings:
        return ValidationResult(
            valid=True,  # Warnings don't prevent saving
            warnings=warnings,
            severity=ValidationSeverity.WARNING,
            metadata={'price_per_sqm': price_per_sqm}
        )

    return ValidationResult(
        valid=True,
        severity=ValidationSeverity.INFO,
        metadata={'price_per_sqm': price_per_sqm}
    )


def validate_bedrooms_bathrooms(
    entities: Dict[str, Any],
    language: str = 'vi'
) -> ValidationResult:
    """
    Validate bedroom to bathroom ratio is reasonable

    Args:
        entities: Extracted property attributes
        language: User's preferred language

    Returns:
        ValidationResult with warnings for unusual ratios
    """
    bedrooms = entities.get('bedrooms', 0)
    bathrooms = entities.get('bathrooms', 0)

    warnings = []

    if bedrooms and bathrooms:
        if bathrooms > bedrooms + 2:
            warnings.append(
                t("validation.logical_bathroom_unusual",
                  language=language,
                  bathrooms=bathrooms,
                  bedrooms=bedrooms)
            )

    if warnings:
        return ValidationResult(
            valid=True,
            warnings=warnings,
            severity=ValidationSeverity.WARNING
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_area_bedrooms(
    entities: Dict[str, Any],
    language: str = 'vi'
) -> ValidationResult:
    """
    Validate area is reasonable for number of bedrooms

    Args:
        entities: Extracted property attributes
        language: User's preferred language

    Returns:
        ValidationResult with warnings for unusual area/bedroom ratios
    """
    area = entities.get('area')
    bedrooms = entities.get('bedrooms')

    warnings = []

    if area and bedrooms:
        area_per_bedroom = area / bedrooms if bedrooms > 0 else area

        if area_per_bedroom < 8:  # Less than 8m² per bedroom
            warnings.append(
                t("validation.logical_area_small",
                  language=language,
                  area=area,
                  bedrooms=bedrooms,
                  area_per_bedroom=f"{area_per_bedroom:.1f}")
            )

        if area_per_bedroom > 100:  # More than 100m² per bedroom
            warnings.append(
                t("validation.logical_area_large",
                  language=language,
                  area=area,
                  bedrooms=bedrooms,
                  area_per_bedroom=f"{area_per_bedroom:.1f}")
            )

    if warnings:
        return ValidationResult(
            valid=True,
            warnings=warnings,
            severity=ValidationSeverity.WARNING
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_floor_vs_total_floors(
    entities: Dict[str, Any],
    language: str = 'vi'
) -> ValidationResult:
    """
    Validate floor number does not exceed total floors

    Args:
        entities: Extracted property attributes
        language: User's preferred language

    Returns:
        ValidationResult with errors for impossible floor numbers
    """
    floor = entities.get('floor')
    total_floors = entities.get('total_floors')

    errors = []

    if floor is not None and total_floors:
        if floor > total_floors:
            errors.append(
                t("validation.logical_floor_exceeds",
                  language=language,
                  floor=floor,
                  total_floors=total_floors)
            )

    if errors:
        return ValidationResult(
            valid=False,
            errors=errors,
            severity=ValidationSeverity.ERROR
        )

    return ValidationResult(valid=True, severity=ValidationSeverity.INFO)


def validate_logical_consistency(
    entities: Dict[str, Any],
    language: str = 'vi'
) -> ValidationResult:
    """
    Combined logical consistency validation

    Args:
        entities: Extracted property attributes
        language: User's preferred language

    Returns:
        Aggregated ValidationResult
    """
    # Run all consistency checks
    price_area_result = validate_price_per_area(entities, language)
    bedrooms_bathrooms_result = validate_bedrooms_bathrooms(entities, language)
    area_bedrooms_result = validate_area_bedrooms(entities, language)
    floor_result = validate_floor_vs_total_floors(entities, language)

    # Aggregate results
    all_errors = (
        price_area_result.errors +
        bedrooms_bathrooms_result.errors +
        area_bedrooms_result.errors +
        floor_result.errors
    )

    all_warnings = (
        price_area_result.warnings +
        bedrooms_bathrooms_result.warnings +
        area_bedrooms_result.warnings +
        floor_result.warnings
    )

    # Determine overall validity
    overall_valid = all(
        result.valid
        for result in [
            price_area_result,
            bedrooms_bathrooms_result,
            area_bedrooms_result,
            floor_result
        ]
    )

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
            **price_area_result.metadata,
            'total_consistency_checks': 4
        }
    )
