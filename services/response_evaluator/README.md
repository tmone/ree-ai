# Response Evaluator Service

## Overview

Response Evaluator Service assesses the quality of system responses using multiple evaluation dimensions. It provides objective, quantitative scores to measure response quality and identify areas for improvement.

**Port**: 8097 (external) / 8080 (internal)

## Evaluation Dimensions

### 1. Accuracy (30% weight)
Evaluates correctness of information:
- ✅ Property details match database
- ✅ Intent detection is correct
- ✅ Entity extraction is accurate
- ✅ Calculations are correct (price per m², ROI, etc.)

**Scoring**:
- 100: All information correct
- 80-99: Minor inaccuracies
- 60-79: Some incorrect information
- <60: Major inaccuracies

### 2. Relevance (30% weight)
Evaluates how well response addresses the query:
- ✅ Response answers the query
- ✅ Suggested properties match filters
- ✅ Semantic similarity to query (uses LLM)
- ✅ No off-topic content

**Scoring**:
- 100: Perfectly relevant
- 80-99: Mostly relevant
- 60-79: Partially relevant
- <60: Mostly irrelevant

### 3. Completeness (20% weight)
Evaluates whether all required information is provided:
- ✅ All query requirements addressed
- ✅ Sources cited
- ✅ Sufficient detail level
- ✅ Alternatives mentioned (when applicable)

**Intent-specific requirements**:
- **Search**: Properties, locations, prices
- **Compare**: Differences, pros/cons, recommendation
- **Price Analysis**: Price range, market context, justification
- **Investment Advice**: ROI, risks, timeframe

### 4. Coherence (15% weight)
Evaluates response structure and language quality:
- ✅ Well-structured sentences
- ✅ Natural language flow
- ✅ No contradictions
- ✅ Proper formatting
- ✅ No excessive repetition

### 5. Latency (5% weight)
Evaluates response time:
- 100 points: 0-2 seconds (excellent)
- 80 points: 2-5 seconds (good)
- 50 points: 5-10 seconds (acceptable)
- 0-50 points: >10 seconds (poor)

## Overall Score Calculation

```
Overall Score = (Accuracy × 0.30) +
                (Relevance × 0.30) +
                (Completeness × 0.20) +
                (Coherence × 0.15) +
                (Latency × 0.05)
```

**Grade Scale**:
- 90-100: Excellent ⭐⭐⭐⭐⭐
- 80-89: Good ⭐⭐⭐⭐
- 70-79: Acceptable ⭐⭐⭐
- 60-69: Needs Improvement ⭐⭐
- 0-59: Failed ⭐

**Passing Score**: 70

## API Endpoints

### Evaluate Single Response

```bash
POST http://localhost:8097/evaluate
Content-Type: application/json

{
  "test_case": {
    "query": "Tìm căn hộ 2 phòng ngủ Quận 7",
    "intent": "search",
    "expected_entities": {
      "bedrooms": 2,
      "location": "quận 7",
      "property_type": "apartment"
    }
  },
  "response": {
    "intent": "search",
    "response": "Đây là các căn hộ 2 phòng ngủ ở Quận 7:\n\n1. Căn hộ Sunrise City - 2PN, 70m², giá 3.5 tỷ\n2. Căn hộ Sky Garden - 2PN, 75m², giá 3.8 tỷ",
    "properties": [
      {"property_id": "123", "title": "Sunrise City", "bedrooms": 2, "price": 3500000000},
      {"property_id": "456", "title": "Sky Garden", "bedrooms": 2, "price": 3800000000}
    ],
    "entities": {
      "bedrooms": 2,
      "location": "quận 7"
    }
  },
  "execution_time_ms": 1234.5
}
```

Response:
```json
{
  "evaluation": {
    "accuracy": 90.0,
    "relevance": 95.0,
    "completeness": 85.0,
    "coherence": 92.0,
    "latency": 100.0,
    "overall_score": 91.15,
    "weights": {
      "accuracy": 0.30,
      "relevance": 0.30,
      "completeness": 0.20,
      "coherence": 0.15,
      "latency": 0.05
    }
  }
}
```

### Batch Evaluate

```bash
POST http://localhost:8097/batch-evaluate
Content-Type: application/json

{
  "evaluations": [
    {
      "test_case": {...},
      "response": {...},
      "execution_time_ms": 1234.5
    },
    {
      "test_case": {...},
      "response": {...},
      "execution_time_ms": 2345.6
    }
  ]
}
```

Returns individual results plus aggregated statistics.

### Get Evaluation Metrics

```bash
GET http://localhost:8097/evaluation-metrics
```

Returns detailed information about evaluation methodology, dimensions, weights, and scoring criteria.

### Get Statistics

```bash
GET http://localhost:8097/stats
```

Returns running statistics of all evaluations performed:
```json
{
  "total_evaluations": 150,
  "statistics": {
    "accuracy": {
      "average": 85.3,
      "min": 60.0,
      "max": 100.0,
      "count": 150
    },
    "relevance": {
      "average": 88.7,
      "min": 65.0,
      "max": 100.0,
      "count": 150
    },
    "overall_score": {
      "average": 84.2,
      "min": 62.5,
      "max": 98.0,
      "count": 150
    }
  }
}
```

### Reset Statistics

```bash
POST http://localhost:8097/reset-stats
```

Resets all accumulated statistics (useful for testing).

## Usage Examples

