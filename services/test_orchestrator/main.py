"""
Test Orchestrator Service

This service coordinates test execution, manages test plans,
and tracks test coverage across the REE AI system.

Port: 8096
"""

import sys
import os
import uuid
import asyncio
import httpx
from typing import List, Dict
from datetime import datetime
from fastapi import HTTPException

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_service import BaseService
from models import (
    TestPlan, TestCase, TestResult, TestPlanExecution,
    CreateTestPlanRequest, ExecuteTestPlanRequest, CoverageReport,
    GenerateTestPlanRequest, TestScenario, IntentType
)


class TestOrchestratorService(BaseService):
    """Test Orchestrator Service - Coordinates test execution"""

    def __init__(self):
        super().__init__(
            name="test_orchestrator",
            version="1.0.0",
            capabilities=["test_execution", "test_planning", "coverage_tracking"],
            port=8080  # Internal port, mapped to 8096 externally
        )

        # Service URLs
        self.ai_test_agent_url = os.getenv("AI_TEST_AGENT_URL", "http://ai-test-agent:8080")
        self.orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8080")
        self.evaluator_url = os.getenv("EVALUATOR_URL", "http://response-evaluator:8080")

        # In-memory storage (should be replaced with PostgreSQL in production)
        self.test_plans: Dict[str, TestPlan] = {}
        self.test_executions: Dict[str, TestPlanExecution] = {}
        self.test_cases: Dict[str, TestCase] = {}

        # Available personas (from AI Test Agent)
        self.available_personas = [
            "first_time_buyer",
            "experienced_investor",
            "young_professional",
            "family_buyer",
            "real_estate_agent"
        ]

        # Available intents
        self.available_intents = [intent for intent in IntentType]

    def setup_routes(self):
        """Setup API routes"""

        @self.app.post("/generate-test-plan")
        async def generate_test_plan(request: GenerateTestPlanRequest) -> Dict:
            """
            Auto-generate a comprehensive test plan

            Example:
            ```
            POST /generate-test-plan
            {
                "plan_type": "comprehensive",
                "queries_per_combination": 5,
                "include_edge_cases": true,
                "parallel_workers": 10
            }
            ```

            This generates a test plan covering all intent-persona combinations.
            """
            self.logger.info(f"🎯 Generating {request.plan_type} test plan")

            # Determine which intents and personas to test
            intents = request.intents or self.available_intents
            personas = request.personas or self.available_personas

            # Generate scenarios
            scenarios = []
            for intent in intents:
                for persona in personas:
                    scenario = TestScenario(
                        scenario_id=f"{intent}_{persona}_{uuid.uuid4().hex[:8]}",
                        persona_type=persona,
                        intent=intent,
                        query_count=request.queries_per_combination,
                        description=f"Test {intent} intent with {persona} persona"
                    )
                    scenarios.append(scenario)

            # Add edge cases if requested
            if request.include_edge_cases:
                edge_scenarios = self._generate_edge_case_scenarios()
                scenarios.extend(edge_scenarios)

            # Create test plan
            total_tests = sum(s.query_count for s in scenarios)

            plan = TestPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:12]}",
                name=f"{request.plan_type.title()} Test Plan",
                description=f"Auto-generated {request.plan_type} test plan with {len(scenarios)} scenarios",
                scenarios=scenarios,
                total_tests=total_tests,
                parallel_workers=request.parallel_workers,
                status="pending"
            )

            # Store plan
            self.test_plans[plan.plan_id] = plan

            self.logger.info(f"✅ Generated test plan {plan.plan_id} with {total_tests} tests")

            return {
                "plan": plan.dict(),
                "scenarios_count": len(scenarios),
                "total_tests": total_tests
            }

        @self.app.post("/create-test-plan")
        async def create_test_plan(request: CreateTestPlanRequest) -> Dict:
            """
            Create a custom test plan

            Example:
            ```
            POST /create-test-plan
            {
                "name": "Search Intent Tests",
                "description": "Test search functionality with all personas",
                "scenarios": [
                    {
                        "scenario_id": "search_first_buyer",
                        "persona_type": "first_time_buyer",
                        "intent": "search",
                        "query_count": 10,
                        "description": "Search tests for first-time buyers"
                    }
                ],
                "parallel_workers": 5
            }
            ```
            """
            plan_id = f"plan_{uuid.uuid4().hex[:12]}"

            total_tests = sum(s.query_count for s in request.scenarios)

            plan = TestPlan(
                plan_id=plan_id,
                name=request.name,
                description=request.description,
                scenarios=request.scenarios,
                total_tests=total_tests,
                parallel_workers=request.parallel_workers,
                status="pending"
            )

            self.test_plans[plan_id] = plan

            self.logger.info(f"✅ Created test plan {plan_id} with {total_tests} tests")

            return {"plan": plan.dict()}

        @self.app.get("/test-plans")
        async def list_test_plans() -> Dict:
            """List all test plans"""
            return {
                "plans": [plan.dict() for plan in self.test_plans.values()],
                "count": len(self.test_plans)
            }

        @self.app.get("/test-plans/{plan_id}")
        async def get_test_plan(plan_id: str) -> Dict:
            """Get a specific test plan"""
            if plan_id not in self.test_plans:
                raise HTTPException(status_code=404, detail="Test plan not found")

            return {"plan": self.test_plans[plan_id].dict()}

        @self.app.post("/execute-test-plan")
        async def execute_test_plan(request: ExecuteTestPlanRequest) -> Dict:
            """
            Execute a test plan

            Example:
            ```
            POST /execute-test-plan
            {
                "plan_id": "plan_abc123",
                "parallel_workers": 10,
                "evaluate_responses": true
            }
            ```

            This will:
            1. Generate test queries using AI Test Agent
            2. Send queries to Orchestrator
            3. Collect responses
            4. Evaluate responses (if requested)
            5. Store results
            """
            if request.plan_id not in self.test_plans:
                raise HTTPException(status_code=404, detail="Test plan not found")

            plan = self.test_plans[request.plan_id]

            self.logger.info(f"🚀 Executing test plan {plan.plan_id}: {plan.name}")
            self.logger.info(f"   Scenarios: {len(plan.scenarios)}, Total tests: {plan.total_tests}")

            # Update plan status
            plan.status = "running"

            # Create execution record
            execution = TestPlanExecution(
                plan_id=plan.plan_id,
                plan=plan,
                results=[],
                total_tests=plan.total_tests,
                passed=0,
                failed=0,
                errors=0,
                total_execution_time_ms=0,
                started_at=datetime.now(),
                status="running"
            )

            try:
                # Execute all scenarios
                all_results = []
                for scenario in plan.scenarios:
                    results = await self._execute_scenario(
                        scenario=scenario,
                        evaluate=request.evaluate_responses
                    )
                    all_results.extend(results)

                # Calculate statistics
                execution.results = all_results
                execution.passed = sum(1 for r in all_results if r.status == "passed")
                execution.failed = sum(1 for r in all_results if r.status == "failed")
                execution.errors = sum(1 for r in all_results if r.status == "error")
                execution.total_execution_time_ms = sum(r.execution_time_ms for r in all_results)

                # Calculate average score if evaluation was done
                if request.evaluate_responses:
                    scores = [r.evaluation["overall_score"] for r in all_results if r.evaluation]
                    execution.average_score = sum(scores) / len(scores) if scores else None

                execution.completed_at = datetime.now()
                execution.status = "completed"
                plan.status = "completed"

                self.logger.info(f"✅ Completed test plan {plan.plan_id}")
                self.logger.info(f"   Passed: {execution.passed}/{execution.total_tests}")
                self.logger.info(f"   Failed: {execution.failed}/{execution.total_tests}")
                self.logger.info(f"   Errors: {execution.errors}/{execution.total_tests}")
                if execution.average_score:
                    self.logger.info(f"   Average Score: {execution.average_score:.2f}/100")

                # Store execution
                self.test_executions[plan.plan_id] = execution

                return {
                    "execution": execution.dict(),
                    "summary": {
                        "total": execution.total_tests,
                        "passed": execution.passed,
                        "failed": execution.failed,
                        "errors": execution.errors,
                        "pass_rate": execution.passed / execution.total_tests * 100,
                        "average_score": execution.average_score,
                        "execution_time_seconds": execution.total_execution_time_ms / 1000
                    }
                }

            except Exception as e:
                self.logger.error(f"❌ Test plan execution failed: {e}")
                execution.status = "failed"
                plan.status = "failed"
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/test-executions/{plan_id}")
        async def get_test_execution(plan_id: str) -> Dict:
            """Get execution results for a test plan"""
            if plan_id not in self.test_executions:
                raise HTTPException(status_code=404, detail="Test execution not found")

            return {"execution": self.test_executions[plan_id].dict()}

        @self.app.get("/coverage-report")
        async def get_coverage_report() -> Dict:
            """
            Get test coverage report

            Shows which intent-persona combinations have been tested
            and identifies gaps in test coverage.
            """
            # Build coverage matrix
            coverage_matrix = {}
            for intent in self.available_intents:
                coverage_matrix[intent] = {}
                for persona in self.available_personas:
                    coverage_matrix[intent][persona] = 0

            # Count tests for each combination
            for test_case in self.test_cases.values():
                intent = test_case.intent
                persona = test_case.persona_type
                if intent in coverage_matrix and persona in coverage_matrix[intent]:
                    coverage_matrix[intent][persona] += 1

            # Find missing combinations
            missing = []
            for intent in self.available_intents:
                for persona in self.available_personas:
                    if coverage_matrix[intent][persona] == 0:
                        missing.append({"intent": intent, "persona": persona})

            # Calculate coverage percentages
            tested_intents = sum(1 for intent in coverage_matrix if any(coverage_matrix[intent].values()))
            tested_personas = len(set(
                persona for intent in coverage_matrix
                for persona, count in coverage_matrix[intent].items()
                if count > 0
            ))

            report = CoverageReport(
                total_intents=len(self.available_intents),
                tested_intents=tested_intents,
                total_personas=len(self.available_personas),
                tested_personas=tested_personas,
                coverage_matrix=coverage_matrix,
                missing_combinations=missing,
                edge_cases_covered=0,  # TODO: Track edge cases
                total_edge_cases=10    # TODO: Define edge cases
            )

            return {"coverage": report.dict()}

    async def _execute_scenario(self, scenario: TestScenario, evaluate: bool = True) -> List[TestResult]:
        """Execute a test scenario"""
        self.logger.info(f"📝 Executing scenario: {scenario.description}")

        results = []

        # Generate queries from AI Test Agent
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ai_test_agent_url}/generate-queries",
                json={
                    "persona_type": scenario.persona_type,
                    "intent": scenario.intent,
                    "count": scenario.query_count
                }
            )
            response.raise_for_status()
            generated_queries = response.json()["queries"]

        # Execute each query
        for query_data in generated_queries:
            # Create test case
            test_case = TestCase(
                test_id=f"test_{uuid.uuid4().hex[:12]}",
                scenario_id=scenario.scenario_id,
                persona_type=scenario.persona_type,
                intent=scenario.intent,
                query=query_data["query"],
                expected_entities=query_data["expected_entities"],
                difficulty=query_data["difficulty"],
                tags=query_data["tags"]
            )

            # Store test case
            self.test_cases[test_case.test_id] = test_case

            # Execute test
            result = await self._execute_test_case(test_case, evaluate)
            results.append(result)

        return results

    async def _execute_test_case(self, test_case: TestCase, evaluate: bool = True) -> TestResult:
        """Execute a single test case"""
        start_time = datetime.now()

        try:
            # Send query to Orchestrator
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.orchestrator_url}/orchestrate",
                    json={
                        "user_id": f"test_user_{test_case.persona_type}",
                        "query": test_case.query
                    }
                )
                response.raise_for_status()
                orchestrator_response = response.json()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Evaluate response if requested
            evaluation = None
            if evaluate:
                try:
                    evaluation = await self._evaluate_response(test_case, orchestrator_response)
                except Exception as e:
                    self.logger.warning(f"⚠️ Evaluation failed: {e}")

            # Determine status
            status = "passed"
            error_message = None

            # Check if intent matches
            detected_intent = orchestrator_response.get("intent", "")
            if detected_intent != test_case.intent:
                status = "failed"
                error_message = f"Intent mismatch: expected {test_case.intent}, got {detected_intent}"

            # Check evaluation score
            if evaluation and evaluation["overall_score"] < 70:
                status = "failed"
                if not error_message:
                    error_message = f"Low quality score: {evaluation['overall_score']}/100"

            result = TestResult(
                test_id=test_case.test_id,
                test_case=test_case,
                response=orchestrator_response,
                evaluation=evaluation,
                execution_time_ms=execution_time,
                status=status,
                error_message=error_message
            )

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                test_id=test_case.test_id,
                test_case=test_case,
                response={},
                execution_time_ms=execution_time,
                status="error",
                error_message=str(e)
            )

    async def _evaluate_response(self, test_case: TestCase, response: Dict) -> Dict:
        """Evaluate a response using Response Evaluator Service"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            eval_response = await client.post(
                f"{self.evaluator_url}/evaluate",
                json={
                    "test_case": test_case.dict(),
                    "response": response
                }
            )
            eval_response.raise_for_status()
            return eval_response.json()["evaluation"]

    def _generate_edge_case_scenarios(self) -> List[TestScenario]:
        """Generate edge case test scenarios"""
        edge_scenarios = []

        # Edge case: empty query
        edge_scenarios.append(TestScenario(
            scenario_id=f"edge_empty_{uuid.uuid4().hex[:8]}",
            persona_type="first_time_buyer",
            intent=IntentType.SEARCH,
            query_count=1,
            description="Edge case: empty query"
        ))

        # Edge case: very long query
        edge_scenarios.append(TestScenario(
            scenario_id=f"edge_long_{uuid.uuid4().hex[:8]}",
            persona_type="experienced_investor",
            intent=IntentType.SEARCH,
            query_count=1,
            description="Edge case: very long query"
        ))

        # Edge case: mixed language
        edge_scenarios.append(TestScenario(
            scenario_id=f"edge_mixed_{uuid.uuid4().hex[:8]}",
            persona_type="young_professional",
            intent=IntentType.SEARCH,
            query_count=1,
            description="Edge case: mixed Vietnamese-English query"
        ))

        return edge_scenarios


if __name__ == "__main__":
    service = TestOrchestratorService()
    service.run()
