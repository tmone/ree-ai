## AI Automation Test System - Usage Guide

### Quick Start

This guide shows you how to use the AI-powered automation test system to continuously test and improve REE AI.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [Running Your First Test](#running-your-first-test)
4. [Daily Test Workflow](#daily-test-workflow)
5. [Understanding Results](#understanding-results)
6. [Common Use Cases](#common-use-cases)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## System Overview

The AI Automation Test System consists of 3 main services:

```
┌──────────────────────┐
│  AI Test Agent       │  Generates realistic queries using Ollama
│  Port: 8095          │  Simulates 5 user personas
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Test Orchestrator   │  Coordinates test execution
│  Port: 8096          │  Creates test plans, runs scenarios
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Response Evaluator  │  Evaluates response quality
│  Port: 8097          │  5 dimensions: accuracy, relevance, etc.
└──────────────────────┘
```

---

## Getting Started

### 1. Start Services

```bash
# Start all automation test services
docker compose --profile real up -d ai-test-agent test-orchestrator response-evaluator

# Check services are running
curl http://localhost:8095/health  # AI Test Agent
curl http://localhost:8096/health  # Test Orchestrator
curl http://localhost:8097/health  # Response Evaluator
```

### 2. Initialize Database

```bash
# Run database migration
docker exec -i ree-ai-postgres psql -U ree_ai_user -d ree_ai < database/schemas/ai_automation_test.sql
```

### 3. Verify Setup

```bash
# Check Ollama connection (for AI Test Agent)
curl http://localhost:8095/test-ollama

# List available personas
curl http://localhost:8095/personas

# Get evaluation metrics
curl http://localhost:8097/evaluation-metrics
```

---

## Running Your First Test

### Step 1: Generate a Test Query

```bash
curl -X POST http://localhost:8095/generate-query \
  -H "Content-Type: application/json" \
  -d '{
    "persona_type": "first_time_buyer",
    "intent": "search"
  }'
```

**Response:**
```json
{
  "query": {
    "query": "Tìm căn hộ 2 phòng ngủ giá dưới 3 tỷ Quận 7",
    "persona_type": "first_time_buyer",
    "intent": "search",
    "expected_entities": {
      "bedrooms": 2,
      "price_max": 3000000000,
      "location": "quận 7"
    },
    "difficulty": "medium"
  }
}
```

### Step 2: Send Query to System

```bash
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "Tìm căn hộ 2 phòng ngủ giá dưới 3 tỷ Quận 7"
  }'
```

### Step 3: Evaluate Response

```bash
curl -X POST http://localhost:8097/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "test_case": {
      "query": "Tìm căn hộ 2 phòng ngủ giá dưới 3 tỷ Quận 7",
      "intent": "search",
      "expected_entities": {
        "bedrooms": 2,
        "price_max": 3000000000,
        "location": "quận 7"
      }
    },
    "response": {
      "intent": "search",
      "response": "..."
    },
    "execution_time_ms": 1500
  }'
```

**Response:**
```json
{
  "evaluation": {
    "accuracy": 90.0,
    "relevance": 95.0,
    "completeness": 85.0,
    "coherence": 92.0,
    "latency": 100.0,
    "overall_score": 91.15
  }
}
```

✅ **Overall Score ≥ 70**: Test PASSED
❌ **Overall Score < 70**: Test FAILED

---

## Daily Test Workflow

### Automated Daily Tests

Create a Python script for daily testing:

```python
# daily_tests.py
import httpx
import asyncio
from datetime import datetime

async def run_daily_tests():
    async with httpx.AsyncClient() as client:
        print(f"🚀 Starting daily tests - {datetime.now()}")

        # 1. Generate comprehensive test plan
        print("\n📝 Generating test plan...")
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

        print(f"✅ Created plan {plan_id}: {plan['total_tests']} tests")

        # 2. Execute test plan
        print(f"\n🏃 Executing {plan['total_tests']} tests...")
        response = await client.post(
            "http://localhost:8096/execute-test-plan",
            json={
                "plan_id": plan_id,
                "evaluate_responses": True
            },
            timeout=600.0  # 10 minutes
        )
        results = response.json()

        # 3. Print summary
        summary = results["summary"]
        print(f"\n{'='*50}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total Tests:    {summary['total']}")
        print(f"Passed:         {summary['passed']} ({summary['pass_rate']:.1f}%)")
        print(f"Failed:         {summary['failed']}")
        print(f"Errors:         {summary['errors']}")
        print(f"Average Score:  {summary['average_score']:.2f}/100")
        print(f"Execution Time: {summary['execution_time_seconds']:.1f}s")
        print(f"{'='*50}")

        # 4. Check pass rate
        if summary['pass_rate'] < 90:
            print(f"\n⚠️ WARNING: Pass rate below 90%!")
            print("Review failed tests and fix issues.")
            return 1
        else:
            print(f"\n✅ All tests passed! System is healthy.")
            return 0

if __name__ == "__main__":
    exit_code = asyncio.run(run_daily_tests())
    exit(exit_code)
```

**Run daily:**
```bash
python daily_tests.py
```

**Schedule with cron:**
```bash
# Run every day at 8 AM
0 8 * * * cd /path/to/ree-ai && python daily_tests.py >> logs/daily_tests.log 2>&1
```

---

## Understanding Results

### Test Result Structure

```json
{
  "test_id": "test_abc123",
  "query": "Tìm căn hộ 2PN Quận 7",
  "intent": "search",
  "persona_type": "first_time_buyer",
  "response": {
    "intent": "search",
    "response": "Đây là các căn hộ 2PN...",
    "properties": [...]
  },
  "evaluation": {
    "accuracy": 90.0,
    "relevance": 95.0,
    "completeness": 85.0,
    "coherence": 92.0,
    "latency": 100.0,
    "overall_score": 91.15
  },
  "status": "passed",
  "execution_time_ms": 1234.5
}
```

### Evaluation Scores Explained

| Dimension | What It Measures | Pass Threshold |
|-----------|------------------|----------------|
| **Accuracy** | Correctness of information, intent, entities | ≥ 80 |
| **Relevance** | How well response addresses query | ≥ 80 |
| **Completeness** | All required info provided | ≥ 75 |
| **Coherence** | Language quality, structure | ≥ 85 |
| **Latency** | Response time performance | ≥ 80 (< 5s) |
| **Overall** | Weighted average | ≥ 70 |

### Common Failure Patterns

#### 1. Intent Mismatch
```json
{
  "failure_type": "intent_mismatch",
  "expected_intent": "compare",
  "actual_intent": "search",
  "root_cause": "Keyword 'so sánh' not detected"
}
```

**Fix**: Add "so sánh" to COMPARE intent keywords

#### 2. Entity Extraction Error
```json
{
  "failure_type": "entity_extraction",
  "expected_entities": {"bedrooms": 2},
  "actual_entities": {},
  "root_cause": "Pattern '2 phòng ngủ' not matched"
}
```

**Fix**: Update entity extraction regex

#### 3. Low Quality Score
```json
{
  "failure_type": "low_quality",
  "overall_score": 65.0,
  "weak_dimensions": ["completeness", "coherence"],
  "root_cause": "Response too brief, lacks details"
}
```

**Fix**: Improve prompt to generate more detailed responses

---

## Common Use Cases

### Use Case 1: Test Specific Intent

```bash
# Test only search intent with all personas
curl -X POST http://localhost:8096/generate-test-plan \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "smoke",
    "intents": ["search"],
    "queries_per_combination": 5,
    "parallel_workers": 5
  }'
```

### Use Case 2: Regression Testing

After fixing a bug, test that it stays fixed:

```bash
# Generate regression test plan
curl -X POST http://localhost:8096/generate-test-plan \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "regression",
    "include_edge_cases": true
  }'
```

### Use Case 3: Performance Testing

Test system under load:

```bash
# Stress test with many parallel queries
curl -X POST http://localhost:8096/generate-test-plan \
  -H "Content-Type: application/json" \
  -d '{
    "plan_type": "stress",
    "queries_per_combination": 50,
    "parallel_workers": 20
  }'
```

### Use Case 4: Check Coverage Gaps

```bash
# Get coverage report
curl http://localhost:8096/coverage-report

# Response shows missing combinations
{
  "coverage": {
    "missing_combinations": [
      {"intent": "legal_guidance", "persona": "first_time_buyer"},
      {"intent": "location_insights", "persona": "young_professional"}
    ]
  }
}
```

### Use Case 5: Monitor Daily Performance

```python
# Get daily statistics
import httpx

async def check_daily_stats():
    async with httpx.AsyncClient() as client:
        # Get evaluation stats
        response = await client.get("http://localhost:8097/stats")
        stats = response.json()["statistics"]

        print(f"Today's Performance:")
        print(f"  Average Score: {stats['overall_score']['average']:.2f}")
        print(f"  Total Evaluations: {stats['overall_score']['count']}")

        # Get test plan summary
        response = await client.get("http://localhost:8096/test-plans")
        plans = response.json()["plans"]

        today_plans = [p for p in plans if p['status'] == 'completed']
        print(f"  Tests Run: {sum(p['total_tests'] for p in today_plans)}")
```

---

## Troubleshooting

### Issue 1: Ollama Not Available

**Symptom**: AI Test Agent returns fallback queries

**Check**:
```bash
curl http://localhost:8095/test-ollama
```

**Fix**:
```bash
# Start Ollama
docker compose up -d ollama

# Pull required model
docker exec -it ree-ai-ollama ollama pull llama2
```

### Issue 2: Services Not Communicating

**Symptom**: Test Orchestrator can't reach AI Test Agent

**Check**:
```bash
# Check Docker network
docker network inspect ree-ai-network

# Check service logs
docker logs ree-ai-test-orchestrator
```

**Fix**:
```bash
# Restart services
docker compose restart ai-test-agent test-orchestrator
```

### Issue 3: Low Pass Rates

**Symptom**: Only 60% tests passing

**Steps**:
1. Check which intents are failing:
```sql
SELECT intent, COUNT(*), AVG(overall_score)
FROM test_results
WHERE status = 'failed'
GROUP BY intent
ORDER BY COUNT(*) DESC;
```

2. Check common failure patterns:
```bash
curl http://localhost:8096/failure-patterns
```

3. Fix identified issues and re-run tests

### Issue 4: Slow Test Execution

**Symptom**: Tests taking > 10 minutes

**Optimization**:
```bash
# Increase parallel workers
curl -X POST http://localhost:8096/execute-test-plan \
  -d '{"plan_id": "...", "parallel_workers": 20}'

# Reduce queries per combination
curl -X POST http://localhost:8096/generate-test-plan \
  -d '{"queries_per_combination": 2}'
```

---

## Best Practices

### 1. Daily Testing Schedule

```
Morning (8 AM):   Comprehensive test (150 tests)
Afternoon (2 PM): Smoke test (40 tests)
Evening (8 PM):   Regression test (varies)
```

### 2. Test Plan Strategy

- **Comprehensive**: Full coverage, run daily
- **Smoke**: Quick validation after deploy
- **Regression**: After bug fixes
- **Stress**: Weekly performance check

### 3. Monitoring Thresholds

Set alerts for:
- Pass rate < 90%
- Average score < 80
- Latency P95 > 5s
- New failure pattern detected

### 4. Continuous Improvement

Weekly review:
1. Identify top 5 failure patterns
2. Fix patterns
3. Generate regression tests
4. Verify fixes
5. Document improvements

### 5. Database Maintenance

```sql
-- Archive old test results (keep last 30 days)
DELETE FROM test_results
WHERE executed_at < NOW() - INTERVAL '30 days';

-- Vacuum to reclaim space
VACUUM ANALYZE test_results;
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/ai-tests.yml
name: AI Automation Tests

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Services
        run: |
          docker compose --profile real up -d
          sleep 60  # Wait for services

      - name: Run Tests
        run: python daily_tests.py

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: logs/daily_tests.log
```

---

## Next Steps

1. **Learn More**:
   - Read [AI Automation System Design](/docs/AI_AUTOMATION_TEST_SYSTEM.md)
   - Check service READMEs for API details

2. **Customize**:
   - Add custom personas in `personas.py`
   - Adjust evaluation weights in `evaluators.py`
   - Create custom test scenarios

3. **Scale**:
   - Add more parallel workers
   - Implement distributed testing
   - Set up monitoring dashboard

---

## Support

- **Documentation**: `/docs/AI_AUTOMATION_TEST_SYSTEM.md`
- **API Docs**:
  - http://localhost:8095/docs (AI Test Agent)
  - http://localhost:8096/docs (Test Orchestrator)
  - http://localhost:8097/docs (Response Evaluator)

---

**Happy Testing! 🚀**
