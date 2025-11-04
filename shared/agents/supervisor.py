"""
Supervisor Agent
Coordinates and delegates tasks to specialist agents
"""
from typing import Dict, Any, List
from datetime import datetime
import asyncio

from .base import BaseAgent, AgentRole, AgentCapability, AgentResult, AgentMessage
from .search_agent import SearchAgent
from .grader_agent import GraderAgent
from .rerank_agent import RerankAgent
from .critique_agent import CritiqueAgent


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent

    Implements CTO's Supervisor Pattern:
    - Decomposes complex tasks
    - Delegates to specialist agents
    - Monitors execution
    - Synthesizes results
    """

    def __init__(self, name: str = "supervisor"):
        super().__init__(
            name=name,
            role=AgentRole.SUPERVISOR,
            capabilities=list(AgentCapability)  # Has all capabilities through delegation
        )

        # Initialize specialist agents
        self.agents: Dict[str, BaseAgent] = {
            "search": SearchAgent(),
            "grader": GraderAgent(),
            "reranker": RerankAgent(),
            "critique": CritiqueAgent()
        }

        self.logger.info(f"👨‍💼 Supervisor initialized with {len(self.agents)} specialist agents")

    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Supervisor can handle any task by delegating"""
        return True

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute task with multi-agent coordination

        Workflow:
        1. Search Agent retrieves properties
        2. Grader Agent filters low-quality results
        3. Reranker Agent re-orders by relevance
        4. Critique Agent evaluates quality

        If quality is low, may trigger retry with Query Rewriter
        """
        start_time = datetime.now()

        self.logger.info(f"👨‍💼 Supervisor orchestrating task: {task.get('type', 'unknown')}")

        try:
            # Step 1: Search
            search_task = {
                "type": "search",
                "query": task.get("query"),
                "filters": task.get("filters", {}),
                "limit": task.get("limit", 10)
            }

            search_result = await self.agents["search"].execute(search_task)

            if not search_result.success or not search_result.data:
                return AgentResult(
                    success=False,
                    agent_name=self.name,
                    capability=AgentCapability.EXECUTE,
                    data=None,
                    reasoning="Search failed, no results to process",
                    confidence=0.0,
                    execution_time=(datetime.now() - start_time).total_seconds()
                )

            # Step 2: Grade
            grade_task = {
                "type": "grade",
                "query": task.get("query"),
                "documents": search_result.data,
                "threshold": 0.5
            }

            grade_result = await self.agents["grader"].execute(grade_task)

            if not grade_result.success:
                self.logger.warning("⚠️  Grading failed, proceeding with unfiltered results")
                documents_after_grading = search_result.data
            else:
                documents_after_grading = grade_result.data

            # Step 3: Rerank
            rerank_task = {
                "type": "rerank",
                "query": task.get("query"),
                "documents": documents_after_grading,
                "top_k": min(5, len(documents_after_grading))
            }

            rerank_result = await self.agents["reranker"].execute(rerank_task)

            if not rerank_result.success:
                self.logger.warning("⚠️  Reranking failed, using graded results")
                final_documents = documents_after_grading
            else:
                final_documents = rerank_result.data

            # Step 4: Critique
            critique_task = {
                "type": "critique",
                "query": task.get("query"),
                "results": final_documents
            }

            critique_result = await self.agents["critique"].execute(critique_task)

            quality_score = critique_result.data.get("quality_score", 0.5) if critique_result.success else 0.5

            execution_time = (datetime.now() - start_time).total_seconds()

            # Synthesize final result
            agent_result = AgentResult(
                success=True,
                agent_name=self.name,
                capability=AgentCapability.EXECUTE,
                data=final_documents,
                reasoning=f"Multi-agent pipeline completed: {len(final_documents)} high-quality results",
                confidence=quality_score,
                execution_time=execution_time,
                metadata={
                    "search_count": len(search_result.data),
                    "graded_count": len(documents_after_grading),
                    "final_count": len(final_documents),
                    "quality_score": quality_score,
                    "agent_pipeline": ["search", "grader", "reranker", "critique"]
                }
            )

            self.record_execution(agent_result)

            # Log agent stats
            self.logger.info(f"📊 Supervisor Stats:")
            for agent_name, agent in self.agents.items():
                stats = agent.get_execution_stats()
                if stats["total_executions"] > 0:
                    self.logger.info(
                        f"   {agent_name}: {stats['total_executions']} tasks, "
                        f"{stats['success_rate']:.1%} success rate"
                    )

            return agent_result

        except Exception as e:
            self.logger.error(f"❌ Supervisor error: {e}")
            agent_result = AgentResult(
                success=False,
                agent_name=self.name,
                capability=AgentCapability.EXECUTE,
                data=None,
                reasoning=f"Exception during multi-agent execution: {str(e)}",
                confidence=0.0,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.record_execution(agent_result)
            return agent_result

    async def delegate_task(
        self,
        agent_name: str,
        task: Dict[str, Any]
    ) -> AgentResult:
        """
        Delegate specific task to specialist agent

        Args:
            agent_name: Name of specialist agent
            task: Task specification

        Returns:
            AgentResult from specialist
        """
        if agent_name not in self.agents:
            return AgentResult(
                success=False,
                agent_name=self.name,
                capability=AgentCapability.EXECUTE,
                data=None,
                reasoning=f"Unknown agent: {agent_name}",
                confidence=0.0
            )

        agent = self.agents[agent_name]

        # Send message to agent
        await self.send_message(
            to_agent=agent.name,
            content=f"Delegating task: {task.get('type')}",
            data=task,
            message_type="request"
        )

        # Execute task
        result = await agent.execute(task)

        return result

    def get_all_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents"""
        stats = {
            "supervisor": self.get_execution_stats()
        }

        for agent_name, agent in self.agents.items():
            stats[agent_name] = agent.get_execution_stats()

        return stats
