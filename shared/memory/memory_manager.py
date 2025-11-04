"""
Memory Manager
Unified interface for all memory types
"""
from typing import List, Dict, Any, Optional
import logging

from .base import MemoryType, MemoryEntry, MemoryQuery
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .procedural_memory import ProceduralMemory


class MemoryManager:
    """
    Unified Memory Manager

    Manages all memory types:
    - Episodic: Past interactions
    - Semantic: Domain facts
    - Procedural: Learned skills

    Implements CTO's Agentic Memory Architecture
    """

    def __init__(self):
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()

        self.logger = logging.getLogger("MemoryManager")
        self.logger.info("🧠 Memory Manager initialized with 3 memory types")

    async def store(
        self,
        memory_type: MemoryType,
        entry: MemoryEntry
    ) -> str:
        """
        Store memory in appropriate store

        Args:
            memory_type: Type of memory
            entry: Memory entry

        Returns:
            Memory ID
        """
        if memory_type == MemoryType.EPISODIC:
            return await self.episodic.store(entry)
        elif memory_type == MemoryType.SEMANTIC:
            return await self.semantic.store(entry)
        elif memory_type == MemoryType.PROCEDURAL:
            return await self.procedural.store(entry)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    async def retrieve(
        self,
        query: MemoryQuery
    ) -> List[MemoryEntry]:
        """
        Retrieve memories from appropriate store(s)

        Args:
            query: Memory query

        Returns:
            List of relevant memories
        """
        if query.memory_type:
            # Retrieve from specific type
            if query.memory_type == MemoryType.EPISODIC:
                return await self.episodic.retrieve(query)
            elif query.memory_type == MemoryType.SEMANTIC:
                return await self.semantic.retrieve(query)
            elif query.memory_type == MemoryType.PROCEDURAL:
                return await self.procedural.retrieve(query)
        else:
            # Retrieve from all types
            episodic_memories = await self.episodic.retrieve(query)
            semantic_memories = await self.semantic.retrieve(query)
            procedural_memories = await self.procedural.retrieve(query)

            # Combine and sort by importance
            all_memories = episodic_memories + semantic_memories + procedural_memories
            all_memories.sort(key=lambda m: m.importance, reverse=True)

            return all_memories[:query.limit]

    async def retrieve_context_for_query(
        self,
        user_id: str,
        query: str,
        include_preferences: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve complete context for answering query

        Returns:
        {
            "episodic_memories": [...],  # Past interactions
            "semantic_facts": [...],     # Domain knowledge
            "applicable_skills": [...],  # Learned strategies
            "user_preferences": {...}    # Extracted preferences
        }
        """
        self.logger.info(f"🔍 Retrieving memory context for user {user_id}: '{query}'")

        # Retrieve episodic memories
        episodic_query = MemoryQuery(
            query=query,
            memory_type=MemoryType.EPISODIC,
            user_id=user_id,
            limit=5
        )
        episodic_memories = await self.episodic.retrieve(episodic_query)

        # Retrieve semantic facts
        semantic_query = MemoryQuery(
            query=query,
            memory_type=MemoryType.SEMANTIC,
            limit=5
        )
        semantic_facts = await self.semantic.retrieve(semantic_query)

        # Retrieve applicable skills
        procedural_query = MemoryQuery(
            query=query,
            memory_type=MemoryType.PROCEDURAL,
            limit=3
        )
        applicable_skills = await self.procedural.retrieve(procedural_query)

        # Get user preferences if requested
        user_preferences = {}
        if include_preferences:
            user_preferences = await self.episodic.get_user_preferences(user_id)

        context = {
            "episodic_memories": episodic_memories,
            "semantic_facts": semantic_facts,
            "applicable_skills": applicable_skills,
            "user_preferences": user_preferences
        }

        self.logger.info(
            f"📊 Context: {len(episodic_memories)} episodic, "
            f"{len(semantic_facts)} semantic, "
            f"{len(applicable_skills)} skills"
        )

        return context

    async def record_interaction(
        self,
        user_id: str,
        query: str,
        results: List[Dict[str, Any]],
        success: bool,
        applied_skills: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Record user interaction across all memory types

        Args:
            user_id: User ID
            query: User query
            results: Search results
            success: Whether interaction was successful
            applied_skills: Skills that were applied
            metadata: Additional metadata
        """
        # Store in episodic memory
        await self.episodic.store_interaction(
            user_id=user_id,
            query=query,
            results=results,
            success=success,
            metadata=metadata
        )

        # Update procedural memory (skill success rates)
        if applied_skills:
            for skill_id in applied_skills:
                await self.procedural.record_skill_usage(
                    skill_id=skill_id,
                    success=success
                )

        self.logger.info(f"📝 Recorded interaction for user {user_id}: success={success}")

    async def learn_from_patterns(self):
        """
        Analyze episodic memories to learn new semantic facts and procedural skills

        This is the "learning" component of agentic memory
        """
        self.logger.info("🌟 Analyzing patterns to learn new knowledge...")

        # TODO: Implement pattern analysis
        # Example patterns to detect:
        # 1. Frequently co-occurring search terms → Semantic fact
        # 2. Query rewrites that work → Procedural skill
        # 3. Filter combinations that succeed → Procedural skill

        learned_count = 0

        # Placeholder for future implementation
        self.logger.info(f"💡 Learned {learned_count} new patterns")

        return learned_count

    async def consolidate_all_memories(self):
        """
        Consolidate memories across all types

        Removes:
        - Old, unimportant episodic memories
        - Low-success procedural skills
        - Outdated semantic facts
        """
        self.logger.info("🧹 Consolidating all memories...")

        episodic_count = await self.episodic.consolidate()
        semantic_count = await self.semantic.consolidate()
        procedural_count = await self.procedural.consolidate()

        total = episodic_count + semantic_count + procedural_count

        self.logger.info(
            f"✅ Consolidated {total} memories "
            f"(episodic: {episodic_count}, semantic: {semantic_count}, procedural: {procedural_count})"
        )

        return total

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        return {
            "episodic_count": len(self.episodic.memories),
            "semantic_count": len(self.semantic.memories),
            "procedural_count": len(self.procedural.memories),
            "total_count": len(self.episodic.memories) + len(self.semantic.memories) + len(self.procedural.memories)
        }
