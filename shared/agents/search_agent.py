"""
Search Agent
Specialized in property search
"""
from typing import Dict, Any
from datetime import datetime

from .base import BaseAgent, AgentRole, AgentCapability, AgentResult
from ..rag_operators.operators import HybridRetrievalOperator


class SearchAgent(BaseAgent):
    """
    Search Agent

    Specialization: Property search
    Uses: HybridRetrievalOperator (vector + BM25)
    """

    def __init__(self, name: str = "search_agent"):
        super().__init__(
            name=name,
            role=AgentRole.SPECIALIST,
            capabilities=[AgentCapability.SEARCH]
        )

        self.retrieval_op = HybridRetrievalOperator()

    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if task is a search task"""
        return task.get("type") == "search" or "query" in task

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute property search

        Args:
            task: {"query": str, "filters": {}, "limit": int}

        Returns:
            AgentResult with retrieved properties
        """
        start_time = datetime.now()

        self.logger.info(f"🔍 Searching for: '{task.get('query')}'")

        try:
            # Use retrieval operator
            result = await self.retrieval_op.safe_execute(task)

            execution_time = (datetime.now() - start_time).total_seconds()

            if result.success:
                agent_result = AgentResult(
                    success=True,
                    agent_name=self.name,
                    capability=AgentCapability.SEARCH,
                    data=result.data.documents,
                    reasoning=f"Retrieved {result.data.count} properties using hybrid search",
                    confidence=0.9,
                    execution_time=execution_time,
                    metadata=result.data.metadata
                )
            else:
                agent_result = AgentResult(
                    success=False,
                    agent_name=self.name,
                    capability=AgentCapability.SEARCH,
                    data=None,
                    reasoning=f"Search failed: {result.error}",
                    confidence=0.0,
                    execution_time=execution_time
                )

            self.record_execution(agent_result)
            return agent_result

        except Exception as e:
            self.logger.error(f"❌ Search error: {e}")
            agent_result = AgentResult(
                success=False,
                agent_name=self.name,
                capability=AgentCapability.SEARCH,
                data=None,
                reasoning=f"Exception: {str(e)}",
                confidence=0.0,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.record_execution(agent_result)
            return agent_result
