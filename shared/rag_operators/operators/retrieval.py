"""
Retrieval Operator
Retrieves documents from database
"""
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..base import RetrievalOperator as BaseRetrievalOp, OperatorResult, OperatorConfig
from ..registry import register_operator


class RetrievalInput(BaseModel):
    """Input for retrieval"""
    query: str
    filters: Dict[str, Any] = {}
    limit: int = 10


class RetrievalOutput(BaseModel):
    """Output from retrieval"""
    documents: List[Dict[str, Any]]
    count: int
    metadata: Dict[str, Any] = {}


@register_operator("hybrid_retrieval")
class HybridRetrievalOperator(BaseRetrievalOp):
    """
    Hybrid Retrieval Operator

    Calls DB Gateway for hybrid search (vector + BM25)
    """

    def __init__(
        self,
        name: str = "hybrid_retrieval",
        config: OperatorConfig = None,
        db_gateway_url: str = "http://db-gateway:8080",
        **kwargs
    ):
        super().__init__(name, config, **kwargs)
        self.db_gateway_url = db_gateway_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def validate_input(self, input_data: Any) -> bool:
        """Validate input has query"""
        if isinstance(input_data, dict):
            return "query" in input_data
        return hasattr(input_data, 'query') or hasattr(input_data, 'rewritten_query')

    async def execute(self, input_data: Any) -> OperatorResult:
        """Retrieve documents from DB Gateway"""
        # Parse input
        if isinstance(input_data, dict):
            retrieval_input = RetrievalInput(**input_data)
        elif hasattr(input_data, 'rewritten_query'):
            # Input from QueryRewriter
            retrieval_input = RetrievalInput(
                query=input_data.rewritten_query,
                filters=input_data.metadata.get('filters', {}),
                limit=input_data.metadata.get('limit', 10)
            )
        else:
            retrieval_input = RetrievalInput(query=str(input_data))

        query = retrieval_input.query
        filters = retrieval_input.filters
        limit = retrieval_input.limit

        self.logger.info(f"🔍 Retrieving documents for: '{query}' (limit={limit})")

        try:
            response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json={
                    "query": query,
                    "filters": filters,
                    "limit": limit
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                documents = data.get("results", [])

                self.logger.info(f"✅ Retrieved {len(documents)} documents")

                output = RetrievalOutput(
                    documents=documents,
                    count=len(documents),
                    metadata={
                        "query": query,
                        "filters": filters,
                        "retrieval_method": "hybrid"
                    }
                )

                return OperatorResult(
                    success=True,
                    data=output,
                    metadata=output.metadata
                )

            else:
                self.logger.error(f"❌ Retrieval failed: HTTP {response.status_code}")
                return OperatorResult(
                    success=False,
                    data=None,
                    error=f"HTTP {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"❌ Retrieval error: {e}")
            return OperatorResult(
                success=False,
                data=None,
                error=str(e)
            )

    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()
