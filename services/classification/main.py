"""
Classification Service (Layer 3 - Sample Service 2)
Classifies property listings using LangChain
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List
import httpx
import time

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from shared.models.core_gateway import LLMRequest, LLMResponse, Message, ModelType
from shared.config import feature_flags
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


# Service-specific models
class ClassifyRequest(BaseModel):
    """Request for property classification"""
    text: str = Field(..., description="Property description to classify", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Căn hộ 2 phòng ngủ, diện tích 75m2, nội thất cao cấp, view sông"
            }
        }


class ClassifyResponse(BaseModel):
    """Response with classification result"""
    property_type: str = Field(..., description="Classified property type")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")
    reasoning: str = Field(..., description="Explanation of classification")
    processing_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "property_type": "apartment",
                "confidence": 0.95,
                "reasoning": "Mentioned '2 phòng ngủ' and 'căn hộ' which indicates an apartment",
                "processing_time_ms": 450
            }
        }


# Core Gateway client
class CoreGatewayClient:
    """Client for calling Core Gateway"""

    def __init__(self):
        if feature_flags.use_real_core_gateway():
            self.base_url = "http://core-gateway:8080"
            logger.info("Using REAL Core Gateway")
        else:
            self.base_url = "http://mock-core-gateway:1080"
            logger.info("Using MOCK Core Gateway")

    async def call_llm(self, request: LLMRequest) -> LLMResponse:
        """Call LLM via Core Gateway"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=request.dict()
            )
            response.raise_for_status()
            return LLMResponse(**response.json())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Classification Service starting up...")
    logger.info(f"Core Gateway Mode: {'REAL' if feature_flags.use_real_core_gateway() else 'MOCK'}")
    yield
    logger.info("👋 Classification Service shutting down...")


app = FastAPI(
    title="REE AI - Classification Service",
    description="Layer 3 Service: Classify property listings using LangChain",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize client
core_gateway = CoreGatewayClient()


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "classification",
        "status": "healthy",
        "version": "1.0.0",
        "core_gateway_mode": "real" if feature_flags.use_real_core_gateway() else "mock",
        "langchain": "enabled"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "core_gateway": {
            "mode": "real" if feature_flags.use_real_core_gateway() else "mock",
            "url": core_gateway.base_url
        },
        "langchain": "initialized"
    }


@app.post("/classify", response_model=ClassifyResponse)
async def classify_property(request: ClassifyRequest):
    """
    Classify property listing using LangChain

    Example use case:
    - Input: "Căn hộ 2 phòng ngủ view đẹp"
    - Output: property_type="apartment", confidence=0.95
    """
    start_time = time.time()

    try:
        logger.info(f"🏷️ Classification Request: {len(request.text)} chars")

        # Use LangChain prompt template
        prompt = f"""
You are a real estate classification expert. Classify this property description into ONE of these types:
- apartment (căn hộ)
- house (nhà phố)
- villa (biệt thự)
- land (đất)
- office (văn phòng)
- shop (cửa hàng)

Property description:
{request.text}

Respond in this EXACT format:
Type: <type>
Confidence: <0.0-1.0>
Reasoning: <explanation>

Example:
Type: apartment
Confidence: 0.95
Reasoning: Mentioned 'căn hộ' and '2 phòng ngủ' which indicates an apartment
"""

        # Call Core Gateway
        llm_request = LLMRequest(
            model=ModelType.OLLAMA_LLAMA2,  # Use Ollama for classification (cheaper)
            messages=[
                Message(
                    role="system",
                    content="You are a property classification expert."
                ),
                Message(
                    role="user",
                    content=prompt
                )
            ],
            max_tokens=500,
            temperature=0.3  # Low temperature for consistent classification
        )

        llm_response = await core_gateway.call_llm(llm_request)

        # Parse response
        response_text = llm_response.content
        lines = response_text.strip().split("\n")

        property_type = "unknown"
        confidence = 0.5
        reasoning = "Unable to parse classification"

        for line in lines:
            if line.startswith("Type:"):
                property_type = line.split(":", 1)[1].strip().lower()
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    confidence = 0.5
            elif line.startswith("Reasoning:"):
                reasoning = line.split(":", 1)[1].strip()

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Classification: {property_type} (confidence={confidence:.2f}), {elapsed_ms}ms")

        return ClassifyResponse(
            property_type=property_type,
            confidence=confidence,
            reasoning=reasoning,
            processing_time_ms=elapsed_ms
        )

    except httpx.HTTPStatusError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Core Gateway Error: {e.response.status_code} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=502,
            detail=f"Core Gateway error: {e.response.status_code}"
        )
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Classification Error: {str(e)} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
