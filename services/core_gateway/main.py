"""
Core Gateway Service
Handles all LLM communication with routing to Ollama/OpenAI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from litellm import completion
import os

from shared.models.core_gateway import LLMRequest, LLMResponse, TokenUsage
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Core Gateway starting up...")
    logger.info(f"OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    logger.info(f"Ollama URL: {os.getenv('OLLAMA_BASE_URL', 'Not set')}")
    yield
    logger.info("👋 Core Gateway shutting down...")


app = FastAPI(
    title="REE AI - Core Gateway",
    description="Central gateway for LLM communication",
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


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "core-gateway",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "ollama_url": os.getenv("OLLAMA_BASE_URL", "not_configured")
    }


@app.post("/v1/chat/completions", response_model=LLMResponse)
async def chat_completions(request: LLMRequest):
    """
    Call LLM (Ollama or OpenAI based on model)
    """
    start_time = time.time()

    try:
        logger.info(f"🤖 LLM Request: model={request.model}, messages={len(request.messages)}")

        # Convert Pydantic models to dicts
        messages = [msg.dict() for msg in request.messages]

        # Call LiteLLM (handles routing)
        response = completion(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False
        )

        # Extract response
        content = response.choices[0].message.content
        usage = response.usage

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ LLM Response: {elapsed_ms}ms, tokens={usage.total_tokens}")

        return LLMResponse(
            content=content,
            model=request.model,
            usage=TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            ),
            finish_reason="stop"
        )

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"❌ LLM Error: {str(e)} ({elapsed_ms}ms)")
        raise HTTPException(
            status_code=500,
            detail=f"LLM call failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
