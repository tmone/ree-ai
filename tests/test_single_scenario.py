"""
Single Scenario AI User Simulator
Test one scenario at a time to debug and fix bugs iteratively
"""
import asyncio
import httpx
import time
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project root and tests folder
project_root = Path(__file__).parent.parent
tests_folder = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(tests_folder))

from test_ai_user_simulator import AIUserSimulator, USER_PERSONAS

PROGRESS_FILE = "/tmp/ai_simulator_progress.json"


def load_progress() -> Dict:
    """Load test progress from file"""
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "completed_scenarios": [],
        "failed_scenarios": [],
        "total_passed": 0,
        "total_failed": 0,
        "last_updated": None
    }


def save_progress(progress: Dict):
    """Save test progress to file"""
    progress["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Progress saved to {PROGRESS_FILE}")


async def test_single_scenario(scenario_num: int):
    """Test a single scenario"""
    if scenario_num < 1 or scenario_num > len(USER_PERSONAS):
        print(f"❌ Invalid scenario number. Must be 1-{len(USER_PERSONAS)}")
        return None

    persona = USER_PERSONAS[scenario_num - 1]

    print("\n" + "="*100)
    print(f"🎯 TESTING SCENARIO #{scenario_num}/100")
    print("="*100)

    simulator = AIUserSimulator(user_model="qwen3:0.6b")
    result = await simulator.run_scenario(persona, scenario_num)

    return result


async def main():
    """Main function"""
    progress = load_progress()

    print("\n" + "="*100)
    print("🔥 SINGLE SCENARIO AI USER SIMULATOR")
    print("="*100)
    print(f"✅ Completed: {len(progress['completed_scenarios'])} scenarios")
    print(f"❌ Failed: {len(progress['failed_scenarios'])} scenarios")
    print(f"📊 Pass Rate: {progress['total_passed']}/{progress['total_passed'] + progress['total_failed']}")

    if progress['completed_scenarios']:
        print(f"\n✅ Passed scenarios: {sorted(progress['completed_scenarios'])}")
    if progress['failed_scenarios']:
        print(f"❌ Failed scenarios: {sorted(progress['failed_scenarios'])}")

    print("\n" + "-"*100)

    # Get scenario number from command line or ask user
    if len(sys.argv) > 1:
        scenario_num = int(sys.argv[1])
    else:
        # Find next untested scenario
        all_scenarios = set(range(1, 101))
        tested_scenarios = set(progress['completed_scenarios'] + progress['failed_scenarios'])
        untested = sorted(all_scenarios - tested_scenarios)

        if untested:
            scenario_num = untested[0]
            print(f"\n🎯 Next untested scenario: #{scenario_num}")
            response = input(f"Test scenario #{scenario_num}? (y/n or enter different number): ").strip()

            if response.lower() == 'n':
                print("❌ Test cancelled")
                return
            elif response.isdigit():
                scenario_num = int(response)
        else:
            print("\n🎉 All 100 scenarios have been tested!")
            print(f"✅ Passed: {len(progress['completed_scenarios'])}")
            print(f"❌ Failed: {len(progress['failed_scenarios'])}")
            return

    print(f"\n🚀 Testing scenario #{scenario_num}...")
    print("-"*100)

    # Run test
    start_time = time.time()
    result = await test_single_scenario(scenario_num)
    elapsed = time.time() - start_time

    if result is None:
        return

    # Evaluate result
    success_rate = result['successful_turns'] / result['total_turns']
    passed = success_rate >= 0.6  # Pass if 60% or more turns successful

    print("\n" + "="*100)
    print(f"📊 SCENARIO #{scenario_num} RESULT")
    print("="*100)
    print(f"Success Rate: {success_rate*100:.1f}% ({result['successful_turns']}/{result['total_turns']})")
    print(f"Avg Response Time: {result['avg_response_time_ms']:.0f}ms")
    print(f"Avg Quality: {result['avg_vietnamese_quality']:.1f}/5")
    print(f"Total Time: {elapsed:.1f}s")

    if passed:
        print(f"\n✅ SCENARIO #{scenario_num} PASSED!")
        if scenario_num not in progress['completed_scenarios']:
            progress['completed_scenarios'].append(scenario_num)
            progress['total_passed'] += 1

        # Remove from failed if it was there
        if scenario_num in progress['failed_scenarios']:
            progress['failed_scenarios'].remove(scenario_num)
            progress['total_failed'] -= 1
    else:
        print(f"\n❌ SCENARIO #{scenario_num} FAILED!")
        print(f"⚠️  Success rate {success_rate*100:.1f}% is below 60% threshold")

        if scenario_num not in progress['failed_scenarios']:
            progress['failed_scenarios'].append(scenario_num)
            progress['total_failed'] += 1

        # Remove from completed if it was there
        if scenario_num in progress['completed_scenarios']:
            progress['completed_scenarios'].remove(scenario_num)
            progress['total_passed'] -= 1

    # Save progress
    save_progress(progress)

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"/tmp/scenario_{scenario_num}_{timestamp}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"📄 Detailed results saved to {result_file}")

    print("\n" + "="*100)
    print(f"📊 OVERALL PROGRESS: {len(progress['completed_scenarios'])}/100 scenarios passed")
    print("="*100)

    # Show next steps
    all_scenarios = set(range(1, 101))
    tested_scenarios = set(progress['completed_scenarios'] + progress['failed_scenarios'])
    untested = sorted(all_scenarios - tested_scenarios)

    if untested:
        print(f"\n💡 Next untested scenarios: {untested[:5]}")
        print(f"   Run: python3 tests/test_single_scenario.py {untested[0]}")

    if progress['failed_scenarios']:
        print(f"\n⚠️  Failed scenarios to fix: {sorted(progress['failed_scenarios'])}")
        print(f"   Re-test: python3 tests/test_single_scenario.py {sorted(progress['failed_scenarios'])[0]}")


if __name__ == "__main__":
    asyncio.run(main())
