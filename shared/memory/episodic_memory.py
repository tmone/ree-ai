"""
Episodic Memory
Stores past interactions and experiences

Examples:
- "User asked about 2-bedroom apartments in District 2 yesterday"
- "Search for villa in Phu My Hung returned 5 results"
- "User preferred properties under 5 billion VND"
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .base import MemoryStore, MemoryEntry, MemoryType, MemoryQuery


class EpisodicMemory(MemoryStore):
    """
    Episodic Memory Store

    Remembers:
    - Past user queries
    - Search results and outcomes
    - User preferences and feedback
    - Interaction patterns
    """

    def __init__(self):
        super().__init__(MemoryType.EPISODIC)
        self.memories: Dict[str, MemoryEntry] = {}
        self.logger = logging.getLogger("EpisodicMemory")

    async def store(self, entry: MemoryEntry) -> str:
        """
        Store episodic memory

        Args:
            entry: Memory entry with interaction details

        Returns:
            Memory ID
        """
        entry.memory_type = MemoryType.EPISODIC

        # Store
        self.memories[entry.id] = entry

        self.logger.info(f"📝 Stored episodic memory: {entry.id[:8]}... (user: {entry.metadata.get('user_id', 'unknown')})")

        return entry.id

    async def retrieve(self, query: MemoryQuery) -> List[MemoryEntry]:
        """
        Retrieve relevant past interactions

        Ranking by:
        - Semantic similarity (if embeddings available)
        - Recency
        - Importance
        """
        results = []

        # Filter by user_id if provided
        for memory in self.memories.values():
            if query.user_id and memory.metadata.get('user_id') != query.user_id:
                continue

            # Filter by importance
            if memory.importance < query.min_importance:
                continue

            # Filter by time range
            if query.time_range:
                if "start" in query.time_range and memory.created_at < query.time_range["start"]:
                    continue
                if "end" in query.time_range and memory.created_at > query.time_range["end"]:
                    continue

            # Compute relevance (simple keyword matching for MVP)
            relevance = self._compute_relevance(query.query, memory.content)

            # Compute recency
            recency = self.compute_recency(memory.created_at)

            # Compute importance
            importance = self.compute_importance(
                recency=recency,
                relevance=relevance,
                access_count=memory.access_count
            )

            # Update importance
            memory.importance = importance

            results.append((memory, importance))

        # Sort by importance
        results.sort(key=lambda x: x[1], reverse=True)

        # Take top K
        top_memories = [mem for mem, score in results[:query.limit]]

        # Update access counts
        for memory in top_memories:
            await self.increment_access(memory.id)

        self.logger.info(f"🔍 Retrieved {len(top_memories)} episodic memories for query: '{query.query}'")

        return top_memories

    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory entry"""
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]

        for key, value in updates.items():
            if key == "access_count" and value == "+1":
                memory.access_count += 1
            else:
                setattr(memory, key, value)

        return True

    async def delete(self, memory_id: str) -> bool:
        """Delete memory entry"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self.logger.info(f"🗑️  Deleted memory: {memory_id[:8]}...")
            return True
        return False

    async def consolidate(self) -> int:
        """
        Consolidate memories:
        - Merge similar memories
        - Decay old, unimportant memories
        """
        consolidated = 0

        # Delete low-importance, old memories
        to_delete = []
        for mem_id, memory in self.memories.items():
            recency = self.compute_recency(memory.created_at, decay_days=90)
            if memory.importance < 0.2 and recency < 0.1:
                to_delete.append(mem_id)

        for mem_id in to_delete:
            await self.delete(mem_id)
            consolidated += 1

        self.logger.info(f"🧹 Consolidated {consolidated} episodic memories")

        return consolidated

    def _compute_relevance(self, query: str, content: str) -> float:
        """
        Compute semantic relevance (simple keyword matching for MVP)

        TODO: Replace with embedding-based similarity
        """
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        matches = len(query_words & content_words)
        return min(1.0, matches / len(query_words))

    async def store_interaction(
        self,
        user_id: str,
        query: str,
        results: List[Dict[str, Any]],
        success: bool,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Convenience method: Store user interaction

        Args:
            user_id: User ID
            query: User's query
            results: Search results
            success: Whether interaction was successful
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        content = f"User query: {query} | Results: {len(results)} properties | Success: {success}"

        entry = MemoryEntry(
            memory_type=MemoryType.EPISODIC,
            content=content,
            metadata={
                "user_id": user_id,
                "query": query,
                "result_count": len(results),
                "success": success,
                **(metadata or {})
            },
            importance=0.7 if success else 0.3  # Success = more important
        )

        return await self.store(entry)

    async def get_user_preferences(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Extract user preferences from episodic memories

        Returns:
        {
            "preferred_districts": ["Quận 2", "Quận 7"],
            "price_range": {"min": 3000000000, "max": 8000000000},
            "property_types": ["căn hộ", "biệt thự"],
            "common_queries": [...]
        }
        """
        query = MemoryQuery(
            query="",
            user_id=user_id,
            limit=limit
        )

        memories = await self.retrieve(query)

        # Analyze patterns
        preferences = {
            "preferred_districts": [],
            "price_ranges": [],
            "property_types": [],
            "common_features": []
        }

        for memory in memories:
            # Extract patterns from metadata
            if "query" in memory.metadata:
                query_text = memory.metadata["query"].lower()

                # Extract districts
                districts = ["quận 2", "quận 7", "quận 1", "quận 3", "bình thạnh"]
                for district in districts:
                    if district in query_text:
                        preferences["preferred_districts"].append(district)

                # Extract property types
                types = ["căn hộ", "biệt thự", "nhà phố", "đất"]
                for ptype in types:
                    if ptype in query_text:
                        preferences["property_types"].append(ptype)

        # Count occurrences
        from collections import Counter
        preferences["preferred_districts"] = [
            item for item, count in Counter(preferences["preferred_districts"]).most_common(3)
        ]
        preferences["property_types"] = [
            item for item, count in Counter(preferences["property_types"]).most_common(2)
        ]

        return preferences
