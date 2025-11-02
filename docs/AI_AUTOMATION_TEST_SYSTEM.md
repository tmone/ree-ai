# AI-Powered Automation Test System

## Overview

This document describes the architecture and implementation of REE AI's intelligent automation test system. The system uses AI (Ollama) to simulate real users, automatically generate test scenarios, evaluate response quality, learn from failures, and continuously improve the product.

## System Goals

1. **Autonomous Testing**: AI acts as end users, generating realistic queries
2. **Quality Evaluation**: Multi-dimensional scoring of system responses
3. **Continuous Learning**: Track failures, analyze patterns, auto-generate regression tests
4. **Self-Improvement**: Automatically suggest and apply fixes to improve response quality
5. **Zero Manual Intervention**: System runs 24/7, detecting and fixing issues autonomously

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   AI AUTOMATION TEST SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

Layer 1: AI Test Agent Layer
┌──────────────────────────────────────────────────────────────────┐
│  AI Test Agent Service (port 8095)                               │
│  - Persona Simulator (Buyer, Investor, Agent, First-timer)      │
│  - Query Generator (Vietnamese natural language)                 │
│  - Conversation Flow Manager (multi-turn interactions)           │
└──────────────────────────────────────────────────────────────────┘

Layer 2: Test Orchestration Layer
┌──────────────────────────────────────────────────────────────────┐
│  Test Orchestrator Service (port 8096)                           │
│  - Test Plan Generator                                           │
│  - Scenario Executor                                             │
│  - Parallel Test Runner                                          │
│  - Test Coverage Tracker                                         │
└──────────────────────────────────────────────────────────────────┘

Layer 3: Evaluation Layer
┌──────────────────────────────────────────────────────────────────┐
│  Response Evaluator Service (port 8097)                          │
│  - Accuracy Scorer                                               │
│  - Relevance Scorer                                              │
│  - Completeness Scorer                                           │
│  - Coherence Scorer                                              │
│  - Semantic Similarity Checker                                   │
│  - Factual Consistency Checker                                   │
└──────────────────────────────────────────────────────────────────┘

Layer 4: Learning Layer
┌──────────────────────────────────────────────────────────────────┐
│  Learning Service (port 8098)                                    │
│  - Failure Database (PostgreSQL)                                 │
│  - Pattern Analyzer                                              │
│  - Regression Test Generator                                     │
│  - Trend Analyzer                                                │
│  - Root Cause Identifier                                         │
└──────────────────────────────────────────────────────────────────┘

Layer 5: Improvement Layer
┌──────────────────────────────────────────────────────────────────┐
│  Improvement Service (port 8099)                                 │
│  - Prompt Optimizer                                              │
│  - Parameter Tuner                                               │
│  - A/B Testing Framework                                         │
│  - Auto-Fix Engine                                               │
└──────────────────────────────────────────────────────────────────┘

Layer 6: Monitoring & Visualization
┌──────────────────────────────────────────────────────────────────┐
│  Test Dashboard (port 3002)                                      │
│  - Real-time Metrics                                             │
│  - Failure Trends                                                │
│  - Improvement Suggestions                                       │
│  - Test Coverage Heatmap                                         │
└──────────────────────────────────────────────────────────────────┘

Storage Layer
┌──────────────────────────────────────────────────────────────────┐
│  PostgreSQL: test_results, failures, patterns, improvements      │
│  Redis: test_cache, real-time_metrics                            │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. AI Test Agent Service (Port 8095)

**Purpose**: Simulate real users using AI to generate test queries and conversations

**Key Features**:
- **Persona Simulation**: Different user types with specific behaviors
  - `first_time_buyer`: Inexperienced, asks basic questions, uses simple language
  - `experienced_investor`: Knowledgeable, asks complex questions about ROI, legal, market trends
  - `young_professional`: Budget-conscious, location-focused (near office, transport)
  - `family_buyer`: Needs schools, parks, safety, space
  - `real_estate_agent`: Professional queries, comparison, market insights

