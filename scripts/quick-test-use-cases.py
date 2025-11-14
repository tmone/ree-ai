#!/usr/bin/env python
"""
Quick Test Script for Use Cases
Verifies that new implementations are syntactically correct
"""
import sys
import importlib.util
from pathlib import Path


def test_import(module_name, file_path):
    """Test if a module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name}: Import successful")
        return True
    except Exception as e:
        print(f"❌ {module_name}: Import failed - {str(e)}")
        return False


def test_orchestrator_methods():
    """Test that orchestrator has new methods"""
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        from services.orchestrator.main import Orchestrator

        # Check for new methods
        methods_to_check = [
            '_handle_property_posting',
            '_handle_price_consultation',
            '_build_conversation_context',
            '_generate_posting_feedback',
            '_query_similar_properties',
            '_validate_market_data',
            '_generate_price_consultation_response'
        ]

        missing = []
        for method in methods_to_check:
            if not hasattr(Orchestrator, method):
                missing.append(method)

        if missing:
            print(f"❌ Orchestrator: Missing methods: {', '.join(missing)}")
            return False
        else:
            print(f"✅ Orchestrator: All {len(methods_to_check)} methods present")
            return True

    except Exception as e:
        print(f"❌ Orchestrator: Check failed - {str(e)}")
        return False


def test_intent_type_enum():
    """Test that IntentType enum has all core intents"""
    try:
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        from shared.models.orchestrator import IntentType

        required_intents = ['POST', 'SEARCH', 'PRICE_CONSULTATION', 'CHAT']
        missing = []

        for intent in required_intents:
            if not hasattr(IntentType, intent):
                missing.append(intent)

        if missing:
            print(f"❌ IntentType: Missing intents: {', '.join(missing)}")
            return False
        else:
            print(f"✅ IntentType: All {len(required_intents)} core intents present")
            return True

    except Exception as e:
        print(f"❌ IntentType: Check failed - {str(e)}")
        return False


def main():
    """Run quick verification tests"""
    print("=" * 60)
    print("Quick Use Case Implementation Verification")
    print("=" * 60)
    print()

    project_root = Path(__file__).parent.parent
    tests_passed = 0
    tests_total = 0

    # Test 1: Import test files
    print("Test 1: Verifying test files...")
    test_files = [
        ('test_case1_property_posting', project_root / 'tests' / 'test_case1_property_posting.py'),
        ('test_case3_price_consultation', project_root / 'tests' / 'test_case3_price_consultation.py'),
        ('test_orchestrator_use_cases_integration', project_root / 'tests' / 'test_orchestrator_use_cases_integration.py')
    ]

    for module_name, file_path in test_files:
        tests_total += 1
        if test_import(module_name, file_path):
            tests_passed += 1

    print()

    # Test 2: Check orchestrator methods
    print("Test 2: Verifying orchestrator methods...")
    tests_total += 1
    if test_orchestrator_methods():
        tests_passed += 1
    print()

    # Test 3: Check IntentType enum
    print("Test 3: Verifying IntentType enum...")
    tests_total += 1
    if test_intent_type_enum():
        tests_passed += 1
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("✅ All quick verification tests passed!")
        print()
        print("Next steps:")
        print("  1. Run full test suite: pytest tests/test_case*.py -v")
        print("  2. Or use: scripts/run-use-case-tests.bat (Windows)")
        print("  3. Or use: scripts/run-use-case-tests.sh (Linux/Mac)")
        return 0
    else:
        print(f"❌ {tests_total - tests_passed} test(s) failed!")
        print()
        print("Please check the errors above and fix before running full tests.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
