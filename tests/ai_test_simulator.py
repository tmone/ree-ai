"""
AI-Powered Test Simulator
Automatically generates test cases, detects bugs, and proposes fixes
"""
import httpx
import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    FIXED = "fixed"


class TestCase:
    """A single test case"""
    def __init__(self, id: str, name: str, query: str, expected_behavior: str, category: str):
        self.id = id
        self.name = name
        self.query = query
        self.expected_behavior = expected_behavior
        self.category = category
        self.status = TestStatus.PENDING
        self.response = None
        self.error = None
        self.execution_time = 0.0
        self.reasoning_chain = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "query": self.query,
            "expected_behavior": self.expected_behavior,
            "category": self.category,
            "status": self.status,
            "execution_time": self.execution_time,
            "error": self.error
        }


class BugReport:
    """Bug detection report"""
    def __init__(self, test_case: TestCase, bug_type: str, severity: str, description: str):
        self.test_case = test_case
        self.bug_type = bug_type
        self.severity = severity  # "critical", "high", "medium", "low"
        self.description = description
        self.root_cause = None
        self.proposed_fix = None
        self.fix_applied = False
        self.verification_result = None

    def to_dict(self):
        return {
            "test_id": self.test_case.id,
            "test_name": self.test_case.name,
            "bug_type": self.bug_type,
            "severity": self.severity,
            "description": self.description,
            "root_cause": self.root_cause,
            "proposed_fix": self.proposed_fix,
            "fix_applied": self.fix_applied
        }


