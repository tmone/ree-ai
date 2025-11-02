"""Pydantic models for Core Gateway (LLM) service communication."""
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Supported LLM model types."""
    # Ollama models (local, free)
    OLLAMA_LLAMA2 = "ollama/llama2"
    OLLAMA_MISTRAL = "ollama/mistral"
    OLLAMA_CODELLAMA = "ollama/codellama"
    OLLAMA_QWEN25 = "ollama/qwen2.5:0.5b"  # Lightweight, fast model

    # OpenAI models (text-only)
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4_MINI = "gpt-4o-mini"
    GPT35_TURBO = "gpt-3.5-turbo"

    # OpenAI Vision models (multimodal)
    GPT4_VISION = "gpt-4-vision-preview"
    GPT4_TURBO_VISION = "gpt-4-turbo"  # Supports vision
    GPT4O = "gpt-4o"  # GPT-4O native multimodal
    GPT4O_MINI_VISION = "gpt-4o-mini"  # Supports vision

    # Ollama Vision models (multimodal, local)
    OLLAMA_QWEN_VL = "ollama/qwen2-vl:7b"  # Qwen2-VL (Vietnamese + Vision)
    OLLAMA_LLAVA = "ollama/llava"  # LLaVA vision model
    OLLAMA_MOONDREAM = "ollama/moondream"  # Lightweight vision model
    OLLAMA_LLAMA32_VISION = "ollama/llama3.2-vision"  # Llama 3.2 with vision

    # Anthropic models (support vision)
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


class FileAttachment(BaseModel):
    """File attachment to a message (image, document, etc.)."""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type (e.g., 'image/jpeg', 'application/pdf')")
    size_bytes: int = Field(..., description="File size in bytes")
    base64_data: Optional[str] = Field(None, description="Base64-encoded file data")
    url: Optional[str] = Field(None, description="URL to file (if stored externally)")
    upload_time: Optional[datetime] = Field(None, description="Time of upload")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Message(BaseModel):
    """Chat message format (supports multimodal content)."""
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: Union[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Message content: string for text-only, or array of content blocks for multimodal"
    )
    name: Optional[str] = Field(None, description="Optional name of the message author")
    files: Optional[List[FileAttachment]] = Field(
        None,
        description="Attached files (images, documents) for multimodal messages"
    )

    def has_files(self) -> bool:
        """Check if message contains file attachments."""
        return self.files is not None and len(self.files) > 0

    def is_multimodal(self) -> bool:
        """Check if message is multimodal (has files or content array)."""
        return self.has_files() or isinstance(self.content, list)


class LLMRequest(BaseModel):
    """Request format for LLM completions (supports multimodal)."""
    model: ModelType = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature (0.0 to 2.0)")
    top_p: Optional[float] = Field(1.0, description="Nucleus sampling parameter")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(0.0, description="Presence penalty (-2.0 to 2.0)")
    frequency_penalty: Optional[float] = Field(0.0, description="Frequency penalty (-2.0 to 2.0)")
    user: Optional[str] = Field(None, description="User identifier for tracking")

    def has_files(self) -> bool:
        """Check if any message contains file attachments."""
        return any(msg.has_files() for msg in self.messages)

    def is_multimodal(self) -> bool:
        """Check if request contains multimodal content."""
        return any(msg.is_multimodal() for msg in self.messages)

    def get_vision_model_fallback(self) -> Optional[str]:
        """Get appropriate vision model fallback based on current model."""
        vision_fallbacks = {
            # OpenAI → Ollama fallback
            ModelType.GPT4_VISION.value: ModelType.OLLAMA_QWEN_VL.value,
            ModelType.GPT4_TURBO_VISION.value: ModelType.OLLAMA_QWEN_VL.value,
            ModelType.GPT4O.value: ModelType.OLLAMA_LLAVA.value,
            ModelType.GPT4O_MINI_VISION.value: ModelType.OLLAMA_LLAMA32_VISION.value,
            # Ollama → OpenAI fallback
            ModelType.OLLAMA_QWEN_VL.value: ModelType.GPT4O.value,
            ModelType.OLLAMA_LLAVA.value: ModelType.GPT4_VISION.value,
            ModelType.OLLAMA_LLAMA32_VISION.value: ModelType.GPT4O_MINI_VISION.value,
        }
        return vision_fallbacks.get(self.model.value)


class Usage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    """Response format from LLM completions."""
    id: str = Field(..., description="Unique response ID")
    model: str = Field(..., description="Model used for completion")
    content: str = Field(..., description="Generated content")
    role: str = Field("assistant", description="Role of the responder")
    finish_reason: Optional[str] = Field(None, description="Reason for completion finish")
    usage: Optional[Usage] = Field(None, description="Token usage statistics")


class EmbeddingRequest(BaseModel):
    """Request format for text embeddings."""
    model: str = Field("text-embedding-ada-002", description="Embedding model to use")
    input: Union[str, List[str]] = Field(..., description="Text or list of texts to embed")
    user: Optional[str] = Field(None, description="User identifier for tracking")


class EmbeddingResponse(BaseModel):
    """Response format for text embeddings."""
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    model: str = Field(..., description="Model used for embeddings")
    usage: Optional[Usage] = Field(None, description="Token usage statistics")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    models_available: Optional[List[str]] = Field(None, description="Available models")
