"""
Orchestrator models for routing requests
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class ServiceType(str, Enum):
    """Available AI services"""
    SEMANTIC_CHUNKING = "semantic_chunking"
    CLASSIFICATION = "classification"
    ATTRIBUTE_EXTRACTION = "attribute_extraction"
    COMPLETENESS = "completeness"
    PRICE_SUGGESTION = "price_suggestion"
    RERANK = "rerank"
    RAG = "rag"
    SEARCH = "search"


class OrchestrationRequest(BaseModel):
    """Request to orchestrator"""
    user_id: str = Field(..., description="User ID")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    query: str = Field(..., description="User query", min_length=1)
    service_type: Optional[ServiceType] = Field(
        None,
        description="Specific service to use (auto-detect if None)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "conversation_id": "conv_456",
                "query": "Tìm nhà 2 phòng ngủ ở Quận 1",
                "service_type": "search",
                "context": {}
            }
        }


class OrchestrationResponse(BaseModel):
    """Response from orchestrator"""
    response: str = Field(..., description="Generated response")
    service_used: ServiceType = Field(..., description="Service that handled request")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    took_ms: int = Field(..., ge=0, description="Processing time in ms")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Tôi tìm thấy 5 căn nhà 2 phòng ngủ ở Quận 1...",
                "service_used": "rag",
                "metadata": {
                    "properties_found": 5,
                    "model_used": "gpt-4o-mini"
                },
                "took_ms": 850
            }
        }
