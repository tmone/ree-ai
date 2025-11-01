"""Pydantic models for Orchestrator service communication."""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Detected user intent types - Aligned with Vietnamese real estate domain."""
    SEARCH = "search"  # Tìm kiếm bất động sản
    COMPARE = "compare"  # So sánh bất động sản
    PRICE_ANALYSIS = "price_analysis"  # Phân tích giá & định giá
    INVESTMENT_ADVICE = "investment_advice"  # Tư vấn đầu tư bất động sản
    LOCATION_INSIGHTS = "location_insights"  # Phân tích khu vực & tiện ích
    LEGAL_GUIDANCE = "legal_guidance"  # Tư vấn pháp lý & thủ tục
    CHAT = "chat"  # Trò chuyện chung / chào hỏi
    UNKNOWN = "unknown"  # Không xác định được intent


class OrchestrationRequest(BaseModel):
    """Request format for orchestration."""
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="User query text")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class IntentDetectionResult(BaseModel):
    """Result of intent detection."""
    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    extracted_entities: Optional[Dict[str, Any]] = Field(None, description="Extracted entities from query")


class ServiceRoute(BaseModel):
    """Service routing information."""
    service_name: str
    service_url: str
    endpoint: str
    method: str = "POST"


class OrchestrationResponse(BaseModel):
    """Response from orchestration."""
    intent: IntentType
    confidence: float
    response: str = Field(..., description="Final response to user")
    service_used: Optional[str] = Field(None, description="Backend service that handled request")
    execution_time_ms: float
    metadata: Optional[Dict[str, Any]] = None


class RoutingDecision(BaseModel):
    """Internal routing decision."""
    intent: IntentType
    target_service: str
    endpoint: str
    should_use_rag: bool = False
    extracted_params: Optional[Dict[str, Any]] = None
