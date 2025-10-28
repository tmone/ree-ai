"""
Semantic Chunking Service - REFACTORED
Using BaseService for proper microservice architecture

This is the CORRECT way to build a service:
1. Inherit from BaseService
2. Automatic service registration
3. Standard health checks
4. Graceful shutdown
"""
import sys
sys.path.insert(0, '/app')

from pydantic import BaseModel, Field
from typing import List
import httpx
import time

from core import BaseService
from shared.models.core_gateway import LLMRequest, LLMResponse, Message, ModelType
from shared.config import feature_flags


# Service-specific models
class ChunkRequest(BaseModel):
    """Request for semantic chunking"""
    text: str = Field(..., description="Text to chunk", min_length=1)
    max_chunk_size: int = Field(default=500, ge=100, le=2000)


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


class SemanticChunkingService(BaseService):
    """
    Semantic Chunking Service

    Capabilities:
    - text_processing: Can process text
    - chunking: Can split text into semantic chunks
    """

    def __init__(self):
        super().__init__(
            name="semantic_chunking",
            version="1.0.0",
            capabilities=["text_processing", "chunking"],
            port=8080
        )

        # Setup Core Gateway client
        if feature_flags.use_real_core_gateway():
            self.core_gateway_url = "http://core-gateway:8080"
        else:
            self.core_gateway_url = "http://mock-core-gateway:1080"

        self.logger.info(f"Core Gateway: {self.core_gateway_url}")

    def setup_routes(self):
        """Setup service-specific routes"""

        @self.app.post("/chunk", response_model=ChunkResponse)
        async def chunk_text(request: ChunkRequest):
            """
            Semantic chunking endpoint

            This is where the actual service logic happens
            """
            start_time = time.time()

            try:
                self.logger.info(f"📝 Chunk Request: {len(request.text)} chars")

                # Call Core Gateway for LLM
                llm_request = LLMRequest(
                    model=ModelType.OLLAMA_LLAMA2,
                    messages=[
                        Message(
                            role="system",
                            content="You are a text chunking expert."
                        ),
                        Message(
                            role="user",
                            content=f"""
Split this text into semantic chunks. Separate chunks with "---CHUNK---".

Text:
{request.text}

Output format:
Chunk 1 content
---CHUNK---
Chunk 2 content
"""
                        )
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )

                # Call Core Gateway
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.core_gateway_url}/v1/chat/completions",
                        json=llm_request.dict()
                    )
                    response.raise_for_status()
                    llm_response = LLMResponse(**response.json())

                # Parse chunks
                raw_chunks = llm_response.content.split("---CHUNK---")
                chunks = []

                for idx, chunk_text in enumerate(raw_chunks):
                    chunk_text = chunk_text.strip()
                    if chunk_text:
                        chunks.append(Chunk(
                            index=idx,
                            content=chunk_text,
                            token_count=len(chunk_text.split())
                        ))

                elapsed_ms = int((time.time() - start_time) * 1000)
                self.logger.info(f"✅ Chunking Complete: {len(chunks)} chunks, {elapsed_ms}ms")

                return ChunkResponse(
                    chunks=chunks,
                    total_chunks=len(chunks),
                    processing_time_ms=elapsed_ms
                )

            except Exception as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.logger.error(f"❌ Error: {str(e)} ({elapsed_ms}ms)")
                raise


if __name__ == "__main__":
    service = SemanticChunkingService()
    service.run()
