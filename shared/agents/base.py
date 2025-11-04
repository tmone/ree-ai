"""
Base Agent Classes
Foundation for Multi-Agent System
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid
import logging


class AgentRole(str, Enum):
    """Agent roles in the system"""
    SUPERVISOR = "supervisor"      # Coordinator
    SPECIALIST = "specialist"      # Specialized worker
    CRITIC = "critic"             # Quality evaluator
    PLANNER = "planner"           # Task planner


class AgentCapability(str, Enum):
    """Agent capabilities"""
    SEARCH = "search"             # Property search
    CLASSIFY = "classify"         # Query classification
    GRADE = "grade"               # Document grading
    RERANK = "rerank"             # Result reranking
    CRITIQUE = "critique"         # Self-reflection
    PLAN = "plan"                 # Task planning
    EXECUTE = "execute"           # Task execution


class AgentMessage(BaseModel):
    """Message passed between agents"""
    id: str = None
    from_agent: str
    to_agent: Optional[str] = None  # None = broadcast
    content: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    message_type: str = "info"  # info, request, response, error

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()

    class Config:
        arbitrary_types_allowed = True


class AgentResult(BaseModel):
    """Result from agent execution"""
    success: bool
    agent_name: str
    capability: AgentCapability
    data: Any
    reasoning: str = ""
    confidence: float = 1.0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class BaseAgent(ABC):
    """
    Base Agent Class

    Implements CTO's Agent Architecture:
    - Autonomous decision-making
    - Tool usage
    - Inter-agent communication
    - Self-monitoring
    """

    def __init__(
        self,
        name: str,
        role: AgentRole,
        capabilities: List[AgentCapability],
        logger: Optional[logging.Logger] = None
    ):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.logger = logger or logging.getLogger(f"Agent.{name}")

        self.message_inbox: List[AgentMessage] = []
        self.execution_history: List[AgentResult] = []

        self.logger.info(f"🤖 Agent initialized: {name} ({role}) with capabilities: {capabilities}")

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute task with agent's capabilities

        Args:
            task: Task specification

        Returns:
            AgentResult with output
        """
        pass

    @abstractmethod
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """
        Check if agent can handle this task

        Args:
            task: Task specification

        Returns:
            True if agent has required capabilities
        """
        pass

    async def receive_message(self, message: AgentMessage):
        """
        Receive message from another agent

        Args:
            message: Agent message
        """
        self.message_inbox.append(message)
        self.logger.debug(f"📨 Received message from {message.from_agent}: {message.content}")

    async def send_message(
        self,
        to_agent: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        message_type: str = "info"
    ) -> AgentMessage:
        """
        Send message to another agent

        Args:
            to_agent: Target agent name
            content: Message content
            data: Optional data payload
            message_type: Message type

        Returns:
            Sent message
        """
        message = AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            content=content,
            data=data,
            message_type=message_type
        )

        self.logger.debug(f"📤 Sent message to {to_agent}: {content}")

        return message

    async def broadcast_message(
        self,
        content: str,
        data: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Broadcast message to all agents

        Args:
            content: Message content
            data: Optional data payload

        Returns:
            Broadcast message
        """
        message = AgentMessage(
            from_agent=self.name,
            to_agent=None,  # Broadcast
            content=content,
            data=data,
            message_type="broadcast"
        )

        self.logger.debug(f"📢 Broadcast: {content}")

        return message

    def record_execution(self, result: AgentResult):
        """
        Record execution result

        Args:
            result: Agent execution result
        """
        self.execution_history.append(result)

        if result.success:
            self.logger.info(
                f"✅ Task completed: {result.capability} "
                f"(confidence: {result.confidence:.2f}, time: {result.execution_time:.2f}s)"
            )
        else:
            self.logger.error(f"❌ Task failed: {result.capability}")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics"""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_confidence": 0.0,
                "average_time": 0.0
            }

        total = len(self.execution_history)
        successes = sum(1 for r in self.execution_history if r.success)
        avg_confidence = sum(r.confidence for r in self.execution_history) / total
        avg_time = sum(r.execution_time for r in self.execution_history) / total

        return {
            "total_executions": total,
            "success_rate": successes / total,
            "average_confidence": avg_confidence,
            "average_time": avg_time
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"
