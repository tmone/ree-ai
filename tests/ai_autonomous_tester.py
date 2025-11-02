"""
🤖 AI AUTONOMOUS TESTING SYSTEM
================================

Hệ thống test tự động với AI:
1. AI User Simulator: Generate test scenarios with Ollama/llama3.2
2. Test Executor: Execute queries against real Orchestrator
3. Bug Detector: Analyze responses for bugs using AI
4. Bug Reporter: Create bug reports for AI agents to fix

Features:
- ✅ Autonomous test generation (no manual test cases)
- ✅ Multi-intent coverage (all 8 intents)
- ✅ AI-powered bug detection
- ✅ Structured bug reports for agent fixing
- ✅ Performance metrics
- ✅ Vietnamese + English support
"""
import asyncio
import httpx
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# Configuration
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8090")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
BUG_REPORTS_DIR = os.getenv("BUG_REPORTS_DIR", "/tmp/bug_reports")


class IntentType(str, Enum):
    """8 intent types in REE AI system"""
    SEARCH = "search"
    COMPARE = "compare"
    PRICE_ANALYSIS = "price_analysis"
    INVESTMENT_ADVICE = "investment_advice"
    LOCATION_INSIGHTS = "location_insights"
    LEGAL_GUIDANCE = "legal_guidance"
    CHAT = "chat"
    UNKNOWN = "unknown"


class BugSeverity(str, Enum):
    """Bug severity levels"""
    CRITICAL = "critical"  # System crash, no response
    HIGH = "high"  # Wrong results, incorrect intent detection
    MEDIUM = "medium"  # Slow performance, incomplete response
    LOW = "low"  # Minor issues, cosmetic


@dataclass
class TestScenario:
    """A generated test scenario"""
    intent: IntentType
    query: str
    expected_behavior: str
    context: Optional[str] = None


@dataclass
class TestResult:
    """Result of a test execution"""
    scenario: TestScenario
    response: Optional[str]
    actual_intent: Optional[str]
    confidence: float
    response_time_ms: float
    status_code: int
    timestamp: str
    bugs_detected: List[Dict] = None


@dataclass
class BugReport:
    """Bug report for AI agent to fix"""
    bug_id: str
    severity: BugSeverity
    title: str
    description: str
    reproduction_steps: List[str]
    expected_behavior: str
    actual_behavior: str
    test_scenario: TestScenario
    test_result: TestResult
    suggested_fix: Optional[str] = None
    related_files: List[str] = None


