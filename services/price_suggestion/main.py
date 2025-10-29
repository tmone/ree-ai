"""
Price Suggestion Service
Suggests property prices based on features using AI-powered analysis
- Supports MOCK and REAL modes (USE_REAL_CORE_GATEWAY env var)
- Calculates price range (min, max, suggested)
- Provides pricing factors and confidence score
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from shared.utils.logger import setup_logger
from shared.config import settings

# Logger
logger = setup_logger(__name__)

# App
app = FastAPI(
    title="REE AI - Price Suggestion Service",
    description="AI-powered property price suggestions based on features",
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

class PropertyType(str, Enum):
    """Property types"""
    APARTMENT = "apartment"
    HOUSE = "house"
    VILLA = "villa"
    OFFICE = "office"
    LAND = "land"
    COMMERCIAL = "commercial"
    OTHER = "other"


class FurnitureStatus(str, Enum):
    """Furniture status"""
    FURNISHED = "furnished"
    UNFURNISHED = "unfurnished"
    PARTIAL = "partial"


class PropertyFeatures(BaseModel):
    """Property features for price suggestion"""
    # Basic Info
    property_type: PropertyType = Field(..., description="Type of property")

    # Location
    city: str = Field(..., description="City (e.g., Ho Chi Minh, Hanoi)")
    district: str = Field(..., description="District (e.g., District 1, Quan 2)")
    ward: Optional[str] = Field(None, description="Ward/commune")
    street: Optional[str] = Field(None, description="Street name")

    # Size
    area_sqm: float = Field(..., description="Floor area in square meters", gt=0)
    land_area_sqm: Optional[float] = Field(None, description="Land area in square meters (for houses/villas)")

    # Rooms
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms", ge=0)
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms", ge=0)
    floors: Optional[int] = Field(None, description="Number of floors", ge=1)

    # Features
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    furniture: Optional[FurnitureStatus] = Field(None, description="Furniture status")
    direction: Optional[str] = Field(None, description="Direction (East, West, etc)")
    year_built: Optional[int] = Field(None, description="Year built", ge=1900, le=2050)

    # Additional context
    nearby_landmarks: List[str] = Field(default_factory=list, description="Nearby landmarks (schools, malls, etc)")
    description: Optional[str] = Field(None, description="Additional description")


class PricingFactors(BaseModel):
    """Breakdown of pricing factors"""
    base_price: float = Field(..., description="Base price per sqm in VND")
    location_premium: float = Field(..., description="Location premium multiplier", ge=0)
    size_factor: float = Field(..., description="Size adjustment factor", ge=0)
    amenities_bonus: float = Field(..., description="Amenities bonus in VND", ge=0)
    condition_factor: float = Field(..., description="Condition/age factor", ge=0, le=2)
    furniture_bonus: float = Field(..., description="Furniture bonus in VND", ge=0)


class PriceSuggestion(BaseModel):
    """Price suggestion result"""
    suggested_price: float = Field(..., description="Suggested price in VND")
    min_price: float = Field(..., description="Minimum recommended price in VND")
    max_price: float = Field(..., description="Maximum recommended price in VND")
    price_per_sqm: float = Field(..., description="Price per square meter in VND")

    confidence_score: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)

    pricing_factors: PricingFactors = Field(..., description="Breakdown of pricing factors")

    market_insights: str = Field(..., description="Market insights and explanation")
    comparable_range: str = Field(..., description="Comparable properties price range")


class PriceSuggestionRequest(BaseModel):
    """Price suggestion request"""
    features: PropertyFeatures = Field(..., description="Property features")
    language: str = Field("vi", description="Language (vi/en)")


class PriceSuggestionResponse(BaseModel):
    """Price suggestion response"""
    success: bool
    suggestion: Optional[PriceSuggestion] = None
    processing_time_ms: float
    model: str
    error: Optional[str] = None


class BatchPriceSuggestionRequest(BaseModel):
    """Batch price suggestion request"""
    properties: List[PropertyFeatures] = Field(..., description="List of properties")
    language: str = Field("vi", description="Language (vi/en)")


# ============================================================
# LLM CONFIGURATION
# ============================================================

# Core Gateway URL
USE_REAL = os.getenv("USE_REAL_CORE_GATEWAY", "false").lower() == "true"
CORE_GATEWAY_URL = "http://core-gateway:8080" if USE_REAL else "http://mock-core-gateway:1080"

logger.info(f"🔧 Mode: {'REAL' if USE_REAL else 'MOCK'}")
logger.info(f"🔧 Core Gateway: {CORE_GATEWAY_URL}")


def get_llm():
    """Get LLM instance"""
    if USE_REAL:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,  # Low temperature for consistent pricing
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=f"{CORE_GATEWAY_URL}/v1"
        )
    else:
        # Mock mode - return None
        return None


# ============================================================
# PRICING LOGIC
# ============================================================

# Pricing prompt
PRICING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert real estate pricing analyst for the Vietnam market.
Provide accurate price suggestions based on property features and market data.

Market Context for Vietnam (2024-2025):
- Ho Chi Minh City: Premium districts (1, 2, 3, 7, Binh Thanh) average 80-150M VND/m²
- Hanoi: Premium districts (Ba Dinh, Hoan Kiem, Dong Da) average 60-120M VND/m²
- Mid-tier districts: 40-80M VND/m²
- Suburban areas: 20-50M VND/m²

Pricing Factors:
1. Location Premium: Premium districts +50-100%, good districts +20-50%, suburban +0-20%
2. Size Factor: Smaller units have higher price per m², larger units lower price per m²
3. Amenities Bonus: Pool +5-10%, Gym +3-5%, Security +2-3%, each amenity adds value
4. Condition Factor: New (2020+) +10-20%, 5-10 years 0-10%, 10+ years -10-20%
5. Furniture Bonus: Fully furnished +10-15%, partial +5-10%

Rules:
1. Calculate base price per m² based on location
2. Apply all adjustment factors
3. Provide min/max range (±10-15% from suggested)
4. Set confidence score based on data completeness
5. Provide clear market insights

Language: {language}
"""),
    ("user", """Suggest price for this property:

Property Type: {property_type}
Location: {location}
Area: {area_sqm} m²
Bedrooms: {bedrooms}
Bathrooms: {bathrooms}
Amenities: {amenities}
Furniture: {furniture}
Year Built: {year_built}
Additional: {additional_info}

Provide detailed pricing analysis.
{format_instructions}
""")
])


