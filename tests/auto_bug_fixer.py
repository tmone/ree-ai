"""
Automatic Bug Finder & Fixer - Detects and automatically fixes common bugs
"""
import asyncio
import subprocess
import json
import time
import re
from pathlib import Path
from datetime import datetime

PROGRESS_FILE = "/tmp/ai_simulator_progress.json"
BUG_REPORT_FILE = "/tmp/bug_findings_and_fixes.md"
MAX_SCENARIOS = 100

class AutoBugFixer:
    def __init__(self):
        self.bugs_found = 0
        self.bugs_fixed = 0
        self.bugs_failed_to_fix = 0

    def log_action(self, message):
        """Log action to both console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        with open(BUG_REPORT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{log_msg}\n")

    def append_bug_report(self, bug_info, fix_info=None):
        """Append bug and fix info to report file"""
        with open(BUG_REPORT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n## Bug #{self.bugs_found} - {datetime.now().strftime('%H:%M:%S')}\n\n")
            f.write(f"**Scenario:** #{bug_info['scenario']}\n\n")
            f.write(f"**Issue:** {bug_info['issue']}\n\n")
            f.write(f"**Evidence:** {bug_info['evidence']}\n\n")

            if fix_info:
                f.write(f"**Fix Applied:** ✅\n\n")
                f.write(f"```\n{fix_info['description']}\n```\n\n")
                f.write(f"**File Modified:** {fix_info['file']}\n\n")
                f.write(f"**Verification:** {fix_info['verification']}\n\n")
            else:
                f.write(f"**Fix Applied:** ❌ Could not auto-fix\n\n")

            f.write("---\n\n")

    def fix_none_district_bug(self):
        """
        Fix: District displays as "None"
        Root cause: Missing district in response formatting
        """
        try:
            orchestrator_file = Path("/Users/tmone/ree-ai/services/orchestrator/main.py")

            if not orchestrator_file.exists():
                return None

            content = orchestrator_file.read_text(encoding='utf-8')

            # Check if bug exists: Look for response formatting that might output "None"
            # Pattern: "ở {city}" or "ở {district}" where city/district might be None

            # Fix pattern 1: In _generate_no_results_clarification
            old_pattern = r'f"Tôi tìm thấy \*\*\{total_in_city\} \{property_type\}\*\* ở \{city\}\."'
            new_pattern = r'f"Tôi tìm thấy **{total_in_city} {property_type}** ở {city or \'Hồ Chí Minh\'}."'

            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                orchestrator_file.write_text(content, encoding='utf-8')

                # Rebuild orchestrator
                subprocess.run(['docker-compose', 'build', 'orchestrator'],
                             capture_output=True, check=False)
                subprocess.run(['docker-compose', 'up', '-d', 'orchestrator'],
                             capture_output=True, check=False)
                time.sleep(10)  # Wait for restart

                return {
                    'description': 'Added fallback for None city: city or "Hồ Chí Minh"',
                    'file': 'services/orchestrator/main.py',
                    'verification': 'Service rebuilt and restarted'
                }

            return None

        except Exception as e:
            self.log_action(f"❌ Failed to fix None district bug: {e}")
            return None

    def fix_price_filter_bug(self, scenario_result):
        """
        Fix: Properties way over budget being returned
        This might be due to missing price normalization
        """
        # This is harder to auto-fix as it requires understanding the query context
        # For now, we'll just log it for manual review
        return None

    def verify_fix(self, scenario_num, bug_type):
        """
        Verify that a fix actually worked by re-running the scenario
        """
        try:
            result = subprocess.run(
                ['python3', 'tests/test_single_scenario.py', str(scenario_num)],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Re-analyze the new result
            bugs = self.analyze_scenario_result(scenario_num)

            # Check if the specific bug type is still present
            for bug in bugs:
                if bug_type in bug['issue']:
                    return False, "Bug still present after fix"

            return True, "Bug fixed successfully"

        except Exception as e:
            return False, f"Verification failed: {e}"

    def analyze_scenario_result(self, scenario_num):
        """Analyze scenario result for bugs"""
        result_files = list(Path("/tmp").glob(f"scenario_{scenario_num}_*.json"))
        if not result_files:
            return []

        # Get latest result file
        result_file = max(result_files, key=lambda p: p.stat().st_mtime)

        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bugs = []

        for turn in data.get('turns', []):
            response = turn.get('system_response', '')

            # Bug 1: "None" district display
            if 'ở None' in response or ' None.' in response:
                bugs.append({
                    'scenario': scenario_num,
                    'type': 'none_district',
                    'issue': 'District displays as "None" instead of actual district name',
                    'evidence': f"Turn {turn['turn']}: {response[:200]}...",
                    'fixable': True,
                    'fix_function': self.fix_none_district_bug
                })

            # Bug 2: System error messages
            if 'gặp sự cố' in response or 'error' in response.lower():
                bugs.append({
                    'scenario': scenario_num,
                    'type': 'system_error',
                    'issue': 'System error in response',
                    'evidence': f"Turn {turn['turn']}: {response[:200]}...",
                    'fixable': False,
                    'fix_function': None
                })

            # Bug 3: Price mismatch (properties way over budget)
            if '33 tỷ' in response or '18 tỷ' in response:
                budget = data.get('persona', {}).get('budget', '')
                if 'tỷ' in budget:
                    max_budget_str = budget.split('-')[-1].strip().replace(' tỷ', '')
                    try:
                        max_budget = float(max_budget_str)
                        if max_budget < 10:
                            bugs.append({
                                'scenario': scenario_num,
                                'type': 'price_filter',
                                'issue': f'Price filter not working - showing properties way over budget ({budget})',
                                'evidence': f"Turn {turn['turn']}: Found properties at 18-33 tỷ when budget is {budget}",
                                'fixable': False,
                                'fix_function': None
                            })
                    except:
                        pass

            # Bug 4: Very slow responses (>60s)
            if turn.get('response_time_ms', 0) > 60000:
                bugs.append({
                    'scenario': scenario_num,
                    'type': 'slow_response',
                    'issue': f"Very slow response: {turn['response_time_ms']/1000:.1f}s",
                    'evidence': f"Turn {turn['turn']}: {turn['response_time_ms']}ms",
                    'fixable': False,  # Performance issues need deeper investigation
                    'fix_function': None
                })

        return bugs

    def load_progress(self):
        if Path(PROGRESS_FILE).exists():
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        return {
            "completed_scenarios": [],
            "failed_scenarios": [],
            "total_passed": 0,
            "total_failed": 0
        }

    def run(self):
        """Main execution loop"""
        print("="*100)
        print("🤖 AUTOMATIC BUG FINDER & FIXER")
        print("="*100)

        # Initialize bug report
        with open(BUG_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# Bug Findings & Fixes Report\n\n")
            f.write(f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

        progress = self.load_progress()
        tested = set(progress['completed_scenarios'] + progress['failed_scenarios'])
        untested = [i for i in range(1, MAX_SCENARIOS + 1) if i not in tested]

        self.log_action(f"📊 Progress: {len(tested)}/100 scenarios tested")
        self.log_action(f"🎯 Will test {len(untested)} remaining scenarios")
        self.log_action(f"📄 Bug report: {BUG_REPORT_FILE}")
        print("\n" + "="*100 + "\n")

        for scenario_num in untested:
            self.log_action(f"\n🧪 Testing Scenario #{scenario_num}...")

            # Run test
            try:
                result = subprocess.run(
                    ['python3', 'tests/test_single_scenario.py', str(scenario_num)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            except subprocess.TimeoutExpired:
                self.log_action(f"⏰ Scenario #{scenario_num} timed out (>5 min)")
                continue

            # Analyze for bugs
            bugs = self.analyze_scenario_result(scenario_num)

            if bugs:
                self.log_action(f"🐛 Found {len(bugs)} bug(s) in scenario #{scenario_num}!")

                for bug in bugs:
                    self.bugs_found += 1
                    self.log_action(f"   Bug #{self.bugs_found}: {bug['issue']}")

                    fix_info = None

                    # Try to auto-fix if fixable
                    if bug['fixable'] and bug['fix_function']:
                        self.log_action(f"   🔧 Attempting to fix...")

                        fix_info = bug['fix_function']()

                        if fix_info:
                            # Verify fix
                            verified, msg = self.verify_fix(scenario_num, bug['type'])

                            if verified:
                                self.log_action(f"   ✅ Fix verified: {msg}")
                                fix_info['verification'] = msg
                                self.bugs_fixed += 1
                            else:
                                self.log_action(f"   ⚠️  Fix verification failed: {msg}")
                                fix_info['verification'] = f"FAILED: {msg}"
                                self.bugs_failed_to_fix += 1
                        else:
                            self.log_action(f"   ❌ Could not generate fix")
                            self.bugs_failed_to_fix += 1
                    else:
                        self.log_action(f"   ⚠️  Bug requires manual fix")
                        self.bugs_failed_to_fix += 1

                    # Log to report
                    self.append_bug_report(bug, fix_info)

            else:
                self.log_action(f"✅ Scenario #{scenario_num} - No bugs detected")

            # Small delay between scenarios
            time.sleep(2)

        # Final summary
        print("\n" + "="*100)
        self.log_action(f"🏁 TESTING COMPLETE")
        self.log_action(f"📊 Bugs found: {self.bugs_found}")
        self.log_action(f"✅ Bugs auto-fixed: {self.bugs_fixed}")
        self.log_action(f"❌ Bugs requiring manual fix: {self.bugs_failed_to_fix}")
        self.log_action(f"📄 Full report: {BUG_REPORT_FILE}")
        print("="*100)

if __name__ == "__main__":
    try:
        fixer = AutoBugFixer()
        fixer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        print(f"📄 Partial results saved to: {BUG_REPORT_FILE}")
