"""
Example: Modular RAG with Agentic Patterns
Demonstrates operator-based architecture with self-correction
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.rag_operators.base import OperatorConfig
from shared.rag_operators.flow import RAGFlow, FlowConfig
from shared.rag_operators.operators import (
    DocumentGraderOperator,
    RerankOperator,
    QueryRewriterOperator,
    HybridRetrievalOperator,
    GenerationOp
)
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def example_basic_rag_flow():
    """
    Example 1: Basic RAG Flow
    Retrieve → Grade → Rerank → Generate
    """
    print("\n" + "="*80)
    print("Example 1: Basic RAG Flow with Quality Control")
    print("="*80 + "\n")

    # Create operators
    retrieval = HybridRetrievalOperator(
        name="retrieval",
        db_gateway_url="http://localhost:8081"  # DB Gateway
    )

    grader = DocumentGraderOperator(
        name="grader",
        core_gateway_url="http://localhost:8080",  # Core Gateway
        use_llm_grading=False  # Use fast grading
    )

    reranker = RerankOperator(
        name="reranker",
        core_gateway_url="http://localhost:8080",
        use_cross_encoder=False  # Use fast reranking
    )

    generator = GenerationOp(
        name="generator",
        core_gateway_url="http://localhost:8080",
        model="gpt-4o-mini"
    )

    # Create flow
    flow = RAGFlow(
        operators=[retrieval, grader, reranker, generator],
        config=FlowConfig(
            name="basic_rag_with_quality_control",
            description="Retrieve → Grade → Rerank → Generate",
            stop_on_error=True
        )
    )

    # Execute
    query = "Tìm căn hộ 2 phòng ngủ ở Quận 2"
    input_data = {
        "query": query,
        "filters": {},
        "limit": 10
    }

    result = await flow.execute(input_data)

    # Display results
    print(f"\n✅ Flow Status: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"⏱️  Total Time: {result.total_execution_time:.2f}s")
    print(f"📊 Operators: {len(result.operator_results)}")

    for i, op_result in enumerate(result.operator_results, 1):
        print(f"\n  [{i}] {flow.operators[i-1].name}:")
        print(f"      ✓ Success: {op_result.success}")
        print(f"      ⏱  Time: {op_result.execution_time:.2f}s")

    if result.success and result.final_output:
        print(f"\n🎉 Final Response:\n{result.final_output.response}\n")


async def example_self_correcting_rag():
    """
    Example 2: Self-Correcting RAG Flow
    If results are poor, rewrite query and retry
    """
    print("\n" + "="*80)
    print("Example 2: Self-Correcting RAG Flow")
    print("="*80 + "\n")

    # Create operators
    retrieval = HybridRetrievalOperator(name="retrieval")
    grader = DocumentGraderOperator(name="grader", use_llm_grading=False)
    reranker = RerankOperator(name="reranker")
    generator = GenerationOp(name="generator")

    # Create flow
    flow = RAGFlow(
        operators=[retrieval, grader, reranker, generator],
        config=FlowConfig(name="self_correcting_rag")
    )

    # Define retry condition: Retry if too few results
    def should_retry(result):
        if not result.success:
            return False

        # Check if we have enough good results
        for op_result in result.operator_results:
            if hasattr(op_result.data, 'filtered_count'):
                # DocumentGrader output
                passed = len(op_result.data.graded_documents)
                if passed < 3:  # Too few results
                    print(f"\n⚠️  Only {passed} documents passed grading. Retrying with rewritten query...")
                    return True

        return False

    # Execute with retry
    query = "can ho Q2"  # Intentionally poor query (typos, abbreviation)
    input_data = {
        "query": query,
        "filters": {},
        "limit": 10
    }

    result = await flow.execute_with_retry(
        input_data,
        max_retries=2,
        retry_condition=should_retry
    )

    print(f"\n✅ Final Status: {'SUCCESS' if result.success else 'FAILED'}")
    print(f"⏱️  Total Time: {result.total_execution_time:.2f}s")


async def example_query_rewriting():
    """
    Example 3: Query Rewriting (Standalone)
    """
    print("\n" + "="*80)
    print("Example 3: Query Rewriting")
    print("="*80 + "\n")

    rewriter = QueryRewriterOperator(
        name="query_rewriter",
        core_gateway_url="http://localhost:8080"
    )

    # Test with poor queries
    poor_queries = [
        "can ho Q2",  # Typos
        "nha",  # Too generic
        "biet thu PMH",  # Abbreviation
        "truong quoc te"  # Missing context
    ]

    for query in poor_queries:
        print(f"\n🔍 Original: '{query}'")

        input_data = {
            "original_query": query,
            "failure_reason": "Query too generic or has typos"
        }

        result = await rewriter.execute(input_data)

        if result.success:
            print(f"✅ Rewritten: '{result.data.rewritten_query}'")
            print(f"💡 Reasoning: {result.data.reasoning}")
            if result.data.changes:
                print(f"🔧 Changes:")
                for change in result.data.changes:
                    print(f"   - {change}")


async def example_document_grading():
    """
    Example 4: Document Grading (Standalone)
    """
    print("\n" + "="*80)
    print("Example 4: Document Grading")
    print("="*80 + "\n")

    grader = DocumentGraderOperator(
        name="grader",
        use_llm_grading=False  # Fast grading
    )

    # Mock documents
    query = "căn hộ 2 phòng ngủ Quận 2"
    documents = [
        {
            "title": "Căn hộ Masteri Thảo Điền 2PN",
            "district": "Quận 2",
            "description": "Căn hộ cao cấp 2 phòng ngủ tại Thảo Điền",
            "price": 5000000000
        },
        {
            "title": "Biệt thự Phú Mỹ Hưng",
            "district": "Quận 7",
            "description": "Biệt thự đơn lập 300m2",
            "price": 15000000000
        },
        {
            "title": "Nhà phố Bình Thạnh",
            "district": "Bình Thạnh",
            "description": "Nhà phố 3 tầng",
            "price": 8000000000
        }
    ]

    input_data = {
        "query": query,
        "documents": documents,
        "threshold": 0.5
    }

    result = await grader.execute(input_data)

    if result.success:
        print(f"📊 Grading Results:")
        print(f"   Total: {result.data.metadata['total_documents']}")
        print(f"   Passed: {result.data.metadata['passed_documents']}")
        print(f"   Filtered: {result.data.filtered_count}")
        print(f"   Avg Score: {result.data.average_score:.3f}\n")

        print(f"✅ Passed Documents:")
        for i, doc in enumerate(result.data.graded_documents, 1):
            print(f"   {i}. {doc['title']} (score: {doc['relevance_score']:.3f})")


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("Modular RAG with Agentic Patterns - Examples")
    print("="*80)

    # Example 4: Document Grading (doesn't require services)
    await example_document_grading()

    # Example 3: Query Rewriting (requires Core Gateway)
    # await example_query_rewriting()

    # Example 1: Basic RAG Flow (requires all services)
    # await example_basic_rag_flow()

    # Example 2: Self-Correcting RAG (requires all services)
    # await example_self_correcting_rag()

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
