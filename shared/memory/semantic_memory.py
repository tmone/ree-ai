"""
Semantic Memory
Stores domain facts and knowledge

Examples:
- "Thảo Điền is an expat area in District 2"
- "Australian International School is in District 2"
- "Phu My Hung average price is 50-70 million VND/m²"
- "Properties near international schools have 20% premium"
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .base import MemoryStore, MemoryEntry, MemoryType, MemoryQuery


class SemanticMemory(MemoryStore):
    """
    Semantic Memory Store

    Stores:
    - Domain facts (locations, schools, prices)
    - Market knowledge (trends, patterns)
    - Rules and constraints
    - Statistical insights
    """

    def __init__(self):
        super().__init__(MemoryType.SEMANTIC)
        self.memories: Dict[str, MemoryEntry] = {}
        self.logger = logging.getLogger("SemanticMemory")

        # Pre-load domain knowledge
        self._load_initial_knowledge()

    def _load_initial_knowledge(self):
        """Load initial domain facts"""
        initial_facts = [
            {
                "content": "Thảo Điền is a premium expat area in District 2 with international schools",
                "metadata": {
                    "category": "location",
                    "district": "Quận 2",
                    "area": "Thảo Điền",
                    "characteristics": ["expat", "premium", "international_schools"]
                },
                "importance": 0.9
            },
            {
                "content": "Australian International School (AIS) is located in District 2, Thảo Điền",
                "metadata": {
                    "category": "school",
                    "school_name": "AIS",
                    "district": "Quận 2"
                },
                "importance": 0.9
            },
            {
                "content": "British International School (BIS) is in District 2",
                "metadata": {
                    "category": "school",
                    "school_name": "BIS",
                    "district": "Quận 2"
                },
                "importance": 0.9
            },
            {
                "content": "Phú Mỹ Hưng is a planned urban area in District 7 with good infrastructure",
                "metadata": {
                    "category": "location",
                    "district": "Quận 7",
                    "area": "Phú Mỹ Hưng",
                    "characteristics": ["planned", "infrastructure"]
                },
                "importance": 0.9
            },
            {
                "content": "Properties near international schools typically have 15-20% price premium",
                "metadata": {
                    "category": "pricing",
                    "factor": "school_proximity",
                    "impact": "15-20% premium"
                },
                "importance": 0.8
            },
            {
                "content": "District 2 average apartment price: 50-70 million VND/m²",
                "metadata": {
                    "category": "pricing",
                    "district": "Quận 2",
                    "property_type": "apartment",
                    "price_range": {"min": 50000000, "max": 70000000}
                },
                "importance": 0.8
            },
            {
                "content": "District 7 average apartment price: 40-60 million VND/m²",
                "metadata": {
                    "category": "pricing",
                    "district": "Quận 7",
                    "property_type": "apartment",
                    "price_range": {"min": 40000000, "max": 60000000}
                },
                "importance": 0.8
            }
        ]

        for fact in initial_facts:
            entry = MemoryEntry(
                memory_type=MemoryType.SEMANTIC,
                content=fact["content"],
                metadata=fact["metadata"],
                importance=fact["importance"]
            )
            self.memories[entry.id] = entry

        self.logger.info(f"📚 Loaded {len(initial_facts)} semantic facts")

    async def store(self, entry: MemoryEntry) -> str:
        """Store semantic fact"""
        entry.memory_type = MemoryType.SEMANTIC

        self.memories[entry.id] = entry

        self.logger.info(f"📝 Stored semantic fact: {entry.content[:50]}...")

        return entry.id

    async def retrieve(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve relevant domain facts"""
        results = []

        for memory in self.memories.values():
            # Filter by category if provided
            if "category" in query.filters:
                if memory.metadata.get("category") != query.filters["category"]:
                    continue

            # Filter by importance
            if memory.importance < query.min_importance:
                continue

            # Compute relevance
            relevance = self._compute_relevance(query.query, memory.content)

            if relevance > 0.1:  # Only include if somewhat relevant
                results.append((memory, relevance))

        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)

        top_memories = [mem for mem, score in results[:query.limit]]

        self.logger.info(f"🔍 Retrieved {len(top_memories)} semantic facts for: '{query.query}'")

        return top_memories

    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update semantic fact"""
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]
        for key, value in updates.items():
            setattr(memory, key, value)

        return True

    async def delete(self, memory_id: str) -> bool:
        """Delete semantic fact"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False

    async def consolidate(self) -> int:
        """
        Consolidate semantic memories:
        - Merge duplicate facts
        - Update outdated facts
        """
        # TODO: Implement fact merging
        return 0

    def _compute_relevance(self, query: str, content: str) -> float:
        """Compute semantic relevance"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        matches = len(query_words & content_words)
        return min(1.0, matches / len(query_words) * 1.5)  # Boost for semantic

    async def get_location_facts(self, district: str) -> List[MemoryEntry]:
        """Get facts about a specific district"""
        query = MemoryQuery(
            query=district,
            filters={"category": "location"},
            limit=5
        )
        return await self.retrieve(query)

    async def get_pricing_facts(self, district: str = None, property_type: str = None) -> List[MemoryEntry]:
        """Get pricing facts"""
        query_str = f"{district or ''} {property_type or ''}"
        query = MemoryQuery(
            query=query_str,
            filters={"category": "pricing"},
            limit=5
        )
        return await self.retrieve(query)

    async def store_market_insight(
        self,
        insight: str,
        category: str,
        confidence: float,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store market insight learned from data

        Args:
            insight: The insight text
            category: Category (location, pricing, trend)
            confidence: Confidence level (0.0-1.0)
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        entry = MemoryEntry(
            memory_type=MemoryType.SEMANTIC,
            content=insight,
            metadata={
                "category": category,
                "confidence": confidence,
                "learned_at": datetime.now().isoformat(),
                **(metadata or {})
            },
            importance=confidence  # Use confidence as importance
        )

        return await self.store(entry)
