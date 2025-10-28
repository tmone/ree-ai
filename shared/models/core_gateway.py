"""
Core Gateway models for LLM communication
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum


class ModelType(str, Enum):
    """Supported LLM models"""
    OLLAMA_LLAMA2 = "ollama/llama2"
    OLLAMA_LLAMA3 = "ollama/llama3"
    GPT4_MINI = "gpt-4o-mini"
    GPT4 = "gpt-4o"


class Message(BaseModel):
    """Chat message format"""
    role: Literal["user", "assistant", "system"]
    content: str

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Tìm nhà ở Quận 1"
            }
        }


class LLMRequest(BaseModel):
    """Request to Core Gateway for LLM completion"""
    model: ModelType = Field(
        default=ModelType.GPT4_MINI,
        description="LLM model to use"
    )
    messages: List[Message] = Field(
        ...,
        description="Conversation messages",
        min_length=1
    )
    max_tokens: int = Field(
        default=1000,
        ge=1,
        le=4000,
        description="Maximum tokens in response"
    )
    temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
        description="Sampling temperature"
    )
    stream: bool = Field(
        default=False,
        description="Stream response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a real estate assistant"},
                    {"role": "user", "content": "Tìm nhà 2 phòng ngủ ở Quận 1"}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }


class TokenUsage(BaseModel):
    """Token usage statistics"""
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)


class LLMResponse(BaseModel):
    """Response from Core Gateway"""
    content: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used")
    usage: TokenUsage = Field(..., description="Token usage")
    finish_reason: Optional[str] = Field(
        default="stop",
        description="Why generation stopped"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Tôi tìm thấy 5 căn nhà 2 phòng ngủ ở Quận 1...",
                "model": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150
                },
                "finish_reason": "stop"
            }
        }
