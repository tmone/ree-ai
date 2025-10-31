# REE AI - Professional Testing Suite

Comprehensive AI-focused testing framework for the REE AI Platform.

---

## 📋 Overview

This testing suite provides **professional-grade tests** specifically designed for AI applications:

- ✅ **AI Quality Tests** - Response accuracy, coherence, consistency
- ✅ **Failover Tests** - OpenAI → Ollama failover mechanism
- ✅ **Performance Tests** - Load testing, latency, throughput
- ✅ **Integration Tests** - End-to-end workflows
- ✅ **Edge Case Tests** - Error handling, unusual inputs

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /Users/tmone/ree-ai/tests
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=services --cov=shared --cov-report=html

# Run specific test categories
pytest -m ai              # Only AI tests
pytest -m failover        # Only failover tests
pytest -m critical        # Only critical tests
pytest -m "not slow"      # Skip slow tests
```

### 3. View Results

```bash
# Open HTML report
open tests/reports/report.html

# Open coverage report
open tests/coverage/index.html
```

---

## 📁 Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── pytest.ini                       # Pytest settings
├── requirements-test.txt            # Test dependencies
│
├── test_ai_quality.py              # ⭐ AI response quality tests (40+ tests)
│   ├── TestAIResponseQuality       # Accuracy, coherence, factual knowledge
│   ├── TestAIConversationFlow      # Multi-turn conversations
│   ├── TestAIEdgeCases            # Special characters, multilingual
│   └── TestAITokenUsage           # Token counting and limits
│
├── test_failover_mechanism.py      # ⭐ Failover reliability tests (25+ tests)
│   ├── TestFailoverReliability     # Basic failover functionality
│   ├── TestFailoverEdgeCases       # Long context, special chars, concurrent
│   ├── TestFailoverLogging         # Logging and observability
│   └── TestFailoverPerformance     # Latency and throughput
│
├── test_comprehensive.sh            # Shell-based integration tests
└── README.md                        # This file
```

---

## 🧪 Test Categories

### 1. AI Quality Tests (`test_ai_quality.py`)

**Purpose:** Verify AI responses are accurate, coherent, and high-quality

**Tests Include:**
- ✅ Mathematical accuracy (2+2=4, 15+27=42)
- ✅ Factual knowledge (capitals, dates, science)
- ✅ Response coherence and structure
- ✅ Code generation capabilities
- ✅ Consistency across multiple calls
- ✅ Multi-turn conversation memory
- ✅ System prompt adherence
- ✅ Multilingual support
- ✅ Token usage tracking

**Example:**
```bash
pytest tests/test_ai_quality.py -v

# Run only critical AI tests
pytest tests/test_ai_quality.py -m critical
```

**Key Tests:**
```python
test_basic_math_accuracy          # 15 + 27 = ?
test_factual_knowledge           # Capital of France?
test_response_coherence          # Well-formed sentences
test_code_generation             # Write Python function
test_consistency_across_calls    # Same question, same answer
test_multi_turn_conversation     # Remembers context
```

---

### 2. Failover Mechanism Tests (`test_failover_mechanism.py`)

**Purpose:** Ensure OpenAI → Ollama failover is reliable and performant

**Tests Include:**
- ✅ Rate limit detection and fallback
- ✅ Functionality preservation during failover
- ✅ Response time under 3 seconds
- ✅ Multiple consecutive failovers
- ✅ Different request parameters
- ✅ Long conversation context
- ✅ Concurrent requests (10+ simultaneous)
- ✅ Latency distribution (P50, P95, P99)
- ✅ Throughput (>5 req/s)

**Example:**
```bash
pytest tests/test_failover_mechanism.py -v

# Run only critical failover tests
pytest tests/test_failover_mechanism.py -m critical

# Run performance tests
pytest tests/test_failover_mechanism.py -m performance
```

**Key Tests:**
```python
test_rate_limit_triggers_fallback        # Primary failover test
test_failover_response_time             # <3s requirement
test_multiple_consecutive_failovers     # 5 requests in a row
test_concurrent_failover_requests       # 10 concurrent requests
test_failover_latency_distribution      # P95 < 5s
test_failover_throughput                # >5 req/s
```

---

## 🎯 Test Markers

Use markers to run specific test categories:

```bash
# By functionality
pytest -m ai              # AI-specific tests
pytest -m failover        # Failover tests
pytest -m integration     # Integration tests
pytest -m unit            # Unit tests
pytest -m e2e            # End-to-end tests

# By priority
pytest -m critical        # Must-pass tests
pytest -m smoke          # Quick smoke tests

# By speed
pytest -m "not slow"      # Skip slow tests
pytest -m slow           # Only slow tests

# By performance
pytest -m performance     # Performance benchmarks
```

---

## 📊 Test Reports

