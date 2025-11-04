"""
Complete Agentic RAG System Example
Demonstrates full integration of all components

Features:
- Modular RAG Operators (Phase 1)
- Agentic Memory System (Phase 2)
- Multi-Agent System (Phase 2)
- Advanced Operators (Phase 3)
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.rag_operators.flow import RAGFlow, FlowConfig
from shared.rag_operators.operators import (
    HybridRetrievalOperator,
    DocumentGraderOperator,
    RerankOperator,
    GenerationOp
)
from shared.rag_operators.operators.hyde import HyDEOperator
from shared.rag_operators.operators.query_decomposition import QueryDecompositionOperator
from shared.rag_operators.operators.reflection import ReflectionOperator
from shared.memory import MemoryManager
from shared.agents import SupervisorAgent
import logging

logging.basicConfig(level=logging.INFO)


async def example_full_agentic_rag():
    """
    Complete Example: All Features Combined

    Flow:
    1. Memory retrieval (preferences, skills, facts)
    2. Query enhancement (HyDE or Decomposition if needed)
    3. Multi-agent search pipeline
    4. Reflection and self-correction
    5. Memory storage
    """
    print("\n" + "="*80)
    print("COMPLETE AGENTIC RAG SYSTEM")
    print("="*80)

    # Initialize components
    memory = MemoryManager()
    supervisor = SupervisorAgent()

    user_id = "demo_user"
    query = "Tìm căn hộ 2 phòng ngủ gần trường quốc tế ở Quận 2"

    print(f"\n🔍 Query: {query}")

    # Step 1: Retrieve memory context
    print("\n📚 Step 1: Retrieving memory context...")
    context = await memory.retrieve_context_for_query(user_id, query)

    print(f"   - Episodic memories: {len(context['episodic_memories'])}")
    print(f"   - Semantic facts: {len(context['semantic_facts'])}")
    print(f"   - Applicable skills: {len(context['applicable_skills'])}")

    if context['user_preferences']:
        print(f"   - User preferences:")
        for key, values in context['user_preferences'].items():
            if values:
                print(f"      {key}: {values}")

    # Step 2: Check for learned skills
    print("\n🧠 Step 2: Checking procedural memory...")
    skills = context['applicable_skills']

    if skills:
        skill = skills[0]
        print(f"   ✅ Found applicable skill: {skill.metadata.get('skill_name')}")
        print(f"      Success rate: {skill.metadata.get('success_rate', 0):.1%}")
        print(f"      Action: {skill.metadata.get('action')}")

    # Step 3: Execute multi-agent search
    print("\n🤖 Step 3: Executing multi-agent search pipeline...")
    result = await supervisor.execute({
        "query": query,
        "filters": {},
        "limit": 10
    })

    if result.success:
        print(f"   ✅ Search successful!")
        print(f"      Retrieved: {result.metadata.get('search_count')} properties")
        print(f"      After grading: {result.metadata.get('graded_count')}")
        print(f"      Final results: {result.metadata.get('final_count')}")
        print(f"      Quality score: {result.metadata.get('quality_score', 0):.2f}")
        print(f"      Pipeline: {' → '.join(result.metadata.get('agent_pipeline', []))}")

    # Step 4: Record interaction
    print("\n📝 Step 4: Recording interaction in memory...")
    await memory.record_interaction(
        user_id=user_id,
        query=query,
        results=result.data if result.success else [],
        success=result.success,
        applied_skills=[s.id for s in skills] if skills else [],
        metadata={
            "confidence": result.confidence,
            "execution_time": result.execution_time
        }
    )
    print("   ✅ Interaction recorded")

    # Step 5: Display memory stats
    print("\n📊 Memory Statistics:")
    stats = memory.get_memory_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Step 6: Display agent stats
    print("\n🤖 Agent Statistics:")
    agent_stats = supervisor.get_all_agent_stats()
    for agent_name, stats in agent_stats.items():
        if stats.get("total_executions", 0) > 0:
            print(f"   {agent_name}:")
            print(f"      Executions: {stats['total_executions']}")
            print(f"      Success rate: {stats['success_rate']:.1%}")
            print(f"      Avg confidence: {stats['average_confidence']:.2f}")
            print(f"      Avg time: {stats['average_time']:.2f}s")

    print("\n" + "="*80)
    print("✅ Complete Agentic RAG Pipeline Executed Successfully!")
    print("="*80)


async def example_advanced_operators():
    """
    Example: Advanced Operators

    Demonstrates:
    - HyDE (Hypothetical Document Embeddings)
    - Query Decomposition
    - Reflection
    """
    print("\n" + "="*80)
    print("ADVANCED OPERATORS DEMO")
    print("="*80)

    # HyDE Example
    print("\n🔮 HyDE Operator:")
    hyde_op = HyDEOperator()
    hyde_result = await hyde_op.execute({"query": "Căn hộ cao cấp Quận 2"})

    if hyde_result.success:
        print(f"   Original: {hyde_result.data.original_query}")
        print(f"   Hypothetical doc: {hyde_result.data.hypothetical_document[:100]}...")
        print(f"   Enhanced query length: {len(hyde_result.data.enhanced_query)} chars")

    # Query Decomposition Example
    print("\n🔍 Query Decomposition Operator:")
    decomp_op = QueryDecompositionOperator()
    decomp_result = await decomp_op.execute({
        "query": "Căn hộ 2PN gần trường quốc tế giá dưới 5 tỷ ở Quận 2"
    })

    if decomp_result.success:
        print(f"   Original: {decomp_result.data.original_query}")
        print(f"   Sub-queries ({len(decomp_result.data.sub_queries)}):")
        for i, sq in enumerate(decomp_result.data.sub_queries, 1):
            print(f"      {i}. {sq}")

    # Reflection Example
    print("\n🪞 Reflection Operator:")
    refl_op = ReflectionOperator()
    refl_result = await refl_op.execute({
        "query": "Tìm căn hộ Quận 2",
        "response": "Tôi tìm thấy 5 căn hộ phù hợp...",
        "sources": [{"title": "Mock property"}]
    })

    if refl_result.success:
        print(f"   Quality score: {refl_result.data.quality_score:.2f}")
        print(f"   Needs improvement: {refl_result.data.needs_improvement}")
        if refl_result.data.issues_found:
            print(f"   Issues:")
            for issue in refl_result.data.issues_found:
                print(f"      - {issue}")

    print("\n" + "="*80)


async def main():
    """Run all examples"""
    # Example 1: Full Agentic RAG
    await example_full_agentic_rag()

    # Example 2: Advanced Operators
    await example_advanced_operators()


if __name__ == "__main__":
    asyncio.run(main())