async def suggest_price_real(features: PropertyFeatures, language: str = "vi") -> PriceSuggestion:
    """Suggest price using real LLM"""
    try:
        llm = get_llm()

        # Create parser
        parser = PydanticOutputParser(pydantic_object=PriceSuggestion)

        # Prepare location string
        location_parts = [features.district, features.city]
        if features.ward:
            location_parts.insert(0, features.ward)
        location = ", ".join(location_parts)

        # Prepare additional info
        additional_info = []
        if features.land_area_sqm:
            additional_info.append(f"Land area: {features.land_area_sqm} m²")
        if features.direction:
            additional_info.append(f"Direction: {features.direction}")
        if features.nearby_landmarks:
            additional_info.append(f"Nearby: {', '.join(features.nearby_landmarks)}")
        if features.description:
            additional_info.append(features.description)

        # Create chain
        prompt = PRICING_PROMPT.partial(
            language=language,
            format_instructions=parser.get_format_instructions()
        )

        chain = prompt | llm | parser

        # Suggest price
        result = await chain.ainvoke({
            "property_type": features.property_type.value,
            "location": location,
            "area_sqm": features.area_sqm,
            "bedrooms": features.bedrooms or "Not specified",
            "bathrooms": features.bathrooms or "Not specified",
            "amenities": ", ".join(features.amenities) if features.amenities else "None",
            "furniture": features.furniture.value if features.furniture else "Not specified",
            "year_built": features.year_built or "Not specified",
            "additional_info": " | ".join(additional_info) if additional_info else "None",
            "language": language
        })

        logger.info(f"✅ Price suggested: {result.suggested_price:,.0f} VND (confidence: {result.confidence_score:.2f})")

        return result

    except Exception as e:
        logger.error(f"❌ Price suggestion failed: {str(e)}")
        raise


