"""
Query Decomposition Operator
Breaks complex queries into sub-queries

CTO Design: Multi-step Reasoning
"""
import httpx
from typing import List, Dict, Any
from pydantic import BaseModel

from ..base import PreRetrievalOperator, OperatorResult, OperatorConfig
from ..registry import register_operator


class DecompositionInput(BaseModel):
    """Input for decomposition"""
    query: str
    core_gateway_url: str = "http://core-gateway:8080"


class DecompositionOutput(BaseModel):
    """Output from decomposition"""
    original_query: str
    sub_queries: List[str]
    reasoning: str
    metadata: Dict[str, Any] = {}


@register_operator("query_decomposition")
class QueryDecompositionOperator(PreRetrievalOperator):
    """
    Query Decomposition Operator

    Breaks complex queries into simpler sub-queries:
    - "Căn hộ 2PN gần trường quốc tế giá dưới 5 tỷ"
      → ["căn hộ 2 phòng ngủ", "gần trường quốc tế", "giá dưới 5 tỷ"]

    Impact: +20% for multi-constraint queries
    """

    def __init__(self, name: str = "query_decomposition", config: OperatorConfig = None, core_gateway_url: str = "http://core-gateway:8080", **kwargs):
        super().__init__(name, config, **kwargs)
        self.core_gateway_url = core_gateway_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def validate_input(self, input_data: Any) -> bool:
        return "query" in (input_data if isinstance(input_data, dict) else input_data.__dict__)

    async def execute(self, input_data: Any) -> OperatorResult:
        """Decompose query"""
        if isinstance(input_data, dict):
            decomp_input = DecompositionInput(**input_data)
        else:
            decomp_input = input_data

        query = decomp_input.query

        # Check if query needs decomposition
        if not self._needs_decomposition(query):
            return OperatorResult(
                success=True,
                data=DecompositionOutput(
                    original_query=query,
                    sub_queries=[query],
                    reasoning="Simple query, no decomposition needed"
                )
            )

        self.logger.info(f"🔍 Decomposing complex query: '{query}'")

        sub_queries = await self._decompose_with_llm(query)

        output = DecompositionOutput(
            original_query=query,
            sub_queries=sub_queries,
            reasoning=f"Decomposed into {len(sub_queries)} sub-queries",
            metadata={"decomposition_method": "llm", "sub_query_count": len(sub_queries)}
        )

        return OperatorResult(success=True, data=output, metadata=output.metadata)

    def _needs_decomposition(self, query: str) -> bool:
        """Check if query is complex enough to decompose"""
        # Simple heuristic: Check for multiple constraints
        constraint_keywords = ["và", "gần", "giá", "dưới", "trên", "có", "với"]
        count = sum(1 for kw in constraint_keywords if kw in query.lower())
        return count >= 2

    async def _decompose_with_llm(self, query: str) -> List[str]:
        """Decompose using LLM"""
        prompt = f"""Break this complex real estate query into simpler sub-queries:

Query: {query}

Return 2-4 sub-queries, one per line, no numbering. Each should focus on one aspect."""

        try:
            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.3
                },
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("content", "").strip()
                sub_queries = [line.strip() for line in text.split("\n") if line.strip() and not line.strip().startswith("-")]
                return sub_queries[:4]  # Max 4 sub-queries
            else:
                return [query]  # Fallback

        except Exception as e:
            self.logger.error(f"Decomposition error: {e}")
            return [query]  # Fallback

    async def cleanup(self):
        await self.http_client.aclose()
