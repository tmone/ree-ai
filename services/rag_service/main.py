"""
RAG Service (Layer 6)
Retrieval-Augmented Generation using LangChain
Flow: Retrieval → Context → Augmentation → Generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import httpx
import time

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from shared.models.core_gateway import LLMRequest, LLMResponse, Message, ModelType
from shared.models.db_gateway import Property, SearchRequest
from shared.config import feature_flags
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


# Service-specific models
class RAGRequest(BaseModel):
    """Request for RAG pipeline"""
    query: str = Field(..., description="User query", min_length=1)
    user_id: str = Field(..., description="User ID")
    conversation_id: str = Field(..., description="Conversation ID")
    use_history: bool = Field(default=True, description="Use conversation history")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Tìm nhà 2 phòng ngủ ở Quận 1giá khoảng 8 tỷ",
                "user_id": "user_123",
                "conversation_id": "conv_456",
                "use_history": True
            }
        }


class RAGResponse(BaseModel):
    """Response from RAG pipeline"""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Source properties")
    metadata: Dict[str, Any] = Field(..., description="Pipeline metadata")
    processing_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Tôi tìm thấy 3 căn nhà 2 phòng ngủ ở Quận 1 trong tầm giá 8 tỷ...",
                "sources": [{"id": "prop_001", "title": "Căn hộ 2PN Quận 1"}],
                "metadata": {"retrieval_count": 5, "model_used": "gpt-4o-mini"},
                "processing_time_ms": 850
            }
        }


# Clients
class CoreGatewayClient:
    """Client for Core Gateway"""

    def __init__(self):
        if feature_flags.use_real_core_gateway():
            self.base_url = "http://core-gateway:8080"
        else:
            self.base_url = "http://mock-core-gateway:1080"

    async def call_llm(self, request: LLMRequest) -> LLMResponse:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=request.dict()
            )
            response.raise_for_status()
            return LLMResponse(**response.json())


class DBGatewayClient:
    """Client for DB Gateway"""

    def __init__(self):
        if feature_flags.use_real_db_gateway():
            self.base_url = "http://db-gateway:8080"
        else:
            self.base_url = "http://mock-db-gateway:1080"

    async def search(self, request: SearchRequest) -> List[Property]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json=request.dict()
            )
            response.raise_for_status()
            data = response.json()
            return [Property(**prop) for prop in data.get("results", [])]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 RAG Service starting up...")
    logger.info(f"Core Gateway Mode: {'REAL' if feature_flags.use_real_core_gateway() else 'MOCK'}")
    logger.info(f"DB Gateway Mode: {'REAL' if feature_flags.use_real_db_gateway() else 'MOCK'}")
    logger.info("📚 LangChain RAG pipeline initialized")
    yield
    logger.info("👋 RAG Service shutting down...")


app = FastAPI(
    title="REE AI - RAG Service",
    description="Layer 6: Retrieval-Augmented Generation using LangChain",
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

# Initialize clients
core_gateway = CoreGatewayClient()
db_gateway = DBGatewayClient()


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "rag-service",
        "status": "healthy",
        "version": "1.0.0",
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
        "db_gateway": {
            "mode": "real" if feature_flags.use_real_db_gateway() else "mock",
            "url": db_gateway.base_url
        },
        "langchain": "initialized"
    }


@app.post("/rag", response_model=RAGResponse)
async def rag_pipeline(request: RAGRequest):
    """
    RAG Pipeline: Retrieval → Context → Augmentation → Generation

    Steps:
    1. Retrieval: Search relevant properties from DB
    2. Context: Load conversation history (TODO)
    3. Augmentation: Combine retrieved docs + context + query
    4. Generation: Generate answer using LLM
    """
    start_time = time.time()

    try:
        logger.info(f"📚 RAG Request: user={request.user_id}, query='{request.query}'")

        # Step 1: Retrieval - Search properties
        retrieval_start = time.time()
        properties = await db_gateway.search(
            SearchRequest(
                query=request.query,
                limit=5
            )
        )
        retrieval_ms = int((time.time() - retrieval_start) * 1000)
        logger.info(f"🔍 Retrieved {len(properties)} properties ({retrieval_ms}ms)")

        # Step 2: Context - Load conversation history
        # TODO: Implement context memory retrieval
        context_history = []
        if request.use_history:
            # Placeholder for conversation history
            context_history = [
                "Previous conversation context will be loaded here"
            ]

        # Step 3: Augmentation - Combine everything
        augmentation_start = time.time()

        # Build context from retrieved properties
        property_context = "Thông tin bất động sản tìm được:\n\n"
        for i, prop in enumerate(properties, 1):
            property_context += f"{i}. {prop.title}\n"
            property_context += f"   - Giá: {prop.price:,.0f} VNĐ\n"
            property_context += f"   - Vị trí: {prop.location}\n"
            property_context += f"   - Diện tích: {prop.area}m²\n"
            property_context += f"   - Phòng ngủ: {prop.bedrooms}\n"
            property_context += f"   - Mô tả: {prop.description[:100]}...\n\n"

        augmentation_ms = int((time.time() - augmentation_start) * 1000)
        logger.info(f"🔗 Augmentation complete ({augmentation_ms}ms)")

        # Step 4: Generation - Generate answer
        generation_start = time.time()

        llm_request = LLMRequest(
            model=ModelType.GPT4_MINI,  # Use OpenAI for better quality
            messages=[
                Message(
                    role="system",
                    content="""Bạn là trợ lý bất động sản chuyên nghiệp.
Nhiệm vụ: Trả lời câu hỏi của khách hàng dựa trên thông tin bất động sản được cung cấp.
Phong cách: Thân thiện, chuyên nghiệp, cung cấp thông tin chi tiết."""
                ),
                Message(
                    role="user",
                    content=f"""
Câu hỏi của khách hàng: {request.query}

{property_context}

Hãy trả lời câu hỏi dựa trên thông tin trên. Nếu có nhiều lựa chọn, hãy so sánh và đưa ra gợi ý phù hợp.
"""
                )
            ],
            max_tokens=1000,
            temperature=0.7
        )

        llm_response = await core_gateway.call_llm(llm_request)
        generation_ms = int((time.time() - generation_start) * 1000)
        logger.info(f"💬 Generation complete ({generation_ms}ms)")

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ RAG Pipeline complete: {elapsed_ms}ms (retrieval={retrieval_ms}ms, augmentation={augmentation_ms}ms, generation={generation_ms}ms)")

        return RAGResponse(
            answer=llm_response.content,
            sources=[prop.dict() for prop in properties],
            metadata={
                "retrieval_count": len(properties),
                "retrieval_ms": retrieval_ms,
                "augmentation_ms": augmentation_ms,
                "generation_ms": generation_ms,
                "model_used": llm_response.model,
                "tokens_used": llm_response.usage.total_tokens
            },
            processing_time_ms=elapsed_ms
        )

    except httpx.HTTPStatusError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Gateway Error: {e.response.status_code} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=502,
            detail=f"Gateway error: {e.response.status_code}"
        )
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ RAG Error: {str(e)} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=500,
            detail=f"RAG pipeline failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
