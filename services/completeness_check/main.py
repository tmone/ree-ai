"""
Completeness Check Service
Analyzes property listings and calculates completeness score
- Checks if all required fields are present
- Validates data quality
- Provides improvement suggestions
- Calculates overall score (0-100)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from shared.utils.logger import get_logger
from shared.config import get_settings

# Logger & Settings
logger = get_logger(__name__)
settings = get_settings()

# App
app = FastAPI(
    title="REE AI - Completeness Check Service",
    description="Analyze property listing completeness and quality",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

class PropertyData(BaseModel):
    """Property data for completeness check"""
    # Basic Info (Required)
    title: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None

    # Size
    area_sqm: Optional[float] = None
    land_area_sqm: Optional[float] = None

    # Rooms
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None

    # Price
    price_vnd: Optional[float] = None

    # Location
    address: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None

    # Images
    images: List[str] = Field(default_factory=list)

    # Features
    amenities: List[str] = Field(default_factory=list)

    # Additional
    year_built: Optional[int] = None
    direction: Optional[str] = None
    legal_status: Optional[str] = None


class FieldScore(BaseModel):
    """Score for individual field"""
    field_name: str
    is_present: bool
    is_valid: bool
    score: float  # 0-10
    issue: Optional[str] = None
    suggestion: Optional[str] = None


class CompletenessResult(BaseModel):
    """Completeness check result"""
    overall_score: float = Field(..., description="Overall score (0-100)")
    total_fields: int = Field(..., description="Total fields checked")
    filled_fields: int = Field(..., description="Number of filled fields")
    valid_fields: int = Field(..., description="Number of valid fields")

    # Scores by category
    basic_info_score: float
    location_score: float
    size_score: float
    price_score: float
    features_score: float
    media_score: float

    # Detailed scores
    field_scores: List[FieldScore]

    # Suggestions
    critical_missing: List[str] = Field(default_factory=list)
    important_missing: List[str] = Field(default_factory=list)
    nice_to_have_missing: List[str] = Field(default_factory=list)

    # Overall assessment
    quality_level: str  # "poor", "fair", "good", "excellent"
    can_publish: bool
    improvement_priority: List[str] = Field(default_factory=list)


class CompletenessRequest(BaseModel):
    """Completeness check request"""
    property_data: PropertyData


class CompletenessResponse(BaseModel):
    """Completeness check response"""
    success: bool
    result: Optional[CompletenessResult] = None
    processing_time_ms: float
    error: Optional[str] = None


# ============================================================
# FIELD DEFINITIONS
# ============================================================

# Field importance levels
CRITICAL_FIELDS = ["title", "property_type", "price_vnd", "city"]
IMPORTANT_FIELDS = ["description", "area_sqm", "bedrooms", "address", "district", "images"]
NICE_TO_HAVE_FIELDS = ["bathrooms", "amenities", "year_built", "direction", "legal_status"]


# ============================================================
# COMPLETENESS LOGIC
# ============================================================

def check_field(field_name: str, value: Any, property_data: PropertyData) -> FieldScore:
    """Check individual field"""
    is_present = value is not None
    is_valid = True
    score = 0.0
    issue = None
    suggestion = None

    if not is_present:
        issue = f"Field '{field_name}' is missing"
        suggestion = f"Please provide {field_name}"
        score = 0.0
    else:
        # Validate based on field type
        if field_name == "title":
            if len(value) < 10:
                is_valid = False
                issue = "Title too short"
                suggestion = "Title should be at least 10 characters"
                score = 5.0
            elif len(value) > 200:
                is_valid = False
                issue = "Title too long"
                suggestion = "Title should be under 200 characters"
                score = 7.0
            else:
                score = 10.0

        elif field_name == "description":
            if len(value) < 50:
                is_valid = False
                issue = "Description too short"
                suggestion = "Description should be at least 50 characters"
                score = 5.0
            elif len(value) > 5000:
                is_valid = False
                issue = "Description too long"
                suggestion = "Description should be under 5000 characters"
                score = 8.0
            else:
                score = 10.0

        elif field_name == "price_vnd":
            if value <= 0:
                is_valid = False
                issue = "Invalid price"
                suggestion = "Price must be greater than 0"
                score = 0.0
            elif value < 100_000_000:  # < 100M VND
                issue = "Price seems low"
                suggestion = "Please verify the price is correct"
                score = 7.0
            else:
                score = 10.0

        elif field_name == "area_sqm":
            if value <= 0:
                is_valid = False
                issue = "Invalid area"
                suggestion = "Area must be greater than 0"
                score = 0.0
            elif value < 10:
                issue = "Area seems very small"
                suggestion = "Please verify the area is correct"
                score = 7.0
            else:
                score = 10.0

        elif field_name == "bedrooms":
            if value <= 0:
                is_valid = False
                issue = "Invalid number of bedrooms"
                suggestion = "Bedrooms must be at least 1"
                score = 0.0
            elif value > 10:
                issue = "Very high number of bedrooms"
                suggestion = "Please verify this is correct"
                score = 8.0
            else:
                score = 10.0

        elif field_name == "images":
            if len(value) == 0:
                issue = "No images provided"
                suggestion = "Add at least 3-5 high-quality images"
                score = 0.0
            elif len(value) < 3:
                issue = "Too few images"
                suggestion = "Add more images (recommended: 5-10)"
                score = 5.0
            elif len(value) >= 5:
                score = 10.0
            else:
                score = 7.0

        else:
            # Default scoring for other fields
            score = 10.0 if is_valid else 5.0

    return FieldScore(
        field_name=field_name,
        is_present=is_present,
        is_valid=is_valid,
        score=score,
        issue=issue,
        suggestion=suggestion
    )


def calculate_completeness(property_data: PropertyData) -> CompletenessResult:
    """Calculate completeness score"""
    logger.info("🔍 Calculating completeness score...")

    # Check all fields
    field_scores = []

    # Convert property data to dict
    data_dict = property_data.dict()

    # Check all fields
    for field_name, value in data_dict.items():
        field_score = check_field(field_name, value, property_data)
        field_scores.append(field_score)

    # Calculate category scores
    basic_fields = ["title", "description", "property_type"]
    location_fields = ["address", "district", "city"]
    size_fields = ["area_sqm", "land_area_sqm", "bedrooms", "bathrooms"]
    price_fields = ["price_vnd"]
    features_fields = ["amenities", "year_built", "direction", "legal_status"]
    media_fields = ["images"]

    def calc_category_score(fields: List[str]) -> float:
        scores = [fs.score for fs in field_scores if fs.field_name in fields]
        return sum(scores) / len(scores) if scores else 0.0

    basic_info_score = calc_category_score(basic_fields)
    location_score = calc_category_score(location_fields)
    size_score = calc_category_score(size_fields)
    price_score = calc_category_score(price_fields)
    features_score = calc_category_score(features_fields)
    media_score = calc_category_score(media_fields)

    # Calculate overall score
    # Weighted average (critical fields matter more)
    weights = {
        "basic_info": 0.25,
        "location": 0.20,
        "size": 0.15,
        "price": 0.20,
        "features": 0.10,
        "media": 0.10
    }

    overall_score = (
        basic_info_score * weights["basic_info"] +
        location_score * weights["location"] +
        size_score * weights["size"] +
        price_score * weights["price"] +
        features_score * weights["features"] +
        media_score * weights["media"]
    ) * 10  # Scale to 0-100

    # Count fields
    total_fields = len(field_scores)
    filled_fields = sum(1 for fs in field_scores if fs.is_present)
    valid_fields = sum(1 for fs in field_scores if fs.is_valid)

    # Determine quality level
    if overall_score >= 85:
        quality_level = "excellent"
    elif overall_score >= 70:
        quality_level = "good"
    elif overall_score >= 50:
        quality_level = "fair"
    else:
        quality_level = "poor"

    # Can publish?
    can_publish = overall_score >= 60 and all(
        fs.is_present for fs in field_scores
        if fs.field_name in CRITICAL_FIELDS
    )

    # Missing fields by priority
    critical_missing = [
        fs.field_name for fs in field_scores
        if not fs.is_present and fs.field_name in CRITICAL_FIELDS
    ]
    important_missing = [
        fs.field_name for fs in field_scores
        if not fs.is_present and fs.field_name in IMPORTANT_FIELDS
    ]
    nice_to_have_missing = [
        fs.field_name for fs in field_scores
        if not fs.is_present and fs.field_name in NICE_TO_HAVE_FIELDS
    ]

    # Improvement priorities
    improvement_priority = []
    if critical_missing:
        improvement_priority.append(f"Add critical fields: {', '.join(critical_missing)}")
    if media_score < 5:
        improvement_priority.append("Add more high-quality images")
    if basic_info_score < 7:
        improvement_priority.append("Improve title and description quality")
    if location_score < 8:
        improvement_priority.append("Provide complete location information")

    logger.info(f"✅ Score calculated: {overall_score:.1f}/100 ({quality_level})")

    return CompletenessResult(
        overall_score=round(overall_score, 1),
        total_fields=total_fields,
        filled_fields=filled_fields,
        valid_fields=valid_fields,
        basic_info_score=round(basic_info_score, 1),
        location_score=round(location_score, 1),
        size_score=round(size_score, 1),
        price_score=round(price_score, 1),
        features_score=round(features_score, 1),
        media_score=round(media_score, 1),
        field_scores=field_scores,
        critical_missing=critical_missing,
        important_missing=important_missing,
        nice_to_have_missing=nice_to_have_missing,
        quality_level=quality_level,
        can_publish=can_publish,
        improvement_priority=improvement_priority
    )


# ============================================================
# ENDPOINTS
# ============================================================

@app.post("/check", response_model=CompletenessResponse)
async def check_completeness(request: CompletenessRequest):
    """
    Check property listing completeness

    Example:
    ```json
    {
        "property_data": {
            "title": "Căn hộ 2PN view đẹp",
            "description": "Căn hộ 2 phòng ngủ, 80m², tầng cao, view đẹp...",
            "property_type": "apartment",
            "area_sqm": 80,
            "bedrooms": 2,
            "bathrooms": 2,
            "price_vnd": 5000000000,
            "address": "123 Nguyễn Huệ",
            "district": "Quận 1",
            "city": "TP.HCM",
            "images": ["img1.jpg", "img2.jpg", "img3.jpg"],
            "amenities": ["Pool", "Gym", "Parking"]
        }
    }
    ```
    """
    start_time = datetime.now()

    try:
        logger.info("🔍 Checking property completeness...")

        result = calculate_completeness(request.property_data)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"✅ Check completed in {processing_time:.0f}ms")

        return CompletenessResponse(
            success=True,
            result=result,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"❌ Check failed: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return CompletenessResponse(
            success=False,
            processing_time_ms=processing_time,
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "completeness_check",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Completeness Check Service",
        "version": "1.0.0",
        "description": "Analyze property listing completeness and quality",
        "scoring": {
            "excellent": "85-100",
            "good": "70-84",
            "fair": "50-69",
            "poor": "0-49"
        },
        "endpoints": {
            "check": "POST /check",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Completeness Check Service starting...")
    logger.info("✅ Completeness Check Service ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
