"""Pydantic models for Core Gateway (LLM) service communication."""
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Supported LLM model types."""
    # Ollama models (local, free)
    OLLAMA_LLAMA2 = "ollama/llama2"
    OLLAMA_MISTRAL = "ollama/mistral"
    OLLAMA_CODELLAMA = "ollama/codellama"
    OLLAMA_QWEN25 = "ollama/qwen2.5:0.5b"  # Lightweight, fast model

    # OpenAI models
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4_MINI = "gpt-4o-mini"
    GPT35_TURBO = "gpt-3.5-turbo"

    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


class Message(BaseModel):
    """Chat message format."""
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="Optional name of the message author")


class LLMRequest(BaseModel):
    """Request format for LLM completions."""
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