async def suggest_price_mock(features: PropertyFeatures, language: str = "vi") -> PriceSuggestion:
    """Mock price suggestion for development"""
    logger.info("🎭 Using MOCK price suggestion")

    # Simple rule-based pricing for demo

    # Base price per m² based on location
    base_price_per_sqm = 50_000_000  # 50M VND/m² default

    city_lower = features.city.lower()
    district_lower = features.district.lower()

    # Location premium
    location_premium = 1.0
    if "ho chi minh" in city_lower or "hcm" in city_lower:
        if any(d in district_lower for d in ["1", "2", "3", "7", "binh thanh"]):
            base_price_per_sqm = 100_000_000  # Premium district
            location_premium = 1.5
        else:
            base_price_per_sqm = 60_000_000  # Mid-tier
            location_premium = 1.2
    elif "hanoi" in city_lower or "hà nội" in city_lower:
        if any(d in district_lower for d in ["ba dinh", "hoan kiem", "dong da"]):
            base_price_per_sqm = 80_000_000  # Premium
            location_premium = 1.4
        else:
            base_price_per_sqm = 50_000_000
            location_premium = 1.1

    # Size factor (smaller = higher price per m²)
    size_factor = 1.0
    if features.area_sqm < 50:
        size_factor = 1.2
    elif features.area_sqm > 150:
        size_factor = 0.9

    # Amenities bonus (each amenity adds value)
    amenities_bonus = len(features.amenities) * 50_000_000  # 50M VND per amenity

    # Condition factor based on year
    condition_factor = 1.0
    if features.year_built:
        age = 2025 - features.year_built
        if age < 3:
            condition_factor = 1.15  # New
        elif age < 10:
            condition_factor = 1.0   # Good
        else:
            condition_factor = 0.85  # Older

    # Furniture bonus
    furniture_bonus = 0
    if features.furniture == FurnitureStatus.FURNISHED:
        furniture_bonus = features.area_sqm * 5_000_000  # 5M VND/m²
    elif features.furniture == FurnitureStatus.PARTIAL:
        furniture_bonus = features.area_sqm * 2_500_000  # 2.5M VND/m²

    # Calculate suggested price
    base_total = base_price_per_sqm * features.area_sqm
    adjusted_price = base_total * location_premium * size_factor * condition_factor
    suggested_price = adjusted_price + amenities_bonus + furniture_bonus

    # Price range (±12%)
    min_price = suggested_price * 0.88
    max_price = suggested_price * 1.12

    # Price per sqm
    price_per_sqm = suggested_price / features.area_sqm

    # Confidence score based on data completeness
    completeness_factors = [
        features.bedrooms is not None,
        features.bathrooms is not None,
        len(features.amenities) > 0,
        features.furniture is not None,
        features.year_built is not None,
        len(features.nearby_landmarks) > 0
    ]
    confidence_score = 0.6 + (sum(completeness_factors) / len(completeness_factors)) * 0.3

    # Market insights
    market_insights = f"Based on {features.district}, {features.city} market analysis. "
    if location_premium > 1.3:
        market_insights += "This is a premium location with high demand. "
    market_insights += f"Property age factor: {condition_factor:.2f}. "
    if amenities_bonus > 0:
        market_insights += f"Amenities add {amenities_bonus:,.0f} VND value."

    # Comparable range
    comparable_range = f"{min_price:,.0f} - {max_price:,.0f} VND for similar properties in the area"

    return PriceSuggestion(
        suggested_price=suggested_price,
        min_price=min_price,
        max_price=max_price,
        price_per_sqm=price_per_sqm,
        confidence_score=confidence_score,
        pricing_factors=PricingFactors(
            base_price=base_price_per_sqm,
            location_premium=location_premium,
            size_factor=size_factor,
            amenities_bonus=amenities_bonus,
            condition_factor=condition_factor,
            furniture_bonus=furniture_bonus
        ),
        market_insights=market_insights,
        comparable_range=comparable_range
    )


# ============================================================
# ENDPOINTS
# ============================================================

@app.post("/suggest", response_model=PriceSuggestionResponse)
async def suggest_price_endpoint(request: PriceSuggestionRequest):
    """
    Suggest property price based on features

    Example:
    ```json
    {
        "features": {
            "property_type": "apartment",
            "city": "Ho Chi Minh",
            "district": "District 1",
            "area_sqm": 80,
            "bedrooms": 2,
            "bathrooms": 2,
            "amenities": ["Swimming Pool", "Gym", "Security 24/7"],
            "furniture": "furnished",
            "year_built": 2020
        },
        "language": "vi"
    }
    ```
    """
    start_time = datetime.now()

    try:
        logger.info(f"💰 Price suggestion for {request.features.property_type.value} in {request.features.district}, {request.features.city}")

        # Suggest price
        if USE_REAL:
            suggestion = await suggest_price_real(request.features, request.language)
        else:
            suggestion = await suggest_price_mock(request.features, request.language)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"✅ Price suggestion completed in {processing_time:.0f}ms")

        return PriceSuggestionResponse(
            success=True,
            suggestion=suggestion,
            processing_time_ms=processing_time,
            model="gpt-4o-mini" if USE_REAL else "mock"
        )

    except Exception as e:
        logger.error(f"❌ Price suggestion failed: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return PriceSuggestionResponse(
            success=False,
            processing_time_ms=processing_time,
            model="gpt-4o-mini" if USE_REAL else "mock",
            error=str(e)
        )


@app.post("/batch-suggest")
async def batch_suggest_prices(request: BatchPriceSuggestionRequest):
    """
    Suggest prices for multiple properties

    Example:
    ```json
    {
        "properties": [
            {
                "property_type": "apartment",
                "city": "Ho Chi Minh",
                "district": "District 1",
                "area_sqm": 80,
                ...
            },
            {
                "property_type": "house",
                "city": "Hanoi",
                "district": "Ba Dinh",
                "area_sqm": 120,
                ...
            }
        ],
        "language": "vi"
    }
    ```
    """
    try:
        logger.info(f"📦 Batch price suggestion for {len(request.properties)} properties")

        results = []
        for features in request.properties:
            req = PriceSuggestionRequest(features=features, language=request.language)
            result = await suggest_price_endpoint(req)
            results.append(result)

        logger.info(f"✅ Batch suggestion completed: {len(results)} results")

        return {
            "success": True,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"❌ Batch suggestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "price_suggestion",
        "mode": "real" if USE_REAL else "mock",
        "core_gateway": CORE_GATEWAY_URL,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Price Suggestion Service",
        "version": "1.0.0",
        "description": "AI-powered property price suggestions based on features",
        "endpoints": {
            "suggest": "POST /suggest",
            "batch": "POST /batch-suggest",
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
    logger.info("🚀 Price Suggestion Service starting...")
    logger.info(f"🔧 Mode: {'REAL' if USE_REAL else 'MOCK'}")
    logger.info(f"🔧 Core Gateway: {CORE_GATEWAY_URL}")
    logger.info("✅ Price Suggestion Service ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
