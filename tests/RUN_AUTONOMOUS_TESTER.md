# 🤖 AI AUTONOMOUS TESTER - Quick Start Guide

## Overview

Hệ thống test tự động hoàn toàn bằng AI:
- **AI User Simulator**: Generate test scenarios tự động với Ollama/llama3.2
- **Test Executor**: Thực thi tests với Orchestrator thật
- **Bug Detector**: Phát hiện bugs bằng AI analysis
- **Bug Reporter**: Tạo bug reports để AI agents khác fix

## Prerequisites

```bash
# 1. Ensure all services running
docker-compose ps

# 2. Check Ollama is running
curl http://localhost:11434/api/tags

# 3. Check Orchestrator is healthy
curl http://localhost:8090/health
```

## Usage

### Option 1: Run Full Test (All 7 Intents, 3 scenarios each = 21 tests)

```bash
cd /Users/tmone/ree-ai
python3 tests/ai_autonomous_tester.py
```

**Output:**
- Console logs with real-time progress
- Bug reports in `/tmp/bug_reports/BUG_*.md`
- Summary statistics at end

### Option 2: Custom Configuration

```bash
# Use different model
OLLAMA_MODEL=qwen2.5:0.5b python3 tests/ai_autonomous_tester.py

# Change bug reports directory
BUG_REPORTS_DIR=/Users/tmone/ree-ai/bug_reports python3 tests/ai_autonomous_tester.py

# Test specific orchestrator
ORCHESTRATOR_URL=http://192.168.1.100:8090 python3 tests/ai_autonomous_tester.py
```

### Option 3: Programmatic Usage

```python
import asyncio
from tests.ai_autonomous_tester import AutonomousTester

async def run_custom_test():
    tester = AutonomousTester()
    try:
        # Run with 5 scenarios per intent
        await tester.run_autonomous_test(num_scenarios_per_intent=5)
    finally:
        await tester.cleanup()

asyncio.run(run_custom_test())
```

## Output Example

```
🤖 AI AUTONOMOUS TESTER
============================================================
Model: llama3.2
Orchestrator: http://localhost:8090
Scenarios per intent: 3
============================================================

📋 Testing Intent: search
------------------------------------------------------------
🔄 Generating 3 test scenarios...
✅ Generated 3 scenarios

  Test 1/3: Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ...
  ⏱️  Response time: 2847ms
  🎯 Intent: search (confidence: 0.95)
  ✅ No bugs detected

  Test 2/3: Find villa in District 2 with pool...
  ⏱️  Response time: 3142ms
  🎯 Intent: search (confidence: 0.92)
  ✅ No bugs detected

  Test 3/3: Có căn hộ nào view sông Sài Gòn không?...
  ⏱️  Response time: 2956ms
  🎯 Intent: search (confidence: 0.88)
  ✅ No bugs detected

📋 Testing Intent: compare
------------------------------------------------------------
🔄 Generating 3 test scenarios...
✅ Generated 3 scenarios

  Test 1/3: So sánh Vinhomes Grand Park với Masteri...
  ⏱️  Response time: 4521ms
  🎯 Intent: chat (confidence: 0.90)
  🐛 Found 1 bug(s)
     📝 Bug report: /tmp/bug_reports/BUG_20251103_012345_intent_mismatch.md
        Severity: HIGH
        Intent detection sai: expected 'compare', got 'chat'

============================================================
📊 TEST SUMMARY
============================================================
Total tests: 21
Total bugs found: 12
Bug reports directory: /tmp/bug_reports
Pass rate: 42.9%
```

## Bug Report Format

Each bug creates a structured markdown file:

```markdown
# Intent detection sai: expected 'compare', got 'chat'

**Bug ID:** BUG_20251103_012345_intent_mismatch
**Severity:** HIGH
**Timestamp:** 2025-11-03T01:23:45

---

## Bug Description
...

## Reproduction Steps
1. Send query to Orchestrator: 'So sánh Vinhomes Grand Park với Masteri'
2. Expected intent: compare
3. Observe actual response and behavior
...

## Expected Behavior
System should detect COMPARE intent and route to comparison handler

## Actual Behavior
System returned 'chat' intent instead

## Suggested Fix
Check intent detection logic in _detect_intent_simple() method.
Ensure all 8 intents are implemented with proper keyword matching.

## Related Files
- services/orchestrator/main.py:_detect_intent_simple
- shared/models/orchestrator.py:IntentType

## Test Data
(Full JSON with scenario details)
```

