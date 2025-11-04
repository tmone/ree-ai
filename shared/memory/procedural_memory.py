"""
Procedural Memory
Stores learned skills and strategies

Examples:
- "When user asks about international schools, suggest District 2 and 7"
- "If query has typos, apply query rewriting first"
- "For villa searches, expand to include garden, garage keywords"
- "Rerank strategy works best for property_type queries"
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .base import MemoryStore, MemoryEntry, MemoryType, MemoryQuery


class ProceduralMemory(MemoryStore):
    """
    Procedural Memory Store

    Stores:
    - Learned strategies (what works)
    - Query patterns → Action mappings
    - Operator configurations
    - Success/failure patterns
    """

    def __init__(self):
        super().__init__(MemoryType.PROCEDURAL)
        self.memories: Dict[str, MemoryEntry] = {}
        self.logger = logging.getLogger("ProceduralMemory")

        # Pre-load initial skills
        self._load_initial_skills()

    def _load_initial_skills(self):
        """Load initial procedural skills"""
        initial_skills = [
            {
                "skill_name": "international_school_query_handler",
                "content": "When query mentions international schools, expand to AIS/BIS and suggest District 2 or 7",
                "metadata": {
                    "trigger_pattern": "trường quốc tế|international school",
                    "action": "expand_query",
                    "parameters": {
                        "terms": ["AIS", "BIS", "Australian International School"],
                        "filters": {"district": {"$in": ["Quận 2", "Quận 7"]}}
                    },
                    "success_rate": 0.85,
                    "usage_count": 0
                },
                "importance": 0.9
            },
            {
                "skill_name": "typo_detection_and_correction",
                "content": "When query has common typos (can ho, biet thu), apply query rewriting",
                "metadata": {
                    "trigger_pattern": "can ho|biet thu|nha pho|Q[0-9]",
                    "action": "rewrite_query",
                    "parameters": {
                        "operator": "query_rewriter"
                    },
                    "success_rate": 0.75,
                    "usage_count": 0
                },
                "importance": 0.8
            },
            {
                "skill_name": "villa_query_expansion",
                "content": "For villa queries, expand to include garden, garage, rooftop keywords",
                "metadata": {
                    "trigger_pattern": "biệt thự|villa",
                    "action": "expand_terms",
                    "parameters": {
                        "additional_terms": ["garden", "garage", "rooftop", "vườn", "sân vườn"]
                    },
                    "success_rate": 0.70,
                    "usage_count": 0
                },
                "importance": 0.7
            },
            {
                "skill_name": "low_results_retry_strategy",
                "content": "When < 3 results after grading, rewrite query and retry",
                "metadata": {
                    "trigger_condition": "graded_documents < 3",
                    "action": "self_correct",
                    "parameters": {
                        "max_retries": 2,
                        "operator_sequence": ["query_rewriter", "retrieval", "grader"]
                    },
                    "success_rate": 0.68,
                    "usage_count": 0
                },
                "importance": 0.85
            },
            {
                "skill_name": "reranking_for_location_queries",
                "content": "Reranking works best for queries with specific location requirements",
                "metadata": {
                    "trigger_pattern": "quận [0-9]|district [0-9]|thảo điền|phú mỹ hưng",
                    "action": "enable_reranking",
                    "parameters": {
                        "reranker_config": {"top_k": 5}
                    },
                    "success_rate": 0.80,
                    "usage_count": 0
                },
                "importance": 0.75
            }
        ]

        for skill in initial_skills:
            entry = MemoryEntry(
                memory_type=MemoryType.PROCEDURAL,
                content=skill["content"],
                metadata=skill["metadata"],
                importance=skill["importance"]
            )
            self.memories[entry.id] = entry

        self.logger.info(f"🧠 Loaded {len(initial_skills)} procedural skills")

    async def store(self, entry: MemoryEntry) -> str:
        """Store procedural skill"""
        entry.memory_type = MemoryType.PROCEDURAL

        self.memories[entry.id] = entry

        self.logger.info(f"📝 Stored procedural skill: {entry.metadata.get('skill_name', 'unknown')}")

        return entry.id

    async def retrieve(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve applicable skills for query"""
        import re

        results = []

        for memory in self.memories.values():
            # Check trigger pattern
            trigger_pattern = memory.metadata.get("trigger_pattern")
            if trigger_pattern:
                if re.search(trigger_pattern, query.query, re.IGNORECASE):
                    # Pattern matched!
                    success_rate = memory.metadata.get("success_rate", 0.5)
                    results.append((memory, success_rate))

        # Sort by success rate
        results.sort(key=lambda x: x[1], reverse=True)

        top_memories = [mem for mem, score in results[:query.limit]]

        if top_memories:
            self.logger.info(f"🎯 Found {len(top_memories)} applicable skills for: '{query.query}'")

        return top_memories

    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update procedural skill"""
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]

        for key, value in updates.items():
            if key == "usage_count" and value == "+1":
                memory.metadata["usage_count"] = memory.metadata.get("usage_count", 0) + 1
            elif key == "success_rate":
                # Update success rate with exponential moving average
                old_rate = memory.metadata.get("success_rate", 0.5)
                alpha = 0.3  # Learning rate
                new_rate = alpha * value + (1 - alpha) * old_rate
                memory.metadata["success_rate"] = new_rate
                memory.importance = new_rate  # Update importance
            else:
                setattr(memory, key, value)

        return True

    async def delete(self, memory_id: str) -> bool:
        """Delete procedural skill"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False

    async def consolidate(self) -> int:
        """
        Consolidate procedural memories:
        - Remove skills with very low success rate
        - Promote frequently used skills
        """
        consolidated = 0

        to_delete = []
        for mem_id, memory in self.memories.items():
            success_rate = memory.metadata.get("success_rate", 0.5)
            usage_count = memory.metadata.get("usage_count", 0)

            # Delete skills with < 30% success rate and used at least 10 times
            if usage_count >= 10 and success_rate < 0.3:
                to_delete.append(mem_id)

        for mem_id in to_delete:
            await self.delete(mem_id)
            consolidated += 1

        if consolidated > 0:
            self.logger.info(f"🧹 Removed {consolidated} low-performing skills")

        return consolidated

    async def record_skill_usage(
        self,
        skill_id: str,
        success: bool
    ):
        """
        Record skill usage and outcome

        Args:
            skill_id: Skill memory ID
            success: Whether skill application was successful
        """
        await self.update(skill_id, {"usage_count": "+1"})

        if success:
            await self.update(skill_id, {"success_rate": 1.0})
        else:
            await self.update(skill_id, {"success_rate": 0.0})

        self.logger.debug(f"📊 Recorded skill usage: {skill_id[:8]}... → {'✅ success' if success else '❌ fail'}")

    async def learn_new_skill(
        self,
        skill_name: str,
        description: str,
        trigger_pattern: str,
        action: str,
        parameters: Dict[str, Any],
        initial_importance: float = 0.5
    ) -> str:
        """
        Learn new procedural skill from experience

        Args:
            skill_name: Unique skill name
            description: Skill description
            trigger_pattern: Regex pattern to trigger skill
            action: Action to take
            parameters: Action parameters
            initial_importance: Initial importance (0.0-1.0)

        Returns:
            Skill memory ID
        """
        entry = MemoryEntry(
            memory_type=MemoryType.PROCEDURAL,
            content=description,
            metadata={
                "skill_name": skill_name,
                "trigger_pattern": trigger_pattern,
                "action": action,
                "parameters": parameters,
                "success_rate": 0.5,  # Start neutral
                "usage_count": 0,
                "learned_at": datetime.now().isoformat()
            },
            importance=initial_importance
        )

        skill_id = await self.store(entry)

        self.logger.info(f"🌟 Learned new skill: {skill_name}")

        return skill_id

    async def get_best_strategy(
        self,
        query: str,
        min_success_rate: float = 0.6
    ) -> Optional[MemoryEntry]:
        """
        Get best strategy for query

        Args:
            query: User query
            min_success_rate: Minimum success rate

        Returns:
            Best matching skill or None
        """
        query_obj = MemoryQuery(
            query=query,
            limit=5
        )

        skills = await self.retrieve(query_obj)

        # Filter by success rate
        valid_skills = [
            skill for skill in skills
            if skill.metadata.get("success_rate", 0) >= min_success_rate
        ]

        if valid_skills:
            # Return best skill
            best_skill = max(valid_skills, key=lambda s: s.metadata.get("success_rate", 0))
            self.logger.info(
                f"🎯 Best strategy: {best_skill.metadata.get('skill_name')} "
                f"(success rate: {best_skill.metadata.get('success_rate', 0):.2%})"
            )
            return best_skill

        return None