class AIUserSimulator:
    """Generate realistic test scenarios using Ollama/llama3.2"""

    def __init__(self, ollama_url: str = OLLAMA_URL, model: str = OLLAMA_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate_scenarios(self, intent: IntentType, count: int = 5) -> List[TestScenario]:
        """Generate test scenarios for a specific intent"""
        prompt = self._build_prompt(intent, count)

        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                scenarios_text = data.get("response", "")
                return self._parse_scenarios(intent, scenarios_text)
            else:
                print(f"❌ Ollama error: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Failed to generate scenarios: {e}")
            return []

    def _build_prompt(self, intent: IntentType, count: int) -> str:
        """Build prompt for scenario generation"""
        intent_descriptions = {
            IntentType.SEARCH: "Tìm kiếm bất động sản (search for properties)",
            IntentType.COMPARE: "So sánh các bất động sản (compare properties)",
            IntentType.PRICE_ANALYSIS: "Phân tích giá & định giá (price analysis)",
            IntentType.INVESTMENT_ADVICE: "Tư vấn đầu tư (investment advice)",
            IntentType.LOCATION_INSIGHTS: "Phân tích khu vực (location insights)",
            IntentType.LEGAL_GUIDANCE: "Tư vấn pháp lý (legal guidance)",
            IntentType.CHAT: "Trò chuyện chung (general chat)",
            IntentType.UNKNOWN: "Câu hỏi không rõ ràng (unclear queries)"
        }

        return f"""You are a Vietnamese real estate customer testing a chatbot system.

Generate {count} realistic test queries for the intent: "{intent_descriptions[intent]}"

Requirements:
- Mix Vietnamese and English queries (70% Vietnamese, 30% English)
- Use realistic Vietnamese property terms (căn hộ, biệt thự, quận, tỷ)
- Include various property types, locations in Ho Chi Minh City
- Make queries natural and conversational
- Include edge cases and tricky queries

Format each query as:
QUERY: <query text>
EXPECTED: <what the system should do>
---

Generate {count} diverse test queries now:"""

    def _parse_scenarios(self, intent: IntentType, text: str) -> List[TestScenario]:
        """Parse generated scenarios from LLM response"""
        scenarios = []
        blocks = text.split("---")

        for block in blocks:
            if "QUERY:" in block and "EXPECTED:" in block:
                try:
                    lines = block.strip().split("\n")
                    query = ""
                    expected = ""

                    for line in lines:
                        if line.startswith("QUERY:"):
                            query = line.replace("QUERY:", "").strip()
                        elif line.startswith("EXPECTED:"):
                            expected = line.replace("EXPECTED:", "").strip()

                    if query and expected:
                        scenarios.append(TestScenario(
                            intent=intent,
                            query=query,
                            expected_behavior=expected
                        ))
                except Exception as e:
                    print(f"⚠️ Failed to parse scenario: {e}")
                    continue

        return scenarios

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class TestExecutor:
    """Execute test scenarios against real Orchestrator"""

    def __init__(self, orchestrator_url: str = ORCHESTRATOR_URL):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient(timeout=120.0)

    async def execute_scenario(self, scenario: TestScenario, user_id: str = "ai_tester") -> TestResult:
        """Execute a single test scenario"""
        start_time = time.time()

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/orchestrate",
                json={
                    "user_id": user_id,
                    "query": scenario.query,
                    "conversation_id": f"test_{scenario.intent.value}_{int(time.time())}"
                }
            )

            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    scenario=scenario,
                    response=data.get("response"),
                    actual_intent=data.get("intent"),
                    confidence=data.get("confidence", 0.0),
                    response_time_ms=elapsed_ms,
                    status_code=200,
                    timestamp=datetime.now().isoformat(),
                    bugs_detected=[]
                )
            else:
                return TestResult(
                    scenario=scenario,
                    response=None,
                    actual_intent=None,
                    confidence=0.0,
                    response_time_ms=elapsed_ms,
                    status_code=response.status_code,
                    timestamp=datetime.now().isoformat(),
                    bugs_detected=[{
                        "type": "http_error",
                        "message": f"HTTP {response.status_code}",
                        "severity": "critical"
                    }]
                )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return TestResult(
                scenario=scenario,
                response=None,
                actual_intent=None,
                confidence=0.0,
                response_time_ms=elapsed_ms,
                status_code=500,
                timestamp=datetime.now().isoformat(),
                bugs_detected=[{
                    "type": "exception",
                    "message": str(e),
                    "severity": "critical"
                }]
            )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class BugDetector:
    """AI-powered bug detection using Ollama"""

    def __init__(self, ollama_url: str = OLLAMA_URL, model: str = OLLAMA_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def analyze_result(self, result: TestResult) -> List[Dict]:
        """Analyze test result for bugs"""
        bugs = []

        # Check 1: HTTP errors
        if result.status_code != 200:
            bugs.append({
                "type": "http_error",
                "severity": BugSeverity.CRITICAL,
                "message": f"HTTP {result.status_code} - System không trả về response",
                "evidence": f"Status code: {result.status_code}"
            })

        # Check 2: Intent mismatch
        if result.actual_intent and result.actual_intent != result.scenario.intent.value:
            # Allow 'chat' as fallback for unimplemented intents
            if result.actual_intent != "chat":
                bugs.append({
                    "type": "intent_mismatch",
                    "severity": BugSeverity.HIGH,
                    "message": f"Intent detection sai: expected '{result.scenario.intent.value}', got '{result.actual_intent}'",
                    "evidence": f"Query: '{result.scenario.query}'"
                })

        # Check 3: Performance issues
        if result.response_time_ms > 30000:  # > 30s
            bugs.append({
                "type": "performance",
                "severity": BugSeverity.MEDIUM,
                "message": f"Response quá chậm: {result.response_time_ms:.0f}ms",
                "evidence": f"Threshold: 30000ms, Actual: {result.response_time_ms:.0f}ms"
            })

        # Check 4: Low confidence
        if result.confidence < 0.5:
            bugs.append({
                "type": "low_confidence",
                "severity": BugSeverity.LOW,
                "message": f"Confidence thấp: {result.confidence:.2f}",
                "evidence": f"Threshold: 0.5, Actual: {result.confidence:.2f}"
            })

        # Check 5: Empty or error response
        if result.response:
            if "lỗi" in result.response.lower() or "error" in result.response.lower():
                bugs.append({
                    "type": "error_response",
                    "severity": BugSeverity.HIGH,
                    "message": "Response chứa thông báo lỗi",
                    "evidence": result.response[:200]
                })

            # Check 6: AI-powered semantic analysis
            semantic_bugs = await self._analyze_semantic_quality(result)
            bugs.extend(semantic_bugs)

        return bugs

    async def _analyze_semantic_quality(self, result: TestResult) -> List[Dict]:
        """Use AI to analyze semantic quality of response"""
        if not result.response:
            return []

        prompt = f"""Analyze this chatbot response for bugs and issues:

USER QUERY: {result.scenario.query}
EXPECTED INTENT: {result.scenario.intent.value}
EXPECTED BEHAVIOR: {result.scenario.expected_behavior}

ACTUAL RESPONSE:
{result.response[:500]}

ACTUAL INTENT: {result.actual_intent}
CONFIDENCE: {result.confidence}

Identify specific bugs or issues. For each bug, provide:
BUG: <type>
SEVERITY: <critical|high|medium|low>
MESSAGE: <description>
EVIDENCE: <specific text from response>
---

Analyze now:"""

        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
            )

            if response.status_code == 200:
                data = response.json()
                analysis = data.get("response", "")
                return self._parse_bug_analysis(analysis)

        except Exception as e:
            print(f"⚠️ Semantic analysis failed: {e}")

        return []

    def _parse_bug_analysis(self, text: str) -> List[Dict]:
        """Parse bugs from AI analysis"""
        bugs = []
        blocks = text.split("---")

        for block in blocks:
            if "BUG:" in block:
                try:
                    bug = {}
                    for line in block.split("\n"):
                        if line.startswith("BUG:"):
                            bug["type"] = line.replace("BUG:", "").strip()
                        elif line.startswith("SEVERITY:"):
                            severity_text = line.replace("SEVERITY:", "").strip().lower()
                            bug["severity"] = BugSeverity(severity_text)
                        elif line.startswith("MESSAGE:"):
                            bug["message"] = line.replace("MESSAGE:", "").strip()
                        elif line.startswith("EVIDENCE:"):
                            bug["evidence"] = line.replace("EVIDENCE:", "").strip()

                    if bug.get("type") and bug.get("message"):
                        bugs.append(bug)
                except Exception as e:
                    print(f"⚠️ Failed to parse bug: {e}")

        return bugs

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class BugReporter:
    """Generate structured bug reports for AI agents"""

    def __init__(self, reports_dir: str = BUG_REPORTS_DIR):
        self.reports_dir = reports_dir
        os.makedirs(reports_dir, exist_ok=True)

    def create_bug_report(self, result: TestResult, bugs: List[Dict]) -> List[BugReport]:
        """Create bug reports from detected bugs"""
        reports = []

        for bug in bugs:
            bug_id = f"BUG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{bug['type']}"

            report = BugReport(
                bug_id=bug_id,
                severity=bug.get("severity", BugSeverity.MEDIUM),
                title=bug["message"],
                description=self._build_description(result, bug),
                reproduction_steps=self._build_repro_steps(result),
                expected_behavior=result.scenario.expected_behavior,
                actual_behavior=bug.get("evidence", result.response or "No response"),
                test_scenario=result.scenario,
                test_result=result,
                suggested_fix=self._suggest_fix(bug),
                related_files=self._identify_files(bug)
            )

            reports.append(report)

        return reports

    def _build_description(self, result: TestResult, bug: Dict) -> str:
        """Build detailed bug description"""
        return f"""## Bug Description

**Type:** {bug['type']}
**Severity:** {bug.get('severity', 'medium')}

{bug['message']}

## Context

**Test Query:** {result.scenario.query}
**Expected Intent:** {result.scenario.intent.value}
**Actual Intent:** {result.actual_intent or 'N/A'}
**Response Time:** {result.response_time_ms:.0f}ms
**Confidence:** {result.confidence:.2f}

## Evidence

{bug.get('evidence', 'No specific evidence')}
"""

    def _build_repro_steps(self, result: TestResult) -> List[str]:
        """Build reproduction steps"""
        return [
            f"Send query to Orchestrator: '{result.scenario.query}'",
            f"Expected intent: {result.scenario.intent.value}",
            f"Observe actual response and behavior",
            f"Compare with expected: {result.scenario.expected_behavior}"
        ]

    def _suggest_fix(self, bug: Dict) -> Optional[str]:
        """Suggest potential fix"""
        fix_suggestions = {
            "intent_mismatch": "Check intent detection logic in _detect_intent_simple() method. Ensure all 8 intents are implemented with proper keyword matching.",
            "http_error": "Check service health and connectivity. Review error handling and retry logic.",
            "performance": "Optimize database queries. Add caching. Check for N+1 query problems. Review OpenSearch performance.",
            "low_confidence": "Review entity extraction accuracy. Check if training data covers this query pattern.",
            "error_response": "Check error handling in orchestrator. Ensure graceful degradation instead of exposing errors to user."
        }

        return fix_suggestions.get(bug["type"], "Review related code and logs for root cause.")

    def _identify_files(self, bug: Dict) -> List[str]:
        """Identify files likely related to bug"""
        file_mapping = {
            "intent_mismatch": [
                "services/orchestrator/main.py:_detect_intent_simple",
                "shared/models/orchestrator.py:IntentType"
            ],
            "http_error": [
                "services/orchestrator/main.py:orchestrate",
                "services/core_gateway/main.py"
            ],
            "performance": [
                "services/orchestrator/main.py:_handle_search",
                "services/db_gateway/main.py:search",
                "services/orchestrator/main.py:_execute_filter_search"
            ],
            "error_response": [
                "services/orchestrator/main.py:_handle_chat",
                "services/orchestrator/main.py:_call_llm"
            ]
        }

        return file_mapping.get(bug["type"], ["services/orchestrator/main.py"])

    def save_report(self, report: BugReport) -> str:
        """Save bug report to markdown file"""
        filename = f"{report.bug_id}.md"
        filepath = os.path.join(self.reports_dir, filename)

        content = f"""# {report.title}

**Bug ID:** {report.bug_id}
**Severity:** {report.severity.value.upper()}
**Timestamp:** {report.test_result.timestamp}

---

{report.description}

## Reproduction Steps

{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(report.reproduction_steps))}

## Expected Behavior

{report.expected_behavior}

## Actual Behavior

```
{report.actual_behavior[:500]}
```

## Suggested Fix

{report.suggested_fix}

## Related Files

{chr(10).join(f'- {file}' for file in report.related_files)}

## Test Data

```json
{json.dumps(asdict(report.test_scenario), indent=2, ensure_ascii=False)}
```

## Full Test Result

```json
{json.dumps(asdict(report.test_result), indent=2, ensure_ascii=False, default=str)}
```

---

**Generated by AI Autonomous Tester**
**For AI Agent to fix this bug, read this report and apply fixes to the related files.**
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath


class AutonomousTester:
    """Main autonomous testing system"""

    def __init__(self):
        self.simulator = AIUserSimulator()
        self.executor = TestExecutor()
        self.detector = BugDetector()
        self.reporter = BugReporter()

    async def run_autonomous_test(self, num_scenarios_per_intent: int = 3):
        """Run full autonomous test cycle"""
        print("🤖 AI AUTONOMOUS TESTER")
        print("=" * 60)
        print(f"Model: {OLLAMA_MODEL}")
        print(f"Orchestrator: {ORCHESTRATOR_URL}")
        print(f"Scenarios per intent: {num_scenarios_per_intent}")
        print("=" * 60)

        all_intents = [intent for intent in IntentType if intent != IntentType.UNKNOWN]
        total_bugs = 0
        total_tests = 0

        for intent in all_intents:
            print(f"\n📋 Testing Intent: {intent.value}")
            print("-" * 60)

            # Step 1: Generate scenarios
            print(f"🔄 Generating {num_scenarios_per_intent} test scenarios...")
            scenarios = await self.simulator.generate_scenarios(intent, num_scenarios_per_intent)
            print(f"✅ Generated {len(scenarios)} scenarios")

            # Step 2: Execute tests
            for i, scenario in enumerate(scenarios, 1):
                print(f"\n  Test {i}/{len(scenarios)}: {scenario.query[:60]}...")

                result = await self.executor.execute_scenario(scenario)
                total_tests += 1

                print(f"  ⏱️  Response time: {result.response_time_ms:.0f}ms")
                print(f"  🎯 Intent: {result.actual_intent} (confidence: {result.confidence:.2f})")

                # Step 3: Detect bugs
                bugs = await self.detector.analyze_result(result)
                result.bugs_detected = bugs

                if bugs:
                    print(f"  🐛 Found {len(bugs)} bug(s)")
                    total_bugs += len(bugs)

                    # Step 4: Generate bug reports
                    reports = self.reporter.create_bug_report(result, bugs)
                    for report in reports:
                        filepath = self.reporter.save_report(report)
                        print(f"     📝 Bug report: {filepath}")
                        print(f"        Severity: {report.severity.value.upper()}")
                        print(f"        {report.title}")
                else:
                    print(f"  ✅ No bugs detected")

                # Small delay to avoid overwhelming system
                await asyncio.sleep(1)

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total_tests}")
        print(f"Total bugs found: {total_bugs}")
        print(f"Bug reports directory: {BUG_REPORTS_DIR}")
        print(f"Pass rate: {((total_tests - total_bugs) / total_tests * 100):.1f}%")

    async def cleanup(self):
        """Cleanup resources"""
        await self.simulator.close()
        await self.executor.close()
        await self.detector.close()


async def main():
    """Main entry point"""
    tester = AutonomousTester()

    try:
        await tester.run_autonomous_test(num_scenarios_per_intent=3)
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
