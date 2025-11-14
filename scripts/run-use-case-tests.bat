@echo off
REM Run Use Case Tests for Orchestrator Service
REM Tests Case 1 (Property Posting) and Case 3 (Price Consultation)

echo ========================================
echo REE AI - Use Case Tests
echo ========================================
echo.

REM Check if pytest is installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo [ERROR] pytest is not installed!
    echo Please run: pip install -r requirements.txt
    exit /b 1
)

echo [INFO] Running Use Case Tests...
echo.

REM Test Case 1: Property Posting
echo ========================================
echo TEST: Case 1 - Property Posting
echo ========================================
pytest tests/test_case1_property_posting.py -v --tb=short
if errorlevel 1 (
    echo [FAILED] Case 1 tests failed!
    set TEST_FAILED=1
) else (
    echo [PASSED] Case 1 tests passed!
)
echo.

REM Test Case 3: Price Consultation
echo ========================================
echo TEST: Case 3 - Price Consultation
echo ========================================
pytest tests/test_case3_price_consultation.py -v --tb=short
if errorlevel 1 (
    echo [FAILED] Case 3 tests failed!
    set TEST_FAILED=1
) else (
    echo [PASSED] Case 3 tests passed!
)
echo.

REM Integration Tests
echo ========================================
echo TEST: Integration - All 4 Use Cases
echo ========================================
pytest tests/test_orchestrator_use_cases_integration.py -v --tb=short
if errorlevel 1 (
    echo [FAILED] Integration tests failed!
    set TEST_FAILED=1
) else (
    echo [PASSED] Integration tests passed!
)
echo.

REM Summary
echo ========================================
echo TEST SUMMARY
echo ========================================
if defined TEST_FAILED (
    echo [RESULT] Some tests FAILED! Please review errors above.
    exit /b 1
) else (
    echo [RESULT] All tests PASSED!
    exit /b 0
)
