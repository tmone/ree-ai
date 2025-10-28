"""
Orchestrator Service (Layer 2)
Routes requests to appropriate AI services using LangChain
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import time
from typing import Optional

from langchain.chains.router import MultiPromptChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

from shared.models.orchestrator import (
    OrchestrationRequest,
    OrchestrationResponse,
    ServiceType
)
from shared.config import settings, feature_flags
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Orchestrator Service starting up...")
    logger.info(f"Core Gateway Mode: {'REAL' if feature_flags.use_real_core_gateway() else 'MOCK'}")
    logger.info(f"DB Gateway Mode: {'REAL' if feature_flags.use_real_db_gateway() else 'MOCK'}")
    yield
    logger.info("👋 Orchestrator shutting down...")


app = FastAPI(
    title="REE AI - Orchestrator",
    description="Layer 2: Routes requests to appropriate AI services using LangChain",
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


# Service URLs based on feature flags
def get_service_url(service_name: str) -> str:
    """Get service URL based on feature flags"""
    base_urls = {
        ServiceType.SEMANTIC_CHUNKING: "http://semantic-chunking:8080",
        ServiceType.CLASSIFICATION: "http://classification:8080",
        ServiceType.ATTRIBUTE_EXTRACTION: "http://attribute-extraction:8080",
        ServiceType.COMPLETENESS: "http://completeness:8080",
        ServiceType.PRICE_SUGGESTION: "http://price-suggestion:8080",
        ServiceType.RERANK: "http://rerank:8080",
        ServiceType.RAG: "http://rag-service:8080",
        ServiceType.SEARCH: "http://db-gateway:8080"
    }
    return base_urls.get(service_name, "http://localhost:8080")


def detect_intent(query: str) -> ServiceType:
    """
    Detect user intent from query
    Simple keyword-based routing for MVP
    """
    query_lower = query.lower()

    # Search patterns
    if any(kw in query_lower for kw in ["tìm", "search", "có", "list", "xem"]):
        return ServiceType.SEARCH

    # Price patterns
    if any(kw in query_lower for kw in ["giá", "price", "bao nhiêu", "cost"]):
        return ServiceType.PRICE_SUGGESTION

    # Classification patterns
    if any(kw in query_lower for kw in ["loại", "classify", "phân loại", "type"]):
        return ServiceType.CLASSIFICATION

    # Default: Use RAG for complex queries
    return ServiceType.RAG


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "orchestrator",
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
            "mode": "real" if feature_flags.use_real_core_gateway() else "mock"
        },
        "db_gateway": {
            "mode": "real" if feature_flags.use_real_db_gateway() else "mock"
        },
        "langchain": "initialized"
    }


@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: OrchestrationRequest):
    """
    Orchestrate request to appropriate service
    Uses LangChain for intelligent routing
    """
    start_time = time.time()

    try:
        logger.info(f"🎯 Orchestration Request: user={request.user_id}, query='{request.query}'")

        # Detect intent if not specified
        if request.service_type is None:
            service_type = detect_intent(request.query)
            logger.info(f"🤖 Detected intent: {service_type}")
        else:
            service_type = request.service_type
            logger.info(f"📌 Explicit service: {service_type}")

        # Route to appropriate service
        service_url = get_service_url(service_type)

        # For MVP: Direct routing
        if service_type == ServiceType.SEARCH:
            # Call DB Gateway directly
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{service_url}/search",
                    json={
                        "query": request.query,
                        "filters": {},
                        "limit": 10
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Format response
                properties = data.get("results", [])
                response_text = f"Tìm thấy {len(properties)} bất động sản:\n\n"
                for i, prop in enumerate(properties[:5], 1):
                    response_text += f"{i}. {prop['title']} - {prop['price']:,.0f} VNĐ\n"

                elapsed_ms = int((time.time() - start_time) * 1000)
                logger.info(f"✅ Search completed: {elapsed_ms}ms")

                return OrchestrationResponse(
                    response=response_text,
                    service_used=service_type,
                    metadata={"properties_count": len(properties)},
                    took_ms=elapsed_ms
                )

        elif service_type == ServiceType.RAG:
            # Call RAG service
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{service_url}/rag",
                    json={
                        "query": request.query,
                        "user_id": request.user_id,
                        "conversation_id": request.conversation_id or "default"
                    }
                )
                response.raise_for_status()
                data = response.json()

                elapsed_ms = int((time.time() - start_time) * 1000)
                logger.info(f"✅ RAG completed: {elapsed_ms}ms")

                return OrchestrationResponse(
                    response=data.get("answer", ""),
                    service_used=service_type,
                    metadata=data.get("metadata", {}),
                    took_ms=elapsed_ms
                )

        else:
            # For other services: Return placeholder
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"⚠️ Service not yet implemented: {service_type}")

            return OrchestrationResponse(
                response=f"Service {service_type} chưa được triển khai. Đây là response placeholder.",
                service_used=service_type,
                metadata={"status": "not_implemented"},
                took_ms=elapsed_ms
            )

    except httpx.HTTPStatusError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Service Error: {e.response.status_code} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=502,
            detail=f"Service error: {e.response.status_code}"
        )
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ Orchestration Error: {str(e)} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
