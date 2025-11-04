"""Critique Agent - Self-reflection and quality assessment"""
from typing import Dict, Any
from datetime import datetime
from .base import BaseAgent, AgentRole, AgentCapability, AgentResult

class CritiqueAgent(BaseAgent):
    def __init__(self, name: str = "critique_agent"):
        super().__init__(name=name, role=AgentRole.CRITIC, capabilities=[AgentCapability.CRITIQUE])

    def can_handle(self, task: Dict[str, Any]) -> bool:
        return task.get("type") == "critique"

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """Evaluate quality of results and suggest improvements"""
        start_time = datetime.now()

        results = task.get("results", [])
        original_query = task.get("query", "")

        # Quality checks
        issues = []
        suggestions = []

        if len(results) < 3:
            issues.append("Too few results")
            suggestions.append("Consider rewriting query or relaxing filters")

        avg_relevance = sum(r.get("relevance_score", 0.5) for r in results) / len(results) if results else 0
        if avg_relevance < 0.5:
            issues.append("Low average relevance")
            suggestions.append("Query rewriting recommended")

        quality_score = 1.0 - (len(issues) * 0.2)

        agent_result = AgentResult(
            success=True, agent_name=self.name, capability=AgentCapability.CRITIQUE,
            data={"quality_score": quality_score, "issues": issues, "suggestions": suggestions},
            reasoning=f"Quality assessment: {len(issues)} issues found, score: {quality_score:.2f}",
            confidence=0.8, execution_time=(datetime.now() - start_time).total_seconds(),
            metadata={"issue_count": len(issues), "suggestion_count": len(suggestions)}
        )

        self.record_execution(agent_result)
        return agent_result
