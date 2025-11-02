# Test Orchestrator Service

## Overview

Test Orchestrator Service coordinates test execution, manages test plans, and tracks test coverage across the REE AI system. It connects AI Test Agent (query generation) with the actual system (Orchestrator) and Response Evaluator (quality assessment).

**Port**: 8096 (external) / 8080 (internal)

## Features

- **Auto-generate Test Plans**: Create comprehensive test plans covering all intent-persona combinations
- **Custom Test Plans**: Define specific test scenarios
- **Parallel Execution**: Run multiple tests concurrently
- **Coverage Tracking**: Monitor which combinations have been tested
- **Integration**: Connects AI Test Agent → Orchestrator → Response Evaluator

## Workflow

```
1. Generate/Create Test Plan
   └─ Define scenarios (intent × persona × query_count)

2. Execute Test Plan
   └─ For each scenario:
      ├─ Call AI Test Agent to generate queries
      ├─ Send queries to Orchestrator
      ├─ Collect responses
      └─ Call Response Evaluator (optional)

3. Collect Results
   └─ Store results with:
      ├─ Test case details
      ├─ Response data
      ├─ Evaluation scores
      └─ Pass/fail status

4. Generate Reports
   └─ Coverage report
   └─ Test summary
```

## API Endpoints

### Generate Test Plan (Auto)

```bash
POST http://localhost:8096/generate-test-plan
Content-Type: application/json

{
  "plan_type": "comprehensive",
  "queries_per_combination": 5,
  "include_edge_cases": true,
  "parallel_workers": 10
}
```

**Plan Types**:
- `comprehensive`: All intent-persona combinations
- `smoke`: Quick validation tests
- `regression`: Tests for previously found bugs
- `stress`: High-volume performance tests

Returns a test plan with scenarios for all combinations.

### Create Custom Test Plan

```bash
POST http://localhost:8096/create-test-plan
Content-Type: application/json

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
    },
    {
      "scenario_id": "search_investor",
      "persona_type": "experienced_investor",
      "intent": "search",
      "query_count": 10,
      "description": "Search tests for investors"
    }
  ],
  "parallel_workers": 5
}
```

### List Test Plans

```bash
GET http://localhost:8096/test-plans
```

Returns all created test plans.

### Get Test Plan

```bash
GET http://localhost:8096/test-plans/{plan_id}
```

Returns details of a specific test plan.

### Execute Test Plan

```bash
POST http://localhost:8096/execute-test-plan
Content-Type: application/json

{
  "plan_id": "plan_abc123",
  "parallel_workers": 10,
  "evaluate_responses": true
}
```

Executes the test plan and returns results.

Response:
```json
{
  "execution": {
    "plan_id": "plan_abc123",
    "results": [...],
    "total_tests": 100,
    "passed": 85,
    "failed": 12,
    "errors": 3,
    "average_score": 82.5
  },
  "summary": {
    "total": 100,
    "passed": 85,
    "failed": 12,
    "errors": 3,
    "pass_rate": 85.0,
    "average_score": 82.5,
    "execution_time_seconds": 45.2
  }
}
```

### Get Test Execution Results

```bash
GET http://localhost:8096/test-executions/{plan_id}
```

Returns execution results for a completed test plan.

### Get Coverage Report

```bash
GET http://localhost:8096/coverage-report
```

Returns test coverage matrix showing which intent-persona combinations have been tested.

Response:
```json
{
  "coverage": {
    "total_intents": 8,
    "tested_intents": 7,
    "total_personas": 5,
    "tested_personas": 5,
    "coverage_matrix": {
      "search": {
        "first_time_buyer": 10,
        "experienced_investor": 8,
        "young_professional": 12,
        "family_buyer": 5,
        "real_estate_agent": 7
      },
      "compare": {
        "first_time_buyer": 5,
        ...
      }
    },
    "missing_combinations": [
      {"intent": "legal_guidance", "persona": "first_time_buyer"}
    ]
  }
}
```

## Usage Examples

### Example 1: Run Comprehensive Daily Tests

```python
import httpx
import asyncio

async def run_daily_tests():
    async with httpx.AsyncClient() as client:
        # Generate comprehensive test plan
        print("Generating test plan...")
        response = await client.post(
            "http://localhost:8096/generate-test-plan",
            json={
                "plan_type": "comprehensive",
                "queries_per_combination": 3,
                "include_edge_cases": True,
                "parallel_workers": 10
            }
        )
        plan = response.json()["plan"]
        plan_id = plan["plan_id"]

        print(f"Created plan {plan_id} with {plan['total_tests']} tests")

        # Execute test plan
        print("Executing tests...")
        response = await client.post(
            "http://localhost:8096/execute-test-plan",
            json={
                "plan_id": plan_id,
                "evaluate_responses": True
            },
            timeout=300.0  # 5 minutes
        )
        results = response.json()

        # Print summary
        summary = results["summary"]
        print(f"\n=== Test Results ===")
        print(f"Total: {summary['total']}")
        print(f"Passed: {summary['passed']} ({summary['pass_rate']:.1f}%)")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Average Score: {summary['average_score']:.2f}/100")
        print(f"Execution Time: {summary['execution_time_seconds']:.1f}s")

asyncio.run(run_daily_tests())
```

