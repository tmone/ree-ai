"""
Semantic Chunking Service (Layer 3 - Sample Service)
This is a sample implementation showing how to:
1. Use shared models
2. Call Core Gateway for LLM
3. Implement service logic
4. Handle errors and logging
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List
import httpx
import time

from shared.models.core_gateway import LLMRequest, LLMResponse, Message, ModelType
from shared.config import settings, feature_flags
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


# Service-specific models
class ChunkRequest(BaseModel):
    """Request for semantic chunking"""
    text: str = Field(..., description="Text to chunk", min_length=1)
    max_chunk_size: int = Field(default=500, ge=100, le=2000, description="Max chars per chunk")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Căn hộ 2 phòng ngủ ở Quận 1, diện tích 75m2, giá 8 tỷ. Nội thất cao cấp, view đẹp.",
                "max_chunk_size": 500
            }
        }


class Chunk(BaseModel):
    """A semantic chunk"""
    index: int
    content: str
    token_count: int


class ChunkResponse(BaseModel):
    """Response with chunks"""
    chunks: List[Chunk]
    total_chunks: int
    processing_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "chunks": [
                    {"index": 0, "content": "Căn hộ 2 phòng ngủ ở Quận 1", "token_count": 15},
                    {"index": 1, "content": "diện tích 75m2, giá 8 tỷ", "token_count": 12}
                ],
                "total_chunks": 2,
                "processing_time_ms": 350
            }
        }


# Core Gateway client
class CoreGatewayClient:
    """Client for calling Core Gateway"""

    def __init__(self):
        # Get URL based on feature flag
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
    logger.info("🚀 Semantic Chunking Service starting up...")
    logger.info(f"Core Gateway Mode: {'REAL' if feature_flags.use_real_core_gateway() else 'MOCK'}")
    yield
    logger.info("👋 Semantic Chunking Service shutting down...")


app = FastAPI(
    title="REE AI - Semantic Chunking Service",
    description="Layer 3 Service: Semantic text chunking using LLM",
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
        "service": "semantic-chunking",
        "status": "healthy",
        "version": "1.0.0",
        "core_gateway_mode": "real" if feature_flags.use_real_core_gateway() else "mock"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "core_gateway": {
            "mode": "real" if feature_flags.use_real_core_gateway() else "mock",
            "url": core_gateway.base_url
        }
    }


@app.post("/chunk", response_model=ChunkResponse)
async def chunk_text(request: ChunkRequest):
    """
    Semantic chunking: Break text into meaningful chunks using LLM

    Example use case:
    - Input: Long property description
    - Output: Semantic chunks (location, price, features, etc.)
    """
    start_time = time.time()

    try:
        logger.info(f"📝 Chunk Request: {len(request.text)} chars, max_chunk_size={request.max_chunk_size}")

        # Step 1: Use LLM to identify semantic boundaries
        llm_request = LLMRequest(
            model=ModelType.OLLAMA_LLAMA2,  # Use Ollama for simple task (cheaper)
            messages=[
                Message(
                    role="system",
                    content="You are a text chunking expert. Break text into semantic chunks based on topics."
                ),
                Message(
                    role="user",
                    content=f"""
Please chunk this text into meaningful segments. Each chunk should be about {request.max_chunk_size} characters.
Separate chunks with "---CHUNK---".

Text:
{request.text}

Output format:
Chunk 1 content
---CHUNK---
Chunk 2 content
---CHUNK---
Chunk 3 content
"""
                )
            ],
            max_tokens=1000,
            temperature=0.3  # Low temperature for consistent chunking
        )

        # Step 2: Call Core Gateway
        llm_response = await core_gateway.call_llm(llm_request)

        # Step 3: Parse chunks
        raw_chunks = llm_response.content.split("---CHUNK---")
        chunks = []

        for idx, chunk_text in enumerate(raw_chunks):
            chunk_text = chunk_text.strip()
            if chunk_text:
                chunks.append(Chunk(
                    index=idx,
                    content=chunk_text,
                    token_count=len(chunk_text.split())  # Rough token count
                ))

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Chunking Complete: {len(chunks)} chunks, {elapsed_ms}ms")

        return ChunkResponse(
            chunks=chunks,
            total_chunks=len(chunks),
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
        logger.error(f"❌ Chunking Error: {str(e)} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=500,
            detail=f"Chunking failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