- **Query Generation**: Uses Ollama to generate realistic Vietnamese queries
  ```python
  # Examples generated by AI:
  "Tìm căn hộ giá dưới 3 tỷ gần trường quốc tế quận 7"
  "Đầu tư vào khu Nam Sài Gòn có tiềm năng không?"
  "So sánh 2 căn hộ: Vinhomes Grand Park vs Masteri Thảo Điền"
  ```

- **Conversation Flow Management**: Multi-turn conversations
  ```
  Turn 1: "Tìm căn hộ 2 phòng ngủ quận 2"
  Turn 2: "Giá khoảng bao nhiêu?"
  Turn 3: "Có gần trường học không?"
  Turn 4: "So sánh 2 căn này cho tôi"
  ```

**API Endpoints**:
```
POST /generate-query           # Generate single query for persona
POST /generate-conversation    # Generate multi-turn conversation
POST /simulate-user-session    # Full user session simulation
GET /personas                  # List available personas
```

**Tech Stack**:
- FastAPI
- Ollama (llama2 or mistral)
- LangChain for conversation memory

### 2. Test Orchestrator Service (Port 8096)

**Purpose**: Coordinate test execution, manage test plans, track coverage

**Key Features**:
- **Test Plan Generation**: Automatically create comprehensive test plans
  ```json
  {
    "plan_id": "daily-regression-2025-11-02",
    "scenarios": [
      {"type": "search", "persona": "first_time_buyer", "count": 50},
      {"type": "compare", "persona": "experienced_investor", "count": 30},
      {"type": "investment_advice", "persona": "experienced_investor", "count": 20}
    ],
    "total_tests": 100,
    "parallel_workers": 10
  }
  ```

- **Scenario Executor**: Execute tests in parallel
  - Spin up multiple AI agents
  - Send queries to REE AI system (Orchestrator)
  - Collect responses
  - Pass to Evaluator

- **Coverage Tracker**: Ensure all intents, entities, edge cases are tested
  - Intent coverage matrix (8 intents × 5 personas = 40 combinations)
  - Entity extraction coverage (location, price, bedrooms, features)
  - Edge case coverage (empty results, ambiguous queries, typos)

**API Endpoints**:
```
POST /create-test-plan         # Create new test plan
POST /execute-test-plan        # Execute test plan
GET /test-plans                # List test plans
GET /coverage-report           # Get coverage metrics
```

### 3. Response Evaluator Service (Port 8097)

**Purpose**: Evaluate quality of system responses using multiple dimensions

**Evaluation Dimensions**:

1. **Accuracy Score (0-100)**:
   - Does response contain correct information?
   - Are property details accurate (price, location, features)?
   - Are calculations correct (price per m², ROI)?
   - Uses ground truth from OpenSearch database

2. **Relevance Score (0-100)**:
   - Does response address the user's query?
   - Are suggested properties relevant to filters?
   - Uses semantic similarity (embeddings)

3. **Completeness Score (0-100)**:
   - Are all required information provided?
   - For CTO 4-question scenario: All 4 questions answered?
   - Are sources cited?

4. **Coherence Score (0-100)**:
   - Is response well-structured?
   - Is language natural and fluent?
   - Are there contradictions?

5. **Latency Score (0-100)**:
   - Response time vs. expected SLA
   - 0-2s: 100 points
   - 2-5s: 80 points
   - 5-10s: 50 points
   - >10s: 0 points

**Evaluation Process**:
```python
# 1. Get response from system
response = await orchestrator.query("Tìm căn hộ quận 7")

# 2. Extract ground truth
properties = await db_gateway.search({"district": "Quận 7"})

# 3. Evaluate
scores = {
    "accuracy": evaluate_accuracy(response, properties),
    "relevance": evaluate_relevance(response.query, response.properties),
    "completeness": evaluate_completeness(response),
    "coherence": evaluate_coherence(response.text),
    "latency": evaluate_latency(response.time)
}

# 4. Overall score (weighted average)
overall = (
    scores["accuracy"] * 0.3 +
    scores["relevance"] * 0.3 +
    scores["completeness"] * 0.2 +
    scores["coherence"] * 0.15 +
    scores["latency"] * 0.05
)
```

