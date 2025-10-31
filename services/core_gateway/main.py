"""Core Gateway - LLM routing service using LiteLLM."""
import time
from typing import Optional
from fastapi import HTTPException
import httpx
from httpx import HTTPStatusError

from core.base_service import BaseService
from shared.models.core_gateway import (
    LLMRequest, LLMResponse, EmbeddingRequest, EmbeddingResponse,
    Message, Usage, ModelType
)
from shared.utils.logger import LogEmoji
from shared.config import settings


class CoreGateway(BaseService):
    """
    Core Gateway Service - Layer 5
    Routes LLM requests to OpenAI or Ollama using LiteLLM.
    """

    def __init__(self):
        super().__init__(
            name="core_gateway",
            version="1.0.0",
            capabilities=["llm", "chat", "embeddings"],
            port=8080
        )

        # HTTP client for Ollama
        self.http_client = httpx.AsyncClient(timeout=120.0)

    def setup_routes(self):
        """Setup Core Gateway API routes."""

        @self.app.post("/chat/completions", response_model=LLMResponse)
        async def chat_completions(request: LLMRequest):
            """
            OpenAI-compatible chat completions endpoint with failover.
            Routes: OpenAI → Ollama (on rate limit/error)
            """
            try:
                start_time = time.time()

                # Route based on model type
                if request.model.value.startswith("ollama/"):
                    response = await self._call_ollama(request)
                else:
                    # Try OpenAI first
                    try:
                        response = await self._call_openai(request)
                        self.logger.info(f"{LogEmoji.SUCCESS} Using OpenAI")
                    except (HTTPStatusError, Exception) as openai_error:
                        error_str = str(openai_error)

                        # Check status code for HTTP errors
                        is_rate_limit = False
                        if isinstance(openai_error, HTTPStatusError):
                            is_rate_limit = openai_error.response.status_code == 429
                        else:
                            # Check string for rate limit indicators
                            is_rate_limit = ("429" in error_str or
                                           "rate_limit" in error_str.lower() or
                                           "quota" in error_str.lower())

                        if is_rate_limit:
                            self.logger.warning(
                                f"{LogEmoji.WARNING} OpenAI rate limit/quota exceeded, "
                                f"failing over to Ollama"
                            )

                            # Failover to Ollama
                            response = await self._call_ollama(request)
                            self.logger.info(f"{LogEmoji.SUCCESS} Using Ollama (failover)")
                        else:
                            # Not a rate limit error, re-raise
                            raise

                execution_time = (time.time() - start_time) * 1000

                self.logger.info(
                    f"{LogEmoji.SUCCESS} LLM request completed: "
                    f"model={request.model.value}, time={execution_time:.2f}ms"
                )

                return response

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} All LLM providers failed: {e}")
                raise HTTPException(status_code=500, detail=f"All LLM providers failed: {str(e)}")

        @self.app.post("/embeddings", response_model=EmbeddingResponse)
        async def create_embeddings(request: EmbeddingRequest):
            """Create text embeddings."""
            try:
                # For now, use OpenAI embeddings
                # In production, could route to Ollama for local embeddings
                if not settings.OPENAI_API_KEY:
                    raise HTTPException(
                        status_code=500,
                        detail="OpenAI API key not configured"
                    )

                # Call OpenAI embeddings API
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }

                texts = [request.input] if isinstance(request.input, str) else request.input

                payload = {
                    "model": request.model,
                    "input": texts
                }

                response = await self.http_client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Extract embeddings
                embeddings = [item["embedding"] for item in data["data"]]

                return EmbeddingResponse(
                    embeddings=embeddings,
                    model=request.model,
                    usage=Usage(**data["usage"]) if "usage" in data else None
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Embedding request failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def _call_openai(self, request: LLMRequest) -> LLMResponse:
        """Call OpenAI API."""
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": request.model.value,
            "messages": [msg.dict() for msg in request.messages],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        }

        if request.stop:
            payload["stop"] = request.stop
        if request.presence_penalty:
            payload["presence_penalty"] = request.presence_penalty
        if request.frequency_penalty:
            payload["frequency_penalty"] = request.frequency_penalty

        response = await self.http_client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        # Extract response
        choice = data["choices"][0]
        message = choice["message"]

        return LLMResponse(
            id=data["id"],
            model=data["model"],
            content=message["content"],
            role=message["role"],
            finish_reason=choice.get("finish_reason"),
            usage=Usage(**data["usage"]) if "usage" in data else None
        )

    async def _call_ollama(self, request: LLMRequest) -> LLMResponse:
        """Call Ollama API."""
        # Extract model name (remove "ollama/" prefix)
        # If failover from OpenAI, use default fast model
        if request.model.value.startswith("ollama/"):
            model_name = request.model.value.replace("ollama/", "")
        else:
            # Failover case - use a default small fast model
            model_name = "qwen2.5:0.5b"

        payload = {
            "model": model_name,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ],
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
            }
        }

        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        response = await self.http_client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        # Extract response
        message = data.get("message", {})
        content = message.get("content", "")

        # Calculate token usage (Ollama provides eval_count and prompt_eval_count)
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return LLMResponse(
            id=f"ollama-{int(time.time())}",
            model=model_name,
            content=content,
            role="assistant",
            finish_reason="stop",
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
        )

    async def on_shutdown(self):
        """Cleanup on shutdown."""
        await self.http_client.aclose()
        await super().on_shutdown()


if __name__ == "__main__":
    service = CoreGateway()
    service.run()
