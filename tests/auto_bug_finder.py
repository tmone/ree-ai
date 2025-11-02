"""
Automatic Bug Finder - Runs scenarios continuously and logs bugs
"""
import asyncio
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

PROGRESS_FILE = "/tmp/ai_simulator_progress.json"
BUG_REPORT_FILE = "/tmp/bug_findings.md"
MAX_SCENARIOS = 100

def load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "completed_scenarios": [],
        "failed_scenarios": [],
        "total_passed": 0,
        "total_failed": 0
    }

def append_bug_report(bug_info):
    """Append bug to report file"""
    with open(BUG_REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n## Bug Found at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Scenario:** #{bug_info['scenario']}\n\n")
        f.write(f"**Issue:** {bug_info['issue']}\n\n")
        f.write(f"**Evidence:** {bug_info['evidence']}\n\n")
        f.write("---\n\n")

def analyze_scenario_result(scenario_num):
    """Analyze scenario result for bugs"""
    result_files = list(Path("/tmp").glob(f"scenario_{scenario_num}_*.json"))
    if not result_files:
        return None

    # Get latest result file
    result_file = max(result_files, key=lambda p: p.stat().st_mtime)

    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    bugs = []

    for turn in data.get('turns', []):
        response = turn.get('system_response', '')

        # Check for "None" district bug
        if 'ở None' in response or 'None.' in response:
            bugs.append({
                'scenario': scenario_num,
                'issue': 'District displays as "None" instead of actual district name',
                'evidence': f"Turn {turn['turn']}: {response[:200]}..."
            })

        # Check for error messages
        if 'gặp sự cố' in response or 'error' in response.lower():
            bugs.append({
                'scenario': scenario_num,
                'issue': 'System error in response',
                'evidence': f"Turn {turn['turn']}: {response[:200]}..."
            })

        # Check for price mismatch (properties way over budget)
        if '33 tỷ' in response or '18 tỷ' in response:
            # Check if this is way over the budget mentioned in persona
            budget = data.get('persona', {}).get('budget', '')
            if 'tỷ' in budget:
                max_budget_str = budget.split('-')[-1].strip().replace(' tỷ', '')
                try:
                    max_budget = float(max_budget_str)
                    if max_budget < 10:  # Budget under 10B but showing 18B+ properties
                        bugs.append({
                            'scenario': scenario_num,
                            'issue': f'Price filter not working - showing properties way over budget ({budget})',
                            'evidence': f"Turn {turn['turn']}: Found properties at 18-33 tỷ when budget is {budget}"
                        })
                except:
                    pass

        # Check for very slow responses (>60s)
        if turn.get('response_time_ms', 0) > 60000:
            bugs.append({
                'scenario': scenario_num,
                'issue': f"Very slow response: {turn['response_time_ms']/1000:.1f}s",
                'evidence': f"Turn {turn['turn']}: {turn['response_time_ms']}ms"
            })

    return bugs

def main():
    print("="*100)
    print("🤖 AUTOMATIC BUG FINDER - Running scenarios continuously")
    print("="*100)

    # Initialize bug report
    with open(BUG_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Bug Findings Report\n\n")
        f.write(f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

    progress = load_progress()
    tested = set(progress['completed_scenarios'] + progress['failed_scenarios'])
    untested = [i for i in range(1, MAX_SCENARIOS + 1) if i not in tested]

    print(f"📊 Progress: {len(tested)}/100 scenarios tested")
    print(f"🎯 Will test {len(untested)} remaining scenarios")
    print(f"📄 Bug report will be saved to: {BUG_REPORT_FILE}")
    print("\n" + "="*100 + "\n")

    bugs_found = 0

    for scenario_num in untested:
        print(f"\n🧪 Testing Scenario #{scenario_num}...")

        # Run test
        result = subprocess.run(
            ['python3', 'tests/test_single_scenario.py', str(scenario_num)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per scenario
        )

        # Analyze for bugs
        bugs = analyze_scenario_result(scenario_num)

        if bugs:
            print(f"🐛 Found {len(bugs)} bug(s) in scenario #{scenario_num}!")
            bugs_found += len(bugs)
            for bug in bugs:
                append_bug_report(bug)
                print(f"   - {bug['issue']}")
        else:
            print(f"✅ Scenario #{scenario_num} - No bugs detected")

        # Small delay between scenarios
        time.sleep(2)

    print("\n" + "="*100)
    print(f"🏁 TESTING COMPLETE")
    print(f"📊 Total bugs found: {bugs_found}")
    print(f"📄 Full report: {BUG_REPORT_FILE}")
    print("="*100)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        print(f"📄 Partial results saved to: {BUG_REPORT_FILE}")
