"""
Attribute Extraction Service
Extracts structured attributes from property descriptions using LLM
- Area (m², sqft)
- Bedrooms, bathrooms
- Price
- Location
- Property type
- Amenities
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import httpx
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from shared.utils.logger import get_logger
from shared.config import get_settings

# Logger & Settings
logger = get_logger(__name__)
settings = get_settings()

# App
app = FastAPI(
    title="REE AI - Attribute Extraction Service",
    description="Extract structured attributes from property descriptions",
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


class PropertyAttributes(BaseModel):
    """Extracted property attributes"""
    # Basic Info
    property_type: PropertyType = Field(description="Type of property")
    title: Optional[str] = Field(None, description="Property title")

    # Size
    area_sqm: Optional[float] = Field(None, description="Area in square meters")
    land_area_sqm: Optional[float] = Field(None, description="Land area in square meters (for houses/villas)")

    # Rooms
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms")
    floors: Optional[int] = Field(None, description="Number of floors")

    # Price
    price_vnd: Optional[float] = Field(None, description="Price in VND")
    price_per_sqm: Optional[float] = Field(None, description="Price per square meter")

    # Location
    address: Optional[str] = Field(None, description="Full address")
    district: Optional[str] = Field(None, description="District")
    city: Optional[str] = Field(None, description="City")

    # Features
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    furniture: Optional[str] = Field(None, description="Furniture status (furnished/unfurnished/partial)")

    # Additional
    year_built: Optional[int] = Field(None, description="Year built")
    direction: Optional[str] = Field(None, description="Direction (East, West, etc)")
    legal_status: Optional[str] = Field(None, description="Legal document status")

    # Confidence
    confidence_score: float = Field(0.0, description="Extraction confidence (0-1)")


class ExtractionRequest(BaseModel):
    """Extraction request"""
    text: str = Field(..., description="Property description text")
    language: str = Field("vi", description="Language (vi/en)")


class ExtractionResponse(BaseModel):
    """Extraction response"""
    success: bool
    attributes: Optional[PropertyAttributes] = None
    raw_text: str
    processing_time_ms: float
    model: str
    error: Optional[str] = None


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
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=f"{CORE_GATEWAY_URL}/v1"
        )
    else:
        # Mock mode - return mock LLM
        return None


# ============================================================
# EXTRACTION LOGIC
# ============================================================

# Extraction prompt
EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert real estate data extractor for Vietnam market.
Extract structured attributes from property descriptions accurately.

Rules:
1. Extract all available information
2. Convert prices to VND (1 tỷ = 1,000,000,000 VND)
3. Convert areas to square meters (m²)
4. Identify property type correctly
5. Extract location details (address, district, city)
6. List all amenities mentioned
7. Set confidence_score based on information completeness (0.0-1.0)

Language: {language}
"""),
    ("user", "Extract attributes from this property description:\n\n{text}")
])


async def extract_attributes_real(text: str, language: str = "vi") -> PropertyAttributes:
    """Extract attributes using real LLM"""
    try:
        llm = get_llm()

        # Create parser
        parser = PydanticOutputParser(pydantic_object=PropertyAttributes)

        # Create chain
        prompt = EXTRACTION_PROMPT.partial(
            language=language,
            format_instructions=parser.get_format_instructions()
        )

        chain = prompt | llm | parser

        # Extract
        result = await chain.ainvoke({"text": text, "language": language})

        logger.info(f"✅ Extracted {len(result.amenities)} amenities")

        return result

    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}")
        raise


async def extract_attributes_mock(text: str, language: str = "vi") -> PropertyAttributes:
    """Mock extraction for development"""
    logger.info("🎭 Using MOCK extraction")

    # Simple keyword-based extraction for demo
    text_lower = text.lower()

    # Detect property type
    property_type = PropertyType.APARTMENT
    if "nhà" in text_lower or "house" in text_lower:
        property_type = PropertyType.HOUSE
    elif "villa" in text_lower or "biệt thự" in text_lower:
        property_type = PropertyType.VILLA
    elif "đất" in text_lower or "land" in text_lower:
        property_type = PropertyType.LAND

    # Extract numbers (simple)
    bedrooms = None
    if "2pn" in text_lower or "2 pn" in text_lower:
        bedrooms = 2
    elif "3pn" in text_lower or "3 pn" in text_lower:
        bedrooms = 3

    # Mock amenities
    amenities = []
    if "ban công" in text_lower or "balcony" in text_lower:
        amenities.append("Balcony")
    if "hồ bơi" in text_lower or "pool" in text_lower:
        amenities.append("Swimming Pool")
    if "gym" in text_lower:
        amenities.append("Gym")
    if "bảo vệ" in text_lower or "security" in text_lower:
        amenities.append("Security 24/7")

    return PropertyAttributes(
        property_type=property_type,
        bedrooms=bedrooms,
        amenities=amenities,
        confidence_score=0.7
    )


# ============================================================
# ENDPOINTS
# ============================================================

@app.post("/extract", response_model=ExtractionResponse)
async def extract_attributes(request: ExtractionRequest):
    """
    Extract structured attributes from property description

    Example:
    ```json
    {
        "text": "Căn hộ 2PN 80m² tại Quận 1, giá 5 tỷ. Có ban công, hồ bơi, gym.",
        "language": "vi"
    }
    ```
    """
    start_time = datetime.now()

    try:
        logger.info(f"📝 Extracting attributes from text ({len(request.text)} chars)")

        # Extract attributes
        if USE_REAL:
            attributes = await extract_attributes_real(request.text, request.language)
        else:
            attributes = await extract_attributes_mock(request.text, request.language)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"✅ Extraction completed in {processing_time:.0f}ms")

        return ExtractionResponse(
            success=True,
            attributes=attributes,
            raw_text=request.text,
            processing_time_ms=processing_time,
            model="gpt-4o-mini" if USE_REAL else "mock"
        )

    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return ExtractionResponse(
            success=False,
            raw_text=request.text,
            processing_time_ms=processing_time,
            model="gpt-4o-mini" if USE_REAL else "mock",
            error=str(e)
        )


@app.post("/batch-extract")
async def batch_extract_attributes(texts: List[str], language: str = "vi"):
    """
    Extract attributes from multiple property descriptions

    Example:
    ```json
    {
        "texts": [
            "Căn hộ 2PN 80m² tại Quận 1...",
            "Nhà 3 tầng 100m² tại Quận 2..."
        ],
        "language": "vi"
    }
    ```
    """
    try:
        logger.info(f"📦 Batch extracting from {len(texts)} texts")

        results = []
        for text in texts:
            request = ExtractionRequest(text=text, language=language)
            result = await extract_attributes(request)
            results.append(result)

        logger.info(f"✅ Batch extraction completed: {len(results)} results")

        return {
            "success": True,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"❌ Batch extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "attribute_extraction",
        "mode": "real" if USE_REAL else "mock",
        "core_gateway": CORE_GATEWAY_URL,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Attribute Extraction Service",
        "version": "1.0.0",
        "description": "Extract structured attributes from property descriptions",
        "endpoints": {
            "extract": "POST /extract",
            "batch": "POST /batch-extract",
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
    logger.info("🚀 Attribute Extraction Service starting...")
    logger.info(f"🔧 Mode: {'REAL' if USE_REAL else 'MOCK'}")
    logger.info(f"🔧 Core Gateway: {CORE_GATEWAY_URL}")
    logger.info("✅ Attribute Extraction Service ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