### Example 1: Evaluate Test Response

```python
import httpx
import asyncio

async def evaluate_response():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8097/evaluate",
            json={
                "test_case": {
                    "query": "Tìm căn hộ giá dưới 3 tỷ Quận 7",
                    "intent": "search",
                    "expected_entities": {
                        "price_max": 3000000000,
                        "location": "quận 7"
                    }
                },
                "response": {
                    "intent": "search",
                    "response": "Tôi tìm thấy 5 căn hộ giá dưới 3 tỷ ở Quận 7...",
                    "properties": [...]
                },
                "execution_time_ms": 1500.0
            }
        )

        result = response.json()
        evaluation = result["evaluation"]

        print(f"Overall Score: {evaluation['overall_score']}/100")
        print(f"  - Accuracy: {evaluation['accuracy']}/100")
        print(f"  - Relevance: {evaluation['relevance']}/100")
        print(f"  - Completeness: {evaluation['completeness']}/100")
        print(f"  - Coherence: {evaluation['coherence']}/100")
        print(f"  - Latency: {evaluation['latency']}/100")

        if evaluation['overall_score'] >= 70:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")

asyncio.run(evaluate_response())
```

### Example 2: Batch Evaluation

```python
import httpx
import asyncio

async def batch_evaluate():
    # Prepare multiple evaluations
    evaluations = []
    for i in range(10):
        evaluations.append({
            "test_case": {"query": f"Test query {i}", "intent": "search"},
            "response": {"response": f"Response {i}..."},
            "execution_time_ms": 1000 + i * 100
        })

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8097/batch-evaluate",
            json={"evaluations": evaluations}
        )

        result = response.json()
        print(f"Total: {result['total']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
        print(f"Average Score: {result['aggregated']['overall_score']:.2f}/100")

asyncio.run(batch_evaluate())
```

### Example 3: Integration with Test Orchestrator

```python
# This is how Test Orchestrator calls Response Evaluator

async def execute_test_with_evaluation(test_case):
    # 1. Send query to Orchestrator
    start_time = time.time()
    orchestrator_response = await send_to_orchestrator(test_case["query"])
    execution_time = (time.time() - start_time) * 1000

    # 2. Evaluate response
    evaluation_response = await httpx.post(
        "http://response-evaluator:8080/evaluate",
        json={
            "test_case": test_case,
            "response": orchestrator_response,
            "execution_time_ms": execution_time
        }
    )

    evaluation = evaluation_response.json()["evaluation"]

    # 3. Determine pass/fail
    passed = evaluation["overall_score"] >= 70

    return {
        "test_case": test_case,
        "response": orchestrator_response,
        "evaluation": evaluation,
        "passed": passed
    }
```

## Evaluation Process

```
┌─────────────────────────────────────────────────────┐
│  1. Receive Evaluation Request                      │
│     - Test case (query, intent, expected entities)  │
│     - System response                               │
│     - Execution time                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  2. Accuracy Evaluation                             │
│     - Check intent detection                        │
│     - Verify entity extraction                      │
│     - Validate property details vs. database        │
│     - Check calculations                            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  3. Relevance Evaluation                            │
│     - Use LLM to assess semantic relevance          │
│     - Fallback: Keyword matching                    │
│     - Check if response addresses query             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  4. Completeness Evaluation                         │
│     - Check intent-specific requirements            │
│     - Verify all required info provided             │
│     - Check for citations/sources                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  5. Coherence Evaluation                            │
│     - Check sentence structure                      │
│     - Assess language fluency                       │
│     - Check for repetition/contradictions           │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  6. Latency Evaluation                              │
│     - Score based on execution time                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  7. Calculate Overall Score                         │
│     - Weighted average of all dimensions            │
│     - Return detailed breakdown                     │
└─────────────────────────────────────────────────────┘
```

## Environment Variables

- `DB_GATEWAY_URL`: DB Gateway URL (default: `http://db-gateway:8080`)
- `CORE_GATEWAY_URL`: Core Gateway URL (default: `http://core-gateway:8080`)
- `DEBUG`: Enable debug mode (default: `true`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Integration Points

### Upstream Services
- **Test Orchestrator** (port 8096): Sends evaluation requests
- **DB Gateway** (port 8081): Verify property accuracy
- **Core Gateway** (port 8080): LLM for relevance evaluation

### Downstream Services
- **Learning Service** (port 8098): Failed evaluations feed into learning

## Evaluation Strategies

### For Different Intents

**Search Intent**:
- Must return properties
- Must include locations and prices
- Entities must match query filters

**Compare Intent**:
- Must mention differences
- Should include pros/cons
- Should provide recommendation

**Price Analysis**:
- Must discuss prices
- Should provide market context
- Should justify price assessment

**Investment Advice**:
- Must mention ROI or returns
- Should discuss risks
- Should provide timeframe

## Future Enhancements

- [ ] Support for custom evaluation criteria
- [ ] A/B test evaluation (compare 2 responses)
- [ ] Historical trend analysis
- [ ] Evaluation explanations (why score was given)
- [ ] User satisfaction correlation
- [ ] Multi-language evaluation
- [ ] Custom weight configuration

## Related Documentation

- AI Automation System: `/docs/AI_AUTOMATION_TEST_SYSTEM.md`
- Test Orchestrator: `/services/test_orchestrator/README.md`
- Evaluators Module: `evaluators.py`
