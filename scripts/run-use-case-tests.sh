#!/bin/bash
# Run Use Case Tests for Orchestrator Service
# Tests Case 1 (Property Posting) and Case 3 (Price Consultation)

set -e  # Exit on error

echo "========================================"
echo "REE AI - Use Case Tests"
echo "========================================"
echo ""

# Check if pytest is installed
if ! python -c "import pytest" &> /dev/null; then
    echo "[ERROR] pytest is not installed!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

echo "[INFO] Running Use Case Tests..."
echo ""

TEST_FAILED=0

# Test Case 1: Property Posting
echo "========================================"
echo "TEST: Case 1 - Property Posting"
echo "========================================"
if pytest tests/test_case1_property_posting.py -v --tb=short; then
    echo "[PASSED] Case 1 tests passed!"
else
    echo "[FAILED] Case 1 tests failed!"
    TEST_FAILED=1
fi
echo ""

# Test Case 3: Price Consultation
echo "========================================"
echo "TEST: Case 3 - Price Consultation"
echo "========================================"
if pytest tests/test_case3_price_consultation.py -v --tb=short; then
    echo "[PASSED] Case 3 tests passed!"
else
    echo "[FAILED] Case 3 tests failed!"
    TEST_FAILED=1
fi
echo ""

# Integration Tests
echo "========================================"
echo "TEST: Integration - All 4 Use Cases"
echo "========================================"
if pytest tests/test_orchestrator_use_cases_integration.py -v --tb=short; then
    echo "[PASSED] Integration tests passed!"
else
    echo "[FAILED] Integration tests failed!"
    TEST_FAILED=1
fi
echo ""

# Summary
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
if [ $TEST_FAILED -eq 1 ]; then
    echo "[RESULT] Some tests FAILED! Please review errors above."
    exit 1
else
    echo "[RESULT] All tests PASSED!"
    exit 0
fi