### Example 2: Test Specific Intent

```python
import httpx
import asyncio

async def test_search_intent():
    async with httpx.AsyncClient() as client:
        # Create custom test plan for search intent only
        response = await client.post(
            "http://localhost:8096/create-test-plan",
            json={
                "name": "Search Intent Test",
                "description": "Test search with all personas",
                "scenarios": [
                    {
                        "scenario_id": f"search_{persona}",
                        "persona_type": persona,
                        "intent": "search",
                        "query_count": 5,
                        "description": f"Search test for {persona}"
                    }
                    for persona in [
                        "first_time_buyer",
                        "experienced_investor",
                        "young_professional",
                        "family_buyer",
                        "real_estate_agent"
                    ]
                ],
                "parallel_workers": 5
            }
        )
        plan_id = response.json()["plan"]["plan_id"]

        # Execute
        response = await client.post(
            "http://localhost:8096/execute-test-plan",
            json={"plan_id": plan_id, "evaluate_responses": True}
        )
        print(response.json()["summary"])

asyncio.run(test_search_intent())
```

### Example 3: Check Coverage Gaps

```python
import httpx
import asyncio

async def check_coverage():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8096/coverage-report")
        coverage = response.json()["coverage"]

        print(f"Intent Coverage: {coverage['tested_intents']}/{coverage['total_intents']}")
        print(f"Persona Coverage: {coverage['tested_personas']}/{coverage['total_personas']}")

        if coverage["missing_combinations"]:
            print("\nMissing test combinations:")
            for combo in coverage["missing_combinations"]:
                print(f"  - {combo['intent']} × {combo['persona']}")
        else:
            print("\n✅ Full coverage achieved!")

asyncio.run(check_coverage())
```

## Test Plan Types

### 1. Comprehensive Test Plan
- Tests all intent-persona combinations
- 3-5 queries per combination
- Includes edge cases
- ~150 total tests
- Duration: ~10 minutes

### 2. Smoke Test Plan
- Quick validation of critical paths
- 1 query per combination
- No edge cases
- ~40 total tests
- Duration: ~2 minutes

### 3. Regression Test Plan
- Tests for previously found bugs
- Based on failure history from Learning Service
- Variable query count
- Duration: depends on bug count

### 4. Stress Test Plan
- High-volume testing
- 50+ queries per combination
- Tests system performance under load
- Duration: ~1 hour

## Environment Variables

- `AI_TEST_AGENT_URL`: AI Test Agent URL (default: `http://ai-test-agent:8080`)
- `ORCHESTRATOR_URL`: Orchestrator URL (default: `http://orchestrator:8080`)
- `EVALUATOR_URL`: Response Evaluator URL (default: `http://response-evaluator:8080`)
- `DEBUG`: Enable debug mode (default: `true`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Integration Points

### Upstream Services
- **AI Test Agent** (port 8095): Query generation
- **Orchestrator** (port 8090): System under test
- **Response Evaluator** (port 8097): Response quality evaluation

### Downstream Services
- **Learning Service** (port 8098): Failure tracking
- **PostgreSQL**: Test results storage (future)

## Data Models

### TestPlan
- `plan_id`: Unique identifier
- `name`: Plan name
- `scenarios`: List of test scenarios
- `total_tests`: Total test count
- `status`: pending/running/completed/failed

### TestScenario
- `scenario_id`: Unique identifier
- `persona_type`: User persona
- `intent`: Test intent
- `query_count`: Number of queries to generate

### TestResult
- `test_id`: Unique identifier
- `test_case`: Test case details
- `response`: Orchestrator response
- `evaluation`: Quality scores (if evaluated)
- `status`: passed/failed/error
- `execution_time_ms`: Execution time

## Metrics

Test Orchestrator tracks:
- Total tests executed
- Pass/fail/error counts
- Pass rate percentage
- Average execution time
- Average quality score
- Coverage percentages

## Future Enhancements

- [ ] PostgreSQL integration for persistent storage
- [ ] Real-time test execution monitoring
- [ ] Test result visualization dashboard
- [ ] Scheduled test execution (cron)
- [ ] Test result comparison (trend analysis)
- [ ] Parallel scenario execution
- [ ] Test retry logic for flaky tests
- [ ] Export test results (JSON, CSV, HTML report)

## Related Documentation

- AI Automation System: `/docs/AI_AUTOMATION_TEST_SYSTEM.md`
- AI Test Agent: `/services/ai_test_agent/README.md`
- Models: `models.py`
