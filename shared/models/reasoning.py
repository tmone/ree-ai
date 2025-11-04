"""
Reasoning and Thinking Models for REE AI Orchestrator
Inspired by Codex's transparent reasoning pattern
"""
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ThinkingStage(str, Enum):
    """Stages in the reasoning process"""
    QUERY_ANALYSIS = "query_analysis"
    CONTEXT_GATHERING = "context_gathering"
    ENTITY_EXTRACTION = "entity_extraction"
    AMBIGUITY_DETECTION = "ambiguity_detection"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    TOOL_SELECTION = "tool_selection"
    EXECUTION = "execution"
    OBSERVATION = "observation"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


class ThinkingItem(BaseModel):
    """Individual reasoning step in the ReAct loop"""
    id: str = Field(default_factory=lambda: f"think_{datetime.now().timestamp()}")
    stage: ThinkingStage
    thought: str = Field(..., description="Human-readable reasoning")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured data for this step")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in this step")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

    class Config:
        json_schema_extra = {
            "example": {
                "id": "think_1234567890",
                "stage": "query_analysis",
                "thought": "Phát hiện 2 điều kiện: (1) hồ bơi, (2) gần trường quốc tế",
                "data": {"conditions": ["pool", "near_school"]},
                "confidence": 0.9,
                "timestamp": 1234567890.123
            }
        }


class ToolCallItem(BaseModel):
    """Tool call action in ReAct loop"""
    id: str = Field(default_factory=lambda: f"tool_{datetime.now().timestamp()}")
    tool_name: str
    arguments: Dict[str, Any]
    reason: str = Field(..., description="Why this tool was called")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class ObservationItem(BaseModel):
    """Observation from tool execution"""
    id: str = Field(default_factory=lambda: f"obs_{datetime.now().timestamp()}")
    tool_call_id: str
    result: Any
    success: bool
    insight: str = Field(..., description="What we learned from this observation")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class AmbiguityType(str, Enum):
    """Types of ambiguity in user queries"""
    LOCATION_TOO_BROAD = "location_too_broad"
    PROPERTY_TYPE_MISSING = "property_type_missing"
    PRICE_RANGE_UNCLEAR = "price_range_unclear"
    AMENITY_AMBIGUOUS = "amenity_ambiguous"
    MULTIPLE_INTENTS = "multiple_intents"


class ClarificationQuestion(BaseModel):
    """Question to clarify ambiguous query"""
    type: AmbiguityType
    question: str
    options: List[str]
    default: Optional[str] = None


class AmbiguityDetectionResult(BaseModel):
    """Result of ambiguity detection"""
    has_ambiguity: bool
    clarifications: List[ClarificationQuestion] = []
    confidence: float = Field(..., ge=0.0, le=1.0)


class KnowledgeExpansion(BaseModel):
    """Query expansion using domain knowledge"""
    original_query: str
    expanded_terms: List[str] = Field(default=[], description="Additional search terms")
    synonyms: Dict[str, List[str]] = Field(default={}, description="Synonyms for key terms")
    filters: Dict[str, Any] = Field(default={}, description="Inferred filters")
    reasoning: str = Field(..., description="Why these expansions were added")


class ReActStep(BaseModel):
    """One complete step in ReAct loop: Thought → Action → Observation"""
    thought: ThinkingItem
    action: Optional[ToolCallItem] = None
    observation: Optional[ObservationItem] = None


class ReasoningChain(BaseModel):
    """Complete reasoning chain for a query"""
    query: str
    steps: List[ReActStep] = []
    ambiguity_check: Optional[AmbiguityDetectionResult] = None
    knowledge_expansion: Optional[KnowledgeExpansion] = None
    final_conclusion: Optional[str] = None
    overall_confidence: float = Field(..., ge=0.0, le=1.0)

    def add_thought(self, stage: ThinkingStage, thought: str, data: Optional[Dict] = None, confidence: float = 1.0):
        """Add a thinking step"""
        thinking = ThinkingItem(stage=stage, thought=thought, data=data, confidence=confidence)
        step = ReActStep(thought=thinking)
        self.steps.append(step)
        return thinking.id

    def add_action(self, tool_name: str, arguments: Dict[str, Any], reason: str):
        """Add a tool call action to the last step"""
        if not self.steps:
            raise ValueError("Cannot add action without a thought step first")
        action = ToolCallItem(tool_name=tool_name, arguments=arguments, reason=reason)
        self.steps[-1].action = action
        return action.id

    def add_observation(self, tool_call_id: str, result: Any, success: bool, insight: str):
        """Add an observation to the last step"""
        if not self.steps or not self.steps[-1].action:
            raise ValueError("Cannot add observation without an action")
        obs = ObservationItem(tool_call_id=tool_call_id, result=result, success=success, insight=insight)
        self.steps[-1].observation = obs
        return obs.id

    def get_summary(self) -> str:
        """Get human-readable summary of reasoning chain"""
        summary_parts = []
        for i, step in enumerate(self.steps, 1):
            summary_parts.append(f"Step {i}: {step.thought.thought}")
            if step.action:
                summary_parts.append(f"  → Action: {step.action.tool_name}")
            if step.observation:
                summary_parts.append(f"  → Result: {step.observation.insight}")
        return "\n".join(summary_parts)


class StreamingReasoningEvent(BaseModel):
    """Event for streaming reasoning updates"""
    event_type: str  # "thought", "action", "observation", "conclusion"
    content: Union[ThinkingItem, ToolCallItem, ObservationItem, str]
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
