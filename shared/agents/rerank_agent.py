"""Rerank Agent - Re-orders search results"""
from typing import Dict, Any
from datetime import datetime
from .base import BaseAgent, AgentRole, AgentCapability, AgentResult
from ..rag_operators.operators import RerankOperator

class RerankAgent(BaseAgent):
    def __init__(self, name: str = "rerank_agent"):
        super().__init__(name=name, role=AgentRole.SPECIALIST, capabilities=[AgentCapability.RERANK])
        self.rerank_op = RerankOperator()

    def can_handle(self, task: Dict[str, Any]) -> bool:
        return task.get("type") == "rerank"

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        start_time = datetime.now()
        try:
            result = await self.rerank_op.safe_execute(task)
            execution_time = (datetime.now() - start_time).total_seconds()
            if result.success:
                agent_result = AgentResult(
                    success=True, agent_name=self.name, capability=AgentCapability.RERANK,
                    data=result.data.reranked_documents,
                    reasoning=f"Reranked {len(result.data.reranked_documents)} documents by relevance",
                    confidence=0.85, execution_time=execution_time, metadata=result.data.metadata
                )
            else:
                agent_result = AgentResult(
                    success=False, agent_name=self.name, capability=AgentCapability.RERANK,
                    data=None, reasoning=f"Reranking failed: {result.error}",
                    confidence=0.0, execution_time=execution_time
                )
            self.record_execution(agent_result)
            return agent_result
        except Exception as e:
            agent_result = AgentResult(
                success=False, agent_name=self.name, capability=AgentCapability.RERANK,
                data=None, reasoning=f"Exception: {str(e)}", confidence=0.0,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.record_execution(agent_result)
            return agent_result
