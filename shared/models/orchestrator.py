"""Pydantic models for Orchestrator service communication."""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from shared.models.core_gateway import FileAttachment
from shared.models.reasoning import ReasoningChain, AmbiguityDetectionResult, KnowledgeExpansion


class IntentType(str, Enum):
    """Detected user intent types - Aligned with Vietnamese real estate domain."""
    # Core intents (5 main use cases)
    POST = "post"  # Đăng tin bán/cho thuê bất động sản (Case 1)
    SEARCH = "search"  # Tìm kiếm bất động sản (Case 2)
    PRICE_CONSULTATION = "price_consultation"  # Tư vấn giá thị trường (Case 3)
    PROPERTY_DETAIL = "property_detail"  # Xem chi tiết bất động sản (Case 4 - NEW)
    CHAT = "chat"  # Trò chuyện chung / chào hỏi (Case 5)

    # Extended intents (future use)
    COMPARE = "compare"  # So sánh bất động sản
    PRICE_ANALYSIS = "price_analysis"  # Phân tích giá & định giá (legacy, use PRICE_CONSULTATION)
    INVESTMENT_ADVICE = "investment_advice"  # Tư vấn đầu tư bất động sản
    LOCATION_INSIGHTS = "location_insights"  # Phân tích khu vực & tiện ích
    LEGAL_GUIDANCE = "legal_guidance"  # Tư vấn pháp lý & thủ tục
    UNKNOWN = "unknown"  # Không xác định được intent


class OrchestrationRequest(BaseModel):
    """Request format for orchestration (supports multimodal)."""
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="User query text")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    files: Optional[List[FileAttachment]] = Field(None, description="Attached files (images, documents)")
    language: Optional[str] = Field("vi", description="User's preferred language (vi, en, th, ja). Auto-detected if not specified.")

    def has_files(self) -> bool:
        """Check if request contains file attachments."""
        return self.files is not None and len(self.files) > 0


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
    """Response from orchestration with transparent reasoning (Codex-inspired)."""
    intent: IntentType
    confidence: float
    response: str = Field(..., description="Final response to user")
    service_used: Optional[str] = Field(None, description="Backend service that handled request")
    execution_time_ms: float
    metadata: Optional[Dict[str, Any]] = None

    # NEW: Reasoning transparency (Phase 1)
    reasoning_chain: Optional[ReasoningChain] = Field(
        None,
        description="Complete ReAct reasoning chain showing thinking process"
    )

    # NEW: Ambiguity detection (Phase 1)
    needs_clarification: bool = Field(
        False,
        description="Whether query has ambiguities requiring user clarification"
    )
    ambiguity_result: Optional[AmbiguityDetectionResult] = Field(
        None,
        description="Details about ambiguities found"
    )

    # NEW: Knowledge expansion (Phase 2)
    knowledge_expansion: Optional[KnowledgeExpansion] = Field(
        None,
        description="How domain knowledge expanded the query"
    )


class RoutingDecision(BaseModel):
    """Internal routing decision."""
    intent: IntentType
    target_service: str
    endpoint: str
    should_use_rag: bool = False
    extracted_params: Optional[Dict[str, Any]] = None