**API Endpoints**:
```
POST /evaluate                 # Evaluate single response
POST /batch-evaluate           # Evaluate multiple responses
GET /evaluation-metrics        # Get scoring methodology details
```

### 4. Learning Service (Port 8098)

**Purpose**: Learn from test failures, identify patterns, auto-generate regression tests

**Key Features**:

1. **Failure Tracking Database**:
   ```sql
   CREATE TABLE test_failures (
       id SERIAL PRIMARY KEY,
       test_id VARCHAR(255),
       timestamp TIMESTAMP,
       query TEXT,
       expected_intent VARCHAR(50),
       actual_intent VARCHAR(50),
       expected_entities JSONB,
       actual_entities JSONB,
       response TEXT,
       scores JSONB,
       root_cause TEXT,
       fixed BOOLEAN DEFAULT FALSE,
       created_at TIMESTAMP DEFAULT NOW()
   );

   CREATE TABLE failure_patterns (
       id SERIAL PRIMARY KEY,
       pattern_type VARCHAR(100),  -- "entity_extraction", "intent_detection", "response_quality"
       pattern_description TEXT,
       frequency INT,
       examples JSONB,
       suggested_fix TEXT,
       priority VARCHAR(20),  -- "critical", "high", "medium", "low"
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

2. **Pattern Analyzer**: Identify common failure patterns
   ```python
   # Example patterns detected:
   patterns = [
       {
           "type": "entity_extraction",
           "issue": "Price range 'dưới 3 tỷ' not extracted correctly",
           "frequency": 15,
           "examples": ["dưới 3 tỷ", "dưới 3 tỉ", "duoi 3 ty"],
           "suggested_fix": "Add more price range variations to extraction regex"
       },
       {
           "type": "intent_detection",
           "issue": "Compare intent mistaken for search",
           "frequency": 8,
           "examples": ["so sánh 2 căn này", "compare these 2"],
           "suggested_fix": "Add 'so sánh', 'compare' to COMPARE intent keywords"
       }
   ]
   ```

3. **Regression Test Generator**: Auto-create tests for fixed bugs
   ```python
   # When bug is fixed, automatically generate regression test:
   def generate_regression_test(failure):
       return f"""
   @pytest.mark.regression
   @pytest.mark.asyncio
   async def test_regression_{failure.id}():
       # Bug: {failure.root_cause}
       # Fixed: {failure.fix_description}
       response = await orchestrator.query("{failure.query}")
       assert response.intent == "{failure.expected_intent}"
       assert extract_price(response) == {failure.expected_entities["price"]}
       """
   ```

4. **Trend Analyzer**: Track improvement over time
   - Daily/weekly/monthly failure rate trends
   - Most common failure types
   - Average scores by dimension
   - Time-to-fix metrics

**API Endpoints**:
```
POST /record-failure           # Record new failure
GET /failure-patterns          # Get identified patterns
POST /generate-regression-test # Generate test from failure
GET /trends                    # Get trend analysis
```

### 5. Improvement Service (Port 8099)

**Purpose**: Automatically suggest and apply improvements to the system

**Key Features**:

1. **Prompt Optimizer**:
   - Analyze prompt effectiveness
   - A/B test different prompts
   - Suggest improvements based on failure patterns

   ```python
   # Example optimization:
   current_prompt = """
   You are a real estate assistant. Answer the user's query.
   """

   optimized_prompt = """
   You are a real estate assistant specializing in Ho Chi Minh City properties.

   When the user asks for property search:
   - Extract: location, price range, bedrooms, features
   - Format: Return structured JSON with {location, price_min, price_max, bedrooms}
   - Always ask clarifying questions if information is missing

   When providing property recommendations:
   - Cite specific properties with IDs
   - Include: price, location, features
   - Explain why each property matches the criteria
   """

   # Test both prompts, compare scores:
   # Current: 72.5 average score
   # Optimized: 84.3 average score ✅ Adopt optimized prompt
   ```

2. **Parameter Tuner**:
   - Optimize LLM parameters (temperature, max_tokens, top_p)
   - Find best configurations for each intent type

   ```python
   # Example tuning results:
   intent_configs = {
       "search": {"temperature": 0.3, "max_tokens": 500},
       "compare": {"temperature": 0.5, "max_tokens": 800},
       "investment_advice": {"temperature": 0.7, "max_tokens": 1000}
   }
   ```

3. **A/B Testing Framework**:
   - Test multiple approaches simultaneously
   - Statistical significance testing
   - Gradual rollout (5% → 25% → 50% → 100%)

4. **Auto-Fix Engine**:
   - For common patterns, automatically apply fixes
   - Generate pull requests with fixes
   - Run tests to verify fixes don't break anything

   ```python
   # Example auto-fix:
   pattern = {
       "type": "entity_extraction",
       "issue": "Price 'dưới 3 tỷ' not extracted",
       "fix_type": "regex_update"
   }

   # Auto-generate fix:
   fix = """
   # File: services/orchestrator/entity_extractor.py
   # Line: 45

   - price_pattern = r'(\\d+) tỷ'
   + price_pattern = r'(dưới |trên )?(\\d+) (tỷ|tỉ|ty)'
   """

   # Apply fix, run tests, create PR
   ```

**API Endpoints**:
```
POST /optimize-prompt          # Optimize prompt for intent
POST /tune-parameters          # Find optimal parameters
POST /create-ab-test           # Create A/B test
POST /auto-fix                 # Apply automatic fix
GET /improvement-suggestions   # Get pending suggestions
```

### 6. Test Dashboard (Port 3002)

**Purpose**: Visualize test metrics, failures, and improvements in real-time

**Key Dashboards**:

1. **Overview Dashboard**:
   - Total tests run (today/week/month)
   - Pass rate (95.2%)
   - Average score (82.3/100)
   - Failed tests (12)
   - Identified patterns (5)
   - Auto-fixes applied (3)

2. **Quality Metrics Dashboard**:
   - Accuracy trend (line chart over time)
   - Relevance distribution (histogram)
   - Completeness by intent (bar chart)
   - Coherence trend
   - Latency P95/P99

3. **Failure Analysis Dashboard**:
   - Top failure types (pie chart)
   - Failure frequency heatmap (intent × persona)
   - Root cause distribution
   - Time-to-fix metrics

4. **Coverage Dashboard**:
   - Intent coverage matrix (8 × 5)
   - Entity extraction coverage
   - Edge case coverage
   - Persona coverage

5. **Improvement Dashboard**:
   - Optimization history
   - A/B test results
   - Auto-fix success rate
   - Prompt evolution timeline

**Tech Stack**:
- React + TypeScript
- Chart.js or Recharts
- WebSocket for real-time updates
- FastAPI backend

## Workflow Example

### Daily Automation Test Run

```
1. Test Plan Generation (8:00 AM)
   └─ Test Orchestrator creates plan:
      - 100 search queries (20 per persona)
      - 50 compare queries
      - 30 investment advice queries
      - 20 edge cases

