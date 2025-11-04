"""
Multi-Agent System
Implements CTO's Multi-Agent Architecture

Agents:
- Supervisor: Coordinates and delegates tasks
- SearchAgent: Specialized in property search
- GraderAgent: Evaluates document quality
- RerankAgent: Re-orders results
- CritiqueAgent: Self-reflection and improvement
"""
from .base import BaseAgent, AgentMessage, AgentRole, AgentCapability
from .supervisor import SupervisorAgent
from .search_agent import SearchAgent
from .grader_agent import GraderAgent
from .rerank_agent import RerankAgent
from .critique_agent import CritiqueAgent

__all__ = [
    'BaseAgent',
    'AgentMessage',
    'AgentRole',
    'AgentCapability',
    'SupervisorAgent',
    'SearchAgent',
    'GraderAgent',
    'RerankAgent',
    'CritiqueAgent'
]
