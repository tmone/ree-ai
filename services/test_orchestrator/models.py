"""
Data models for Test Orchestrator Service
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class IntentType(str, Enum):
    """Test intent types (matching Orchestrator intents)"""
    SEARCH = "search"
    COMPARE = "compare"
    PRICE_ANALYSIS = "price_analysis"
    INVESTMENT_ADVICE = "investment_advice"
    LOCATION_INSIGHTS = "location_insights"
    LEGAL_GUIDANCE = "legal_guidance"
    CHAT = "chat"
    CLARIFICATION = "clarification"


class TestScenario(BaseModel):
    """Test scenario definition"""
    scenario_id: str
    persona_type: str
    intent: IntentType
    query_count: int = 1
    description: str


class TestPlan(BaseModel):
    """Test plan definition"""
    plan_id: str
    name: str
    description: str
    scenarios: List[TestScenario]
    total_tests: int
    parallel_workers: int = 5
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed


class TestCase(BaseModel):
    """Individual test case"""
    test_id: str
    scenario_id: str
    persona_type: str
    intent: IntentType
    query: str
    expected_entities: Dict[str, any]
    difficulty: str
    tags: List[str]
    created_at: datetime = Field(default_factory=datetime.now)


class TestResult(BaseModel):
    """Test execution result"""
    test_id: str
    test_case: TestCase
    response: Dict[str, any]  # Response from Orchestrator
    evaluation: Optional[Dict[str, any]] = None  # From Evaluator Service
    execution_time_ms: float
    status: str  # passed, failed, error
    error_message: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.now)


class TestPlanExecution(BaseModel):
    """Test plan execution results"""
    plan_id: str
    plan: TestPlan
    results: List[TestResult]
    total_tests: int
    passed: int
    failed: int
    errors: int
    total_execution_time_ms: float
    average_score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # running, completed, failed


class CreateTestPlanRequest(BaseModel):
    """Request to create a test plan"""
    name: str
    description: str
    scenarios: List[TestScenario]
    parallel_workers: int = 5


class ExecuteTestPlanRequest(BaseModel):
    """Request to execute a test plan"""
    plan_id: str
    parallel_workers: Optional[int] = None
    evaluate_responses: bool = True  # Whether to call Evaluator Service


class CoverageReport(BaseModel):
    """Test coverage report"""
    total_intents: int
    tested_intents: int
    total_personas: int
    tested_personas: int
    coverage_matrix: Dict[str, Dict[str, int]]  # intent -> persona -> test_count
    missing_combinations: List[Dict[str, str]]  # Untested combinations
    edge_cases_covered: int
    total_edge_cases: int


class GenerateTestPlanRequest(BaseModel):
    """Request to auto-generate a test plan"""
    plan_type: str = "comprehensive"  # comprehensive, smoke, regression, stress
    intents: Optional[List[IntentType]] = None  # Specific intents to test
    personas: Optional[List[str]] = None  # Specific personas to test
    queries_per_combination: int = 5  # Queries per intent-persona combination
    include_edge_cases: bool = True
    parallel_workers: int = 10