2. Test Execution (8:05 AM - 9:00 AM)
   └─ AI Test Agent generates queries
   └─ Test Orchestrator sends to REE AI system
   └─ Responses collected

3. Evaluation (9:00 AM - 9:30 AM)
   └─ Response Evaluator scores all responses
   └─ Identify failures (score < 70)
   └─ 12 failures found

4. Learning (9:30 AM - 10:00 AM)
   └─ Learning Service analyzes failures
   └─ Identifies 3 patterns:
      - Price extraction issues (5 cases)
      - Intent confusion: compare vs search (4 cases)
      - Empty results for some districts (3 cases)

5. Improvement (10:00 AM - 11:00 AM)
   └─ Improvement Service generates fixes:
      - Update price extraction regex
      - Add more compare keywords
      - Improve district name normalization
   └─ Auto-apply fixes (if confidence > 90%)
   └─ Create PRs for manual review (if confidence < 90%)

6. Regression Test Generation (11:00 AM)
   └─ Generate 12 new regression tests
   └─ Add to test suite

7. Re-run Tests (11:30 AM)
   └─ Run tests again with fixes applied
   └─ 10/12 failures fixed ✅
   └─ 2 failures need manual investigation

8. Report Generation (12:00 PM)
   └─ Send daily report to team:
      - Tests run: 200
      - Pass rate: 94% (188/200)
      - Failures: 12 → 2 (10 auto-fixed)
      - New patterns: 3
      - Auto-fixes applied: 3
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create AI Test Agent Service
  - Persona definitions
  - Query generator using Ollama
  - Basic conversation flow