class AITestSimulator:
    """
    AI-powered test simulator with auto-fix capabilities
    """

    def __init__(self, base_url: str = "http://localhost:8090", llm_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.llm_url = llm_url
        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.test_cases: List[TestCase] = []
        self.bug_reports: List[BugReport] = []

    async def generate_test_cases(self, count: int = 20) -> List[TestCase]:
        """
        Use LLM to generate diverse test cases
        """
        print("\n🤖 Generating test cases using AI...")

        prompt = f"""Generate {count} diverse test cases for a Vietnamese real estate search system.

Test categories:
1. Simple searches (clear intent, specific requirements)
2. Ambiguous queries (missing information, vague requirements)
3. Complex multi-criteria searches
4. Context-dependent queries
5. Edge cases (empty, too short, unusual requests)

For each test case, provide:
- name: Brief test name
- query: Vietnamese search query
- expected_behavior: What should happen
- category: One of the categories above

Return as JSON array:
[
  {{
    "name": "Simple apartment search",
    "query": "Tìm căn hộ 2 phòng ngủ Quận 2",
    "expected_behavior": "Should search for 2-bedroom apartments in District 2",
    "category": "simple_search"
  }},
  ...
]

Generate diverse, realistic Vietnamese real estate queries."""

        try:
            response = await self.http_client.post(
                f"{self.llm_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.8
                }
            )

            if response.status_code == 200:
                content = response.json().get("content", "")

                # Extract JSON from response
                start_idx = content.find("[")
                end_idx = content.rfind("]") + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    test_data = json.loads(json_str)

                    for i, test in enumerate(test_data):
                        test_case = TestCase(
                            id=f"test_{i+1:03d}",
                            name=test.get("name", f"Test {i+1}"),
                            query=test.get("query", ""),
                            expected_behavior=test.get("expected_behavior", ""),
                            category=test.get("category", "unknown")
                        )
                        self.test_cases.append(test_case)

                    print(f"✅ Generated {len(self.test_cases)} test cases")
                    return self.test_cases
                else:
                    print("❌ Failed to parse JSON from LLM response")
                    return []
            else:
                print(f"❌ LLM request failed: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error generating test cases: {e}")
            return []

    async def run_test_case(self, test_case: TestCase, endpoint: str = "/orchestrate/v2") -> bool:
        """
        Execute a single test case
        """
        test_case.status = TestStatus.RUNNING
        start_time = time.time()

        try:
            response = await self.http_client.post(
                f"{self.base_url}{endpoint}",
                json={
                    "user_id": f"test_user_{test_case.id}",
                    "query": test_case.query,
                    "conversation_id": None
                }
            )

            test_case.execution_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                test_case.response = response.json()
                test_case.reasoning_chain = test_case.response.get("reasoning_chain")
                test_case.status = TestStatus.PASSED
                return True
            else:
                test_case.status = TestStatus.FAILED
                test_case.error = f"HTTP {response.status_code}: {response.text[:200]}"
                return False

        except Exception as e:
            test_case.execution_time = (time.time() - start_time) * 1000
            test_case.status = TestStatus.FAILED
            test_case.error = str(e)
            return False

    async def analyze_test_result(self, test_case: TestCase) -> Optional[BugReport]:
        """
        Use LLM to analyze test results and detect bugs
        """
        if test_case.status == TestStatus.PASSED and test_case.response:
            # Analyze response quality
            prompt = f"""Analyze this test result for a Vietnamese real estate search system:

Test: {test_case.name}
Query: "{test_case.query}"
Expected Behavior: {test_case.expected_behavior}

Response received:
- Intent: {test_case.response.get('intent')}
- Confidence: {test_case.response.get('confidence')}
- Response: {test_case.response.get('response', '')[:200]}...
- Reasoning steps: {len(test_case.response.get('reasoning_chain', {}).get('steps', []))}

Analysis tasks:
1. Does the response match expected behavior?
2. Is the confidence score appropriate?
3. Are there any reasoning errors?
4. Is the response in correct Vietnamese?
5. Any edge cases not handled?

If you find issues, respond with JSON:
{{
  "has_bug": true/false,
  "bug_type": "logic_error|low_confidence|wrong_intent|poor_response|other",
  "severity": "critical|high|medium|low",
  "description": "Clear description of the issue",
  "root_cause": "Likely root cause"
}}

If no issues, return: {{"has_bug": false}}"""

            try:
                response = await self.http_client.post(
                    f"{self.llm_url}/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500,
                        "temperature": 0.3
                    }
                )

                if response.status_code == 200:
                    content = response.json().get("content", "")

                    # Extract JSON
                    start_idx = content.find("{")
                    end_idx = content.rfind("}") + 1

                    if start_idx >= 0 and end_idx > start_idx:
                        analysis = json.loads(content[start_idx:end_idx])

                        if analysis.get("has_bug"):
                            bug_report = BugReport(
                                test_case=test_case,
                                bug_type=analysis.get("bug_type", "unknown"),
                                severity=analysis.get("severity", "medium"),
                                description=analysis.get("description", "")
                            )
                            bug_report.root_cause = analysis.get("root_cause")
                            return bug_report

            except Exception as e:
                print(f"⚠️ Error analyzing test {test_case.id}: {e}")

        elif test_case.status == TestStatus.FAILED:
            # Failed test - create bug report
            bug_report = BugReport(
                test_case=test_case,
                bug_type="execution_failure",
                severity="critical" if "500" in str(test_case.error) else "high",
                description=f"Test failed with error: {test_case.error}"
            )
            bug_report.root_cause = test_case.error
            return bug_report

        return None

    async def propose_fix(self, bug_report: BugReport) -> str:
        """
        Use LLM to propose a fix for the bug
        """
        print(f"\n🔧 Proposing fix for bug in test: {bug_report.test_case.name}")

        prompt = f"""You are a senior Python developer fixing bugs in a REE AI real estate system.

Bug Report:
- Test: {bug_report.test_case.name}
- Query: "{bug_report.test_case.query}"
- Bug Type: {bug_report.bug_type}
- Severity: {bug_report.severity}
- Description: {bug_report.description}
- Root Cause: {bug_report.root_cause}

Error details:
{bug_report.test_case.error}

System Architecture:
- Orchestrator with ReAct reasoning engine
- Knowledge base (PROPERTIES.md, LOCATIONS.md)
- Ambiguity detector
- RAG service for property search

Propose a fix:
1. Identify the likely file(s) that need changes
2. Describe the fix in detail
3. Provide specific code changes if possible

Respond in JSON:
{{
  "target_files": ["file1.py", "file2.py"],
  "fix_description": "Detailed explanation",
  "code_changes": "Specific changes to make",
  "risk_level": "low|medium|high",
  "testing_recommendation": "How to verify the fix"
}}"""

        try:
            response = await self.http_client.post(
                f"{self.llm_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.3
                }
            )

            if response.status_code == 200:
                content = response.json().get("content", "")

                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1

                if start_idx >= 0 and end_idx > start_idx:
                    fix_proposal = content[start_idx:end_idx]
                    bug_report.proposed_fix = fix_proposal
                    return fix_proposal

        except Exception as e:
            print(f"❌ Error proposing fix: {e}")

        return None

    async def run_all_tests(self, endpoint: str = "/orchestrate/v2") -> Dict[str, Any]:
        """
        Run all test cases and collect results
        """
        print(f"\n🚀 Running {len(self.test_cases)} test cases...")
        print(f"Target endpoint: {endpoint}\n")

        results = {
            "total": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "bugs_found": 0,
            "start_time": datetime.now().isoformat()
        }

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"[{i}/{len(self.test_cases)}] Running: {test_case.name} ({test_case.category})")
            print(f"  Query: '{test_case.query}'")

            success = await self.run_test_case(test_case, endpoint)

            if success:
                print(f"  ✅ PASSED ({test_case.execution_time:.0f}ms)")
                results["passed"] += 1
            else:
                print(f"  ❌ FAILED ({test_case.execution_time:.0f}ms)")
                print(f"  Error: {test_case.error}")
                results["failed"] += 1

            # Analyze result
            bug_report = await self.analyze_test_result(test_case)
            if bug_report:
                self.bug_reports.append(bug_report)
                results["bugs_found"] += 1
                print(f"  🐛 Bug detected: {bug_report.bug_type} ({bug_report.severity})")

            # Small delay to avoid overwhelming the system
            await asyncio.sleep(0.5)

        results["end_time"] = datetime.now().isoformat()
        return results

    async def auto_fix_bugs(self, max_fixes: int = 5) -> List[BugReport]:
        """
        Automatically propose fixes for detected bugs
        """
        print(f"\n🔧 Auto-fixing {len(self.bug_reports)} bugs...")

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_bugs = sorted(
            self.bug_reports,
            key=lambda b: severity_order.get(b.severity, 4)
        )

        fixed_bugs = []

        for i, bug_report in enumerate(sorted_bugs[:max_fixes], 1):
            print(f"\n[{i}/{min(max_fixes, len(sorted_bugs))}] Fixing: {bug_report.bug_type}")

            fix_proposal = await self.propose_fix(bug_report)

            if fix_proposal:
                print(f"✅ Fix proposed")
                print(f"Proposal: {fix_proposal[:200]}...")
                fixed_bugs.append(bug_report)
            else:
                print(f"❌ Could not propose fix")

        return fixed_bugs

    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate comprehensive test report
        """
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║              AI TEST SIMULATOR - FINAL REPORT                  ║
╚════════════════════════════════════════════════════════════════╝

📊 TEST SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests:     {results['total']}
✅ Passed:        {results['passed']} ({results['passed']/results['total']*100:.1f}%)
❌ Failed:        {results['failed']} ({results['failed']/results['total']*100:.1f}%)
🐛 Bugs Found:    {results['bugs_found']}

🐛 BUG BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Group bugs by severity
        bugs_by_severity = {}
        for bug in self.bug_reports:
            if bug.severity not in bugs_by_severity:
                bugs_by_severity[bug.severity] = []
            bugs_by_severity[bug.severity].append(bug)

        for severity in ["critical", "high", "medium", "low"]:
            if severity in bugs_by_severity:
                bugs = bugs_by_severity[severity]
                emoji = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                report += f"{emoji} {severity.upper()}: {len(bugs)} bugs\n"

        report += "\n📋 DETAILED BUG REPORTS\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        for i, bug in enumerate(self.bug_reports[:10], 1):  # Top 10 bugs
            report += f"\n{i}. [{bug.severity.upper()}] {bug.test_case.name}\n"
            report += f"   Query: \"{bug.test_case.query}\"\n"
            report += f"   Bug Type: {bug.bug_type}\n"
            report += f"   Description: {bug.description[:100]}...\n"
            if bug.proposed_fix:
                report += f"   ✅ Fix proposed\n"

        report += "\n\n🎯 RECOMMENDATIONS\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        if results["failed"] == 0:
            report += "✅ All tests passed! System is working as expected.\n"
        elif results["failed"] < results["total"] * 0.1:
            report += "✅ System is mostly stable (>90% pass rate).\n"
            report += "⚠️ Fix the identified bugs to improve robustness.\n"
        else:
            report += "⚠️ System needs attention (high failure rate).\n"
            report += "🔧 Priority: Fix critical and high severity bugs first.\n"

        report += f"\n🕐 Test Duration: {results['start_time']} to {results['end_time']}\n"
        report += "═" * 64 + "\n"

        return report


async def main():
    """
    Main test execution
    """
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         AI-POWERED TEST SIMULATOR FOR REE AI                   ║")
    print("║     Automatic Test Generation, Bug Detection & Auto-Fix       ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    simulator = AITestSimulator(
        base_url="http://localhost:8090",
        llm_url="http://localhost:8080"
    )

    # Step 1: Generate test cases
    await simulator.generate_test_cases(count=15)

    if not simulator.test_cases:
        print("❌ No test cases generated. Exiting.")
        return

    # Step 2: Run all tests
    results = await simulator.run_all_tests(endpoint="/orchestrate/v2")

    # Step 3: Auto-fix bugs
    if simulator.bug_reports:
        await simulator.auto_fix_bugs(max_fixes=5)

    # Step 4: Generate report
    report = simulator.generate_report(results)
    print(report)

    # Save report to file
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
        f.write("\n\nDETAILED TEST RESULTS\n")
        f.write("=" * 64 + "\n")
        for test in simulator.test_cases:
            f.write(f"\n{test.to_dict()}\n")

        f.write("\n\nBUG REPORTS\n")
        f.write("=" * 64 + "\n")
        for bug in simulator.bug_reports:
            f.write(f"\n{json.dumps(bug.to_dict(), indent=2, ensure_ascii=False)}\n")

    print(f"\n💾 Full report saved to: {report_file}")

    await simulator.http_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
