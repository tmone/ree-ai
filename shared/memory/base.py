"""
Base Memory Classes
Foundation for Agentic Memory System
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


class MemoryType(str, Enum):
    """Types of memory"""
    SHORT_TERM = "short_term"  # Current conversation
    EPISODIC = "episodic"      # Past interactions
    SEMANTIC = "semantic"      # Domain facts
    PROCEDURAL = "procedural"  # Learned skills


class MemoryEntry(BaseModel):
    """Single memory entry"""
    id: str = None
    memory_type: MemoryType
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = None
    last_accessed: datetime = None
    access_count: int = 0
    importance: float = 0.5  # 0.0-1.0

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_accessed is None:
            self.last_accessed = self.created_at

    class Config:
        arbitrary_types_allowed = True


class MemoryQuery(BaseModel):
    """Query for memory retrieval"""
    query: str
    memory_type: Optional[MemoryType] = None
    user_id: Optional[str] = None
    limit: int = 5
    min_importance: float = 0.0
    time_range: Optional[Dict[str, datetime]] = None
    filters: Dict[str, Any] = {}


class MemoryStore(ABC):
    """
    Base class for memory storage

    Implements CTO's Memory Architecture:
    - Store memories with embeddings
    - Retrieve by semantic similarity
    - Importance scoring
    - Temporal decay
    """

    def __init__(self, memory_type: MemoryType):
        self.memory_type = memory_type

    @abstractmethod
    async def store(self, entry: MemoryEntry) -> str:
        """
        Store memory entry

        Args:
            entry: Memory entry to store

        Returns:
            Memory ID
        """
        pass

    @abstractmethod
    async def retrieve(self, query: MemoryQuery) -> List[MemoryEntry]:
        """
        Retrieve memories by semantic similarity

        Args:
            query: Memory query

        Returns:
            List of relevant memory entries
        """
        pass

    @abstractmethod
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update memory entry

        Args:
            memory_id: Memory ID
            updates: Fields to update

        Returns:
            Success status
        """
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """
        Delete memory entry

        Args:
            memory_id: Memory ID

        Returns:
            Success status
        """
        pass

    @abstractmethod
    async def consolidate(self) -> int:
        """
        Consolidate memories (merge similar, decay old)

        Returns:
            Number of memories consolidated
        """
        pass

    async def increment_access(self, memory_id: str):
        """Increment access count for memory"""
        await self.update(memory_id, {
            "access_count": "+1",
            "last_accessed": datetime.now()
        })

    def compute_importance(
        self,
        recency: float,
        relevance: float,
        access_count: int
    ) -> float:
        """
        Compute memory importance score

        Formula: importance = 0.4*recency + 0.4*relevance + 0.2*log(access_count+1)

        Args:
            recency: How recent (0.0-1.0, 1.0 = just created)
            relevance: Semantic relevance (0.0-1.0)
            access_count: Number of accesses

        Returns:
            Importance score (0.0-1.0)
        """
        import math

        access_score = min(1.0, math.log(access_count + 1) / 5.0)
        importance = 0.4 * recency + 0.4 * relevance + 0.2 * access_score

        return min(1.0, max(0.0, importance))

    def compute_recency(self, created_at: datetime, decay_days: int = 30) -> float:
        """
        Compute recency score with exponential decay

        Args:
            created_at: When memory was created
            decay_days: Days for score to decay to 0.5

        Returns:
            Recency score (0.0-1.0)
        """
        import math

        days_old = (datetime.now() - created_at).days
        decay_rate = math.log(0.5) / decay_days

        return math.exp(decay_rate * days_old)