- [ ] Create Test Orchestrator Service
  - Test plan structure
  - Basic executor
- [ ] Set up databases (PostgreSQL: test_results, test_failures)

### Phase 2: Evaluation (Week 2)
- [ ] Create Response Evaluator Service
  - Accuracy scorer
  - Relevance scorer (semantic similarity)
  - Completeness checker
- [ ] Integrate with Test Orchestrator
- [ ] Store evaluation results in database

### Phase 3: Learning (Week 3)
- [ ] Create Learning Service
  - Failure tracking
  - Pattern analyzer
  - Regression test generator
- [ ] Implement trend analysis

### Phase 4: Improvement (Week 4)
- [ ] Create Improvement Service
  - Prompt optimizer
  - A/B testing framework
  - Auto-fix engine (simple patterns)
- [ ] Manual review workflow for complex fixes

### Phase 5: Visualization (Week 5)
- [ ] Build Test Dashboard
  - Overview metrics
  - Quality charts
  - Failure analysis
  - Coverage heatmaps
- [ ] Real-time updates via WebSocket

### Phase 6: Integration & Automation (Week 6)
- [ ] Integrate with CI/CD pipeline
- [ ] Scheduled daily/weekly test runs
- [ ] Automated reporting to Slack/email
- [ ] Fine-tune auto-fix confidence thresholds

## Key Technologies

- **AI/LLM**: Ollama (llama2, mistral), OpenAI (backup)
- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL (test results, failures, patterns)
- **Cache**: Redis (real-time metrics)
- **Frontend**: React + TypeScript
- **Visualization**: Chart.js, Recharts
- **Testing**: pytest, pytest-asyncio
- **Embeddings**: sentence-transformers (semantic similarity)
- **NLP**: spaCy (Vietnamese tokenization)

## Success Metrics

### Short-term (Month 1)
- [ ] 95%+ test pass rate
- [ ] <5% manual test intervention
- [ ] 80+ average quality score
- [ ] 10+ patterns identified

### Medium-term (Month 3)
- [ ] 98%+ test pass rate
- [ ] 50+ regression tests auto-generated
- [ ] 20+ auto-fixes applied
- [ ] 5+ prompt optimizations deployed

### Long-term (Month 6)
- [ ] 99%+ test pass rate
- [ ] 90%+ fixes applied automatically
- [ ] 30+ A/B tests completed
- [ ] 10+ major system improvements from AI insights

## Security & Privacy

- All test data stored securely in PostgreSQL with encryption at rest
- No real user data used in tests (synthetic data only)
- Test queries are anonymized
- Dashboard requires authentication
- API endpoints protected with JWT

## Cost Optimization

- Use Ollama (local, free) for test generation
- OpenSearch caching for repeated queries
- Redis for real-time metrics (avoid DB load)
- Batch evaluation to reduce API calls
- Auto-scaling test workers based on load

## Monitoring & Alerts

- Alert if pass rate drops below 90%
- Alert if average score drops below 75
- Alert if latency P95 > 10s
- Alert if new failure pattern detected (frequency > 5)
- Daily summary report to team Slack channel

## Future Enhancements

1. **Adversarial Testing**: Generate queries designed to break the system
2. **Multi-language Support**: Test in English, Vietnamese, mixed languages
3. **Voice Query Testing**: Test speech-to-text → query flow
4. **Mobile App Testing**: Integrate with mobile UI testing
5. **Load Testing**: Simulate thousands of concurrent users
6. **Security Testing**: Test for injection attacks, data leaks
7. **Model Comparison**: Compare different LLM models (GPT-4 vs Claude vs Gemini)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-02
**Owner**: AI Engineering Team
