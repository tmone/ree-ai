"""Core Gateway - LLM routing service using LiteLLM."""
import time
import base64
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
import httpx
from httpx import HTTPStatusError

from core.base_service import BaseService
from shared.models.core_gateway import (
    LLMRequest, LLMResponse, EmbeddingRequest, EmbeddingResponse,
    Message, Usage, ModelType, FileAttachment
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
            capabilities=["llm", "chat", "embeddings", "vision"],
            port=8080
        )

        # HTTP client for Ollama
        self.http_client = httpx.AsyncClient(timeout=120.0)

        # Vision-capable models
        self.vision_models = {
            ModelType.GPT4_VISION.value,
            ModelType.GPT4_TURBO_VISION.value,
            ModelType.GPT4O.value,
            ModelType.GPT4O_MINI_VISION.value,
            ModelType.OLLAMA_QWEN_VL.value,
            ModelType.OLLAMA_LLAVA.value,
            ModelType.OLLAMA_MOONDREAM.value,
            ModelType.OLLAMA_LLAMA32_VISION.value,
            ModelType.CLAUDE_3_OPUS.value,
            ModelType.CLAUDE_3_SONNET.value,
            ModelType.CLAUDE_3_HAIKU.value,
        }

    def _is_vision_model(self, model: str) -> bool:
        """Check if model supports vision/multimodal capabilities."""
        return model in self.vision_models

    def _encode_image_to_base64(self, file_attachment: FileAttachment) -> str:
        """
        Encode image to base64 data URI for OpenAI Vision API.

        Returns:
            Data URI: "data:image/jpeg;base64,<base64_data>"
        """
        if file_attachment.base64_data:
            # Already has base64 data
            return f"data:{file_attachment.mime_type};base64,{file_attachment.base64_data}"
        else:
            # Should not happen if files are properly uploaded
            raise ValueError(f"File {file_attachment.filename} missing base64_data")

    def _build_openai_vision_content(self, message: Message) -> List[Dict[str, Any]]:
        """
        Build OpenAI-compatible content array for vision requests.

        Format:
        [
            {"type": "text", "text": "..."},
            {"type": "image_url", "image_url": {"url": "data:...", "detail": "high"}}
        ]
        """
        content_blocks = []

        # Add text content
        text_content = message.content if isinstance(message.content, str) else ""
        if text_content:
            content_blocks.append({
                "type": "text",
                "text": text_content
            })

        # Add image attachments
        if message.files:
            for file in message.files:
                if file.mime_type.startswith("image/"):
                    data_uri = self._encode_image_to_base64(file)
                    content_blocks.append({
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri,
                            "detail": "high"  # Use high detail for property images
                        }
                    })

        return content_blocks

    def setup_routes(self):
        """Setup Core Gateway API routes."""

        @self.app.post("/chat/completions", response_model=LLMResponse)
        async def chat_completions(request: LLMRequest):
            """
            OpenAI-compatible chat completions endpoint with failover.
            Routes: OpenAI → Ollama (on rate limit/error)
            Supports multimodal (vision) requests with automatic model selection.
            """
            try:
                start_time = time.time()
                is_multimodal = request.is_multimodal()

                # Log request type
                if is_multimodal:
                    self.logger.info(
                        f"{LogEmoji.AI} Multimodal request detected with model {request.model.value}"
                    )

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
                            # For vision requests, get appropriate vision fallback
                            if is_multimodal:
                                fallback_model = request.get_vision_model_fallback()
                                if fallback_model:
                                    self.logger.info(
                                        f"{LogEmoji.AI} Using vision fallback model: {fallback_model}"
                                    )
                                    request.model = ModelType(fallback_model)

                            response = await self._call_ollama(request)
                            self.logger.info(f"{LogEmoji.SUCCESS} Using Ollama (failover)")
                        else:
                            # Not a rate limit error, re-raise
                            raise

                execution_time = (time.time() - start_time) * 1000

                self.logger.info(
                    f"{LogEmoji.SUCCESS} LLM request completed: "
                    f"model={request.model.value}, multimodal={is_multimodal}, "
                    f"time={execution_time:.2f}ms"
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
        """
        Call OpenAI API (routes to vision handler if multimodal).
        """
        # Check if request contains multimodal content
        if request.is_multimodal():
            # Verify model supports vision
            if not self._is_vision_model(request.model.value):
                self.logger.warning(
                    f"{LogEmoji.WARNING} Model {request.model.value} doesn't support vision, "
                    f"upgrading to GPT-4O"
                )
                # Auto-upgrade to vision-capable model
                request.model = ModelType.GPT4O

            return await self._call_openai_multimodal(request)
        else:
            return await self._call_openai_text_only(request)

    async def _call_openai_text_only(self, request: LLMRequest) -> LLMResponse:
        """Call OpenAI API for text-only requests."""
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

    async def _call_openai_multimodal(self, request: LLMRequest) -> LLMResponse:
        """
        Call OpenAI Vision API for multimodal requests (images + text).

        OpenAI Vision Format:
        {
            "model": "gpt-4-vision-preview",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": "data:...", "detail": "high"}}
                ]
            }]
        }
        """
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )

        self.logger.info(
            f"{LogEmoji.AI} Calling OpenAI Vision API with model {request.model.value}"
        )

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # Build messages with vision content
        messages = []
        for msg in request.messages:
            if msg.is_multimodal():
                # Build content array for multimodal message
                content = self._build_openai_vision_content(msg)
                messages.append({
                    "role": msg.role,
                    "content": content
                })
            else:
                # Text-only message
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        payload = {
            "model": request.model.value,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,  # Vision needs more tokens
            "temperature": request.temperature,
        }

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

        self.logger.info(
            f"{LogEmoji.SUCCESS} OpenAI Vision response received: {len(message['content'])} chars"
        )

        return LLMResponse(
            id=data["id"],
            model=data["model"],
            content=message["content"],
            role=message["role"],
            finish_reason=choice.get("finish_reason"),
            usage=Usage(**data["usage"]) if "usage" in data else None
        )

    async def _call_ollama(self, request: LLMRequest) -> LLMResponse:
        """
        Call Ollama API (routes to vision handler if multimodal).
        """
        # Check if request contains multimodal content
        if request.is_multimodal():
            return await self._call_ollama_vision(request)
        else:
            return await self._call_ollama_text_only(request)

    async def _call_ollama_text_only(self, request: LLMRequest) -> LLMResponse:
        """Call Ollama API for text-only requests."""
        # Extract model name (remove "ollama/" prefix)
        # If failover from OpenAI, use thinking-capable model for better intent detection
        if request.model.value.startswith("ollama/"):
            model_name = request.model.value.replace("ollama/", "")
        else:
            # Failover case - use deepseek-v3.1:671b-cloud for better performance
            # Cloud model provides better Vietnamese understanding and response quality
            model_name = "deepseek-v3.1:671b-cloud"

        # Thinking mode DISABLED - best results achieved without it (Iteration 3: 71.4%)
        # enable_think = "deepseek" in model_name.lower()

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

        # Thinking mode disabled for intent detection
        # if enable_think:
        #     payload["think"] = True

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

    async def _call_ollama_vision(self, request: LLMRequest) -> LLMResponse:
        """
        Call Ollama Vision API for multimodal requests.

        Ollama Vision Format (different from OpenAI):
        {
            "model": "qwen2-vl:7b",
            "messages": [{
                "role": "user",
                "content": "What's in this image?",
                "images": ["base64_encoded_image"]  # Separate field!
            }],
            "stream": false
        }
        """
        # Extract model name or use default vision model
        if request.model.value.startswith("ollama/"):
            model_name = request.model.value.replace("ollama/", "")
        else:
            # Failover case - use qwen2-vl for Vietnamese + vision support
            model_name = "qwen2-vl:7b"
            self.logger.info(
                f"{LogEmoji.WARNING} Failover: Using Ollama {model_name} for vision"
            )

        # Verify model supports vision
        vision_models_ollama = ["qwen2-vl", "llava", "moondream", "llama3.2-vision"]
        if not any(vm in model_name.lower() for vm in vision_models_ollama):
            # Auto-upgrade to qwen2-vl
            self.logger.warning(
                f"{LogEmoji.WARNING} Model {model_name} doesn't support vision, "
                f"upgrading to qwen2-vl:7b"
            )
            model_name = "qwen2-vl:7b"

        self.logger.info(
            f"{LogEmoji.AI} Calling Ollama Vision API with model {model_name}"
        )

        # Build messages with images
        messages = []
        for msg in request.messages:
            message_dict = {
                "role": msg.role,
                "content": msg.content if isinstance(msg.content, str) else ""
            }

            # Extract images for Ollama format
            if msg.files:
                images = []
                for file in msg.files:
                    if file.mime_type.startswith("image/"):
                        # Ollama needs raw base64 (no data URI prefix)
                        if file.base64_data:
                            images.append(file.base64_data)

                if images:
                    message_dict["images"] = images

            messages.append(message_dict)

        payload = {
            "model": model_name,
            "messages": messages,
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

        self.logger.info(
            f"{LogEmoji.SUCCESS} Ollama Vision response received: {len(content)} chars"
        )

        # Calculate token usage
        prompt_tokens = data.get("prompt_eval_count", 0)
        completion_tokens = data.get("eval_count", 0)

        return LLMResponse(
            id=f"ollama-vision-{int(time.time())}",
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
