"""
Validation Service
Post-extraction validation layer for property attributes
Layer 3 - AI Services
Port: 8086
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

from shared.utils.i18n import t

from services.validation.models.validation import (
    ValidationRequest,
    ComprehensiveValidationResponse,
    ValidationResult,
    ValidationSeverity
)
from services.validation.validators.field_presence import validate_field_presence
from services.validation.validators.data_format import validate_data_format
from services.validation.validators.logical_consistency import validate_logical_consistency
from services.validation.validators.spam_detection import validate_spam_indicators
from services.validation.validators.duplicate_detection import validate_duplicate_listing

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Validation Service",
    description="Post-extraction validation for property attributes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": t("validation.health_status", language="en"),
        "service": t("validation.health_service", language="en"),
        "version": "1.0.0"
    }


@app.post("/validate", response_model=ComprehensiveValidationResponse)
async def validate_property(request: ValidationRequest) -> ComprehensiveValidationResponse:
    """
    Validate extracted property attributes

    Runs 5 validation categories:
    1. Field Presence (required/recommended fields)
    2. Data Format (numeric ranges, contact info)
    3. Logical Consistency (cross-field checks)
    4. Spam Detection (suspicious patterns)
    5. Duplicate Detection (similar listings)

    Args:
        request: Validation request with entities and intent

    Returns:
        Comprehensive validation response
    """
    try:
        logger.info(f"Validating property for intent: {request.intent}")

        # Run all validations
        validations: Dict[str, ValidationResult] = {}

        # 1. Field presence validation
        validations['field_presence'] = validate_field_presence(
            request.entities,
            request.intent,
            request.language
        )

        # 2. Data format validation
        validations['data_format'] = validate_data_format(
            request.entities,
            request.language
        )

        # 3. Logical consistency validation
        validations['logical_consistency'] = validate_logical_consistency(
            request.entities,
            request.language
        )

        # 4. Spam detection
        validations['spam_detection'] = validate_spam_indicators(
            request.entities,
            request.user_id,
            request.language
        )

        # 5. Duplicate detection
        validations['duplicate_detection'] = validate_duplicate_listing(
            request.entities,
            request.user_id,
            request.language
        )

        # Aggregate results
        critical_errors = []
        errors = []
        warnings = []

        for category, result in validations.items():
            if result.severity == ValidationSeverity.CRITICAL:
                critical_errors.extend(result.errors)
            elif result.severity == ValidationSeverity.ERROR:
                errors.extend(result.errors)

            warnings.extend(result.warnings)

        # Determine overall validity
        overall_valid = all(result.valid for result in validations.values())
        can_save = len(critical_errors) == 0 and len(errors) == 0

        # Calculate confidence score (based on validation results)
        confidence_score = calculate_confidence_score(validations, request.entities)

        # Generate user-friendly summary
        summary = generate_summary(
            critical_errors, errors, warnings, can_save, request.language
        )

        # Generate next steps
        next_steps = generate_next_steps(
            critical_errors, errors, warnings, can_save, request.language
        )

        response = ComprehensiveValidationResponse(
            overall_valid=overall_valid,
            confidence_score=confidence_score,
            validation_results=validations,
            summary=summary,
            next_steps=next_steps,
            can_save=can_save,
            total_errors=len(critical_errors) + len(errors),
            total_warnings=len(warnings)
        )

        logger.info(f"Validation complete. Can save: {can_save}, Errors: {len(critical_errors) + len(errors)}, Warnings: {len(warnings)}")

        return response

    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        error_msg = t(
            "validation.validation_failed",
            language=request.language if hasattr(request, 'language') else 'vi',
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=error_msg)


def calculate_confidence_score(
    validations: Dict[str, ValidationResult],
    entities: Dict[str, Any]
) -> float:
    """
    Calculate confidence score based on validation results

    Args:
        validations: Results from all validators
        entities: Extracted property attributes

    Returns:
        Confidence score (0-100)
    """
    base_score = 100.0

    # Deduct for critical errors
    critical_count = sum(
        1 for v in validations.values()
        if v.severity == ValidationSeverity.CRITICAL
    )
    base_score -= critical_count * 30

    # Deduct for errors
    error_count = sum(
        1 for v in validations.values()
        if v.severity == ValidationSeverity.ERROR
    )
    base_score -= error_count * 15

    # Deduct for warnings
    warning_count = sum(len(v.warnings) for v in validations.values())
    base_score -= warning_count * 5

    # Boost for completeness
    recommended_fields = ['area', 'bedrooms', 'description', 'images', 'title']
    filled_recommended = sum(
        1 for field in recommended_fields
        if entities.get(field) is not None
    )
    completeness_bonus = (filled_recommended / len(recommended_fields)) * 10
    base_score += completeness_bonus

    return max(0.0, min(100.0, base_score))


def generate_summary(
    critical_errors: list,
    errors: list,
    warnings: list,
    can_save: bool,
    language: str = 'vi'
) -> str:
    """Generate user-friendly validation summary"""

    if can_save and not warnings:
        return t("validation.summary_all_passed", language=language)

    if can_save and warnings:
        return t(
            "validation.summary_can_save_with_warnings",
            language=language,
            count=len(warnings)
        )

    if critical_errors:
        return t(
            "validation.summary_critical_errors",
            language=language,
            count=len(critical_errors)
        )

    if errors:
        return t(
            "validation.summary_errors",
            language=language,
            count=len(errors)
        )

    return t("validation.summary_completed", language=language)


def generate_next_steps(
    critical_errors: list,
    errors: list,
    warnings: list,
    can_save: bool,
    language: str = 'vi'
) -> list[str]:
    """Generate actionable next steps for user"""

    steps = []

    if critical_errors:
        steps.append(t("validation.next_step_fix_critical", language=language))
        steps.extend(critical_errors[:3])  # Show first 3 critical errors

    if errors and not critical_errors:
        steps.append(t("validation.next_step_fix_errors", language=language))
        steps.extend(errors[:3])  # Show first 3 errors

    if warnings and can_save:
        steps.append(t("validation.next_step_consider_recommendations", language=language))
        steps.extend(warnings[:2])  # Show first 2 warnings

    if can_save and not steps:
        steps.append(t("validation.next_step_ready_to_save", language=language))

    return steps


if __name__ == "__main__":
    uvicorn.run(
        "services.validation.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