## Bug Severity Levels

- **CRITICAL**: System crash, no response, HTTP errors
- **HIGH**: Wrong results, intent mismatch, data corruption
- **MEDIUM**: Slow performance (>30s), incomplete responses
- **LOW**: Minor issues, low confidence, cosmetic

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ORCHESTRATOR_URL` | `http://localhost:8090` | Orchestrator endpoint |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Model for test generation |
| `BUG_REPORTS_DIR` | `/tmp/bug_reports` | Bug reports output directory |

## How It Works

### 1. Test Generation (AI-Powered)

Llama3.2 generates realistic test queries for each intent:

```
Prompt: "Generate 3 realistic Vietnamese real estate queries for COMPARE intent..."

AI Output:
QUERY: So sánh giá căn hộ Vinhomes và Masteri
EXPECTED: System should compare two properties
---
QUERY: Căn nào tốt hơn cho đầu tư?
EXPECTED: System should provide comparison analysis
---
```

### 2. Test Execution

Execute each scenario against real Orchestrator:
- Record response time
- Capture intent detection
- Get confidence score
- Save full response

### 3. Bug Detection (Multi-Layer)

**Layer 1: Rule-Based Checks**
- HTTP errors (status ≠ 200)
- Intent mismatch (expected ≠ actual)
- Performance issues (>30s)
- Low confidence (<0.5)

**Layer 2: AI Semantic Analysis**
- Llama3.2 analyzes response quality
- Detects semantic errors
- Identifies incomplete/incorrect answers
- Finds edge cases

### 4. Bug Reporting

Generate structured markdown reports:
- Severity classification
- Reproduction steps
- Expected vs actual behavior
- Suggested fixes
- Related files for fixing

## Integration with Bug Fixing Workflow

Bug reports are designed for AI agents to consume:

```bash
# 1. Run autonomous tester
python3 tests/ai_autonomous_tester.py

# 2. AI agent reads bug reports
for file in /tmp/bug_reports/BUG_*.md; do
    claude-code fix --bug-report="$file"
done

# 3. Re-test to verify fixes
python3 tests/ai_autonomous_tester.py
```

## Tips & Best Practices

1. **Run Regularly**: Run after each major change to catch regressions
2. **Review AI-Generated Scenarios**: AI might generate creative edge cases
3. **Tune Temperature**: Higher temperature = more diverse tests
4. **Monitor Performance**: Track bug count trend over time
5. **Fix Critical Bugs First**: Sort by severity

## Troubleshooting

### Issue: No scenarios generated

```bash
# Check Ollama connectivity
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"test","stream":false}'

# Check model availability
curl http://localhost:11434/api/tags | grep llama3.2
```

### Issue: All tests fail

```bash
# Check Orchestrator
curl http://localhost:8090/health

# Check services
docker-compose ps

# View orchestrator logs
docker-compose logs orchestrator --tail=50
```

### Issue: Bug reports not created

```bash
# Check directory permissions
ls -la /tmp/bug_reports

# Create directory manually
mkdir -p /tmp/bug_reports
chmod 755 /tmp/bug_reports
```

## Advanced Features

### Custom Bug Detectors

Extend `BugDetector` class to add domain-specific checks:

```python
class CustomBugDetector(BugDetector):
    async def analyze_result(self, result):
        bugs = await super().analyze_result(result)

        # Custom check: Price format
        if result.response and "tỷ" in result.response:
            if not self._validate_price_format(result.response):
                bugs.append({
                    "type": "price_format_error",
                    "severity": BugSeverity.MEDIUM,
                    "message": "Price format incorrect"
                })

        return bugs
```

### Parallel Testing

Run multiple testers concurrently:

```python
async def run_parallel_tests():
    testers = [AutonomousTester() for _ in range(5)]
    tasks = [t.run_autonomous_test(2) for t in testers]
    await asyncio.gather(*tasks)
```

---

**Created by:** AI Autonomous Tester
**Last Updated:** 2025-11-03
**Version:** 1.0.0