### HTML Report
```bash
pytest --html=tests/reports/report.html --self-contained-html
open tests/reports/report.html
```

### Coverage Report
```bash
pytest --cov=services --cov=shared --cov-report=html
open tests/coverage/index.html
```

### JSON Report (for CI/CD)
```bash
pytest --json-report --json-report-file=tests/reports/report.json
```

---

## 🔧 Advanced Usage

### Parallel Execution
```bash
# Run tests in parallel (faster)
pytest -n auto

# Use 4 workers
pytest -n 4
```

### Verbose Output
```bash
# Show test names
pytest -v

# Show print statements
pytest -s

# Show slowest 10 tests
pytest --durations=10
```

### Failed Tests Only
```bash
# Re-run only failed tests
pytest --lf

# Re-run failed tests first, then others
pytest --ff
```

### Stop on First Failure
```bash
pytest -x
```

### Debug Mode
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on error
pytest --pdbcls=IPython.terminal.debugger:Pdb
```

---

## 📈 Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable |
|--------|--------|------------|
| **Failover Latency (avg)** | < 1.5s | < 3.0s |
| **Failover Latency (P95)** | < 3.0s | < 5.0s |
| **Throughput** | > 10 req/s | > 5 req/s |
| **Success Rate** | > 95% | > 90% |
| **Concurrent Requests** | 20+ | 10+ |

### Run Performance Tests
```bash
pytest -m performance -v

# With detailed timing
pytest -m performance --durations=0
```

---

## 🚦 CI/CD Integration

### GitHub Actions Example
```yaml
name: AI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r tests/requirements-test.txt
      - name: Run critical tests
        run: |
          pytest -m critical --json-report
      - name: Run AI quality tests
        run: |
          pytest tests/test_ai_quality.py -v
      - name: Run failover tests
        run: |
          pytest tests/test_failover_mechanism.py -v
```

### Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
pytest -m "critical and not slow" -x
```

---

## 🐛 Debugging Failed Tests

### 1. Get Detailed Output
```bash
pytest tests/test_ai_quality.py::TestAIResponseQuality::test_basic_math_accuracy -vv -s
```

### 2. Check Service Logs
```bash
docker logs ree-ai-core-gateway --tail 50
```

### 3. Test Individual Endpoint
```bash
curl -X POST http://localhost:8080/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 10
  }'
```

---

## 📋 Test Checklist

Before deploying to production, ensure these tests pass:

### Critical Tests (Must Pass)
- [ ] `test_rate_limit_triggers_fallback` - Failover works
- [ ] `test_failover_response_time` - Response < 3s
- [ ] `test_basic_math_accuracy` - AI accuracy
- [ ] `test_factual_knowledge` - AI knowledge
- [ ] `test_multiple_consecutive_failovers` - Reliability

### Performance Tests (Should Pass)
- [ ] `test_failover_latency_distribution` - P95 < 5s
- [ ] `test_failover_throughput` - > 5 req/s
- [ ] `test_concurrent_failover_requests` - 80%+ success

### Quality Tests (Should Pass)
- [ ] `test_response_coherence` - Well-formed responses
- [ ] `test_consistency_across_calls` - Consistent answers
- [ ] `test_code_generation` - Can generate code

---

## 🎓 Writing New Tests

### Template for AI Quality Test
```python
@pytest.mark.ai
@pytest.mark.asyncio
async def test_my_ai_feature(core_gateway_client):
    """Test description."""
    response = await core_gateway_client.chat_completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=50
    )

    assert response.status_code == 200
    data = response.json()

    # Your assertions here
    assert "expected" in data["content"].lower()
```

### Template for Failover Test
```python
@pytest.mark.failover
@pytest.mark.asyncio
async def test_my_failover_scenario(core_gateway_client):
    """Test description."""
    response = await core_gateway_client.chat_completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=10
    )

    # Check failover occurred
    if response.status_code == 200:
        data = response.json()
        if data["id"].startswith("ollama-"):
            # Failover worked
            assert "qwen" in data["model"].lower()
```

---

## 📞 Support

For issues or questions about tests:
1. Check test output: `pytest -vv`
2. Check service health: `./tests/test_comprehensive.sh`
3. Review logs: `docker logs ree-ai-core-gateway`
4. See documentation: `docs/testing/`

---

## 📚 Additional Resources

- **Pytest Documentation:** https://docs.pytest.org/
- **Testing Best Practices:** `docs/testing/BEST_PRACTICES.md`
- **Test Report:** `docs/testing/COMPREHENSIVE_TEST_REPORT.md`
- **CI/CD Setup:** `docs/testing/CI_CD_SETUP.md`

---

**Last Updated:** 2025-10-31
**Test Coverage:** 80%+ (target: 90%)
**Total Tests:** 60+ AI-focused tests
