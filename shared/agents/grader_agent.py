"""
Grader Agent - Evaluates document quality
"""
from typing import Dict, Any
from datetime import datetime

from .base import BaseAgent, AgentRole, AgentCapability, AgentResult
from ..rag_operators.operators import DocumentGraderOperator


class GraderAgent(BaseAgent):
    """Grader Agent - Evaluates document relevance"""

    def __init__(self, name: str = "grader_agent"):
        super().__init__(
            name=name,
            role=AgentRole.CRITIC,
            capabilities=[AgentCapability.GRADE]
        )
        self.grader_op = DocumentGraderOperator()

    def can_handle(self, task: Dict[str, Any]) -> bool:
        return task.get("type") == "grade"

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        start_time = datetime.now()
        self.logger.info(f"🎯 Grading {len(task.get('documents', []))} documents")

        try:
            result = await self.grader_op.safe_execute(task)
            execution_time = (datetime.now() - start_time).total_seconds()

            if result.success:
                agent_result = AgentResult(
                    success=True,
                    agent_name=self.name,
                    capability=AgentCapability.GRADE,
                    data=result.data.graded_documents,
                    reasoning=f"Graded and filtered {result.data.filtered_count} low-quality documents",
                    confidence=0.9,
                    execution_time=execution_time,
                    metadata=result.data.metadata
                )
            else:
                agent_result = AgentResult(
                    success=False,
                    agent_name=self.name,
                    capability=AgentCapability.GRADE,
                    data=None,
                    reasoning=f"Grading failed: {result.error}",
                    confidence=0.0,
                    execution_time=execution_time
                )

            self.record_execution(agent_result)
            return agent_result

        except Exception as e:
            self.logger.error(f"❌ Grading error: {e}")
            agent_result = AgentResult(
                success=False,
                agent_name=self.name,
                capability=AgentCapability.GRADE,
                data=None,
                reasoning=f"Exception: {str(e)}",
                confidence=0.0,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.record_execution(agent_result)
            return agent_result
