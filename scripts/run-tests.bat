@echo off
REM REE AI - Automated Test Runner (Windows)
REM Runs all tests in Docker containers

setlocal enabledelayedexpansion

echo ============================
echo REE AI - Automated Testing
echo ============================
echo.

set TEST_COMPOSE_FILE=docker-compose.test.yml
set TEST_RESULTS_DIR=.\test-results

REM Create test results directory
if not exist "%TEST_RESULTS_DIR%" mkdir "%TEST_RESULTS_DIR%"

REM Parse arguments
set RUN_ALL=true
set PYTEST_ARGS=-v --tb=short --junit-xml=/app/test-results/junit.xml

if "%1"=="--fast" (
    set RUN_ALL=false
    set PYTEST_ARGS=%PYTEST_ARGS% -m unit
)
if "%1"=="--integration" (
    set RUN_ALL=false
    set PYTEST_ARGS=%PYTEST_ARGS% -m integration
)
if "%1"=="--e2e" (
    set RUN_ALL=false
    set PYTEST_ARGS=%PYTEST_ARGS% -m e2e
)

echo Test Configuration:
if "%RUN_ALL%"=="true" (
    echo   - Running: ALL tests
    set PYTEST_ARGS=%PYTEST_ARGS% /app/tests
) else (
    echo   - Running: Selected tests
)
echo.

REM Step 1: Start infrastructure
echo Step 1: Starting infrastructure services...
docker-compose -f %TEST_COMPOSE_FILE% up -d postgres redis opensearch ollama
timeout /t 10 /nobreak > nul

echo   Waiting for services to be healthy...
timeout /t 15 /nobreak > nul
echo   OK Infrastructure ready
echo.

REM Step 2: Start Service Registry
echo Step 2: Starting Service Registry...
docker-compose -f %TEST_COMPOSE_FILE% up -d service-registry
timeout /t 10 /nobreak > nul
echo   OK Service Registry ready
echo.

REM Step 3: Start Core Services
echo Step 3: Starting Core Services...
docker-compose -f %TEST_COMPOSE_FILE% up -d core-gateway db-gateway
timeout /t 5 /nobreak > nul
echo   OK Core Services started
echo.

REM Step 4: Start AI Services
echo Step 4: Starting AI Services...
docker-compose -f %TEST_COMPOSE_FILE% up -d semantic-chunking classification
timeout /t 5 /nobreak > nul
echo   OK AI Services started
echo.

REM Step 5: Start Orchestrator
echo Step 5: Starting Orchestrator...
docker-compose -f %TEST_COMPOSE_FILE% up -d orchestrator
timeout /t 5 /nobreak > nul
echo   OK Orchestrator started
echo.

REM Wait for services to register
echo Waiting for services to register...
timeout /t 10 /nobreak > nul

REM Step 6: Run Tests
echo Step 6: Running Tests...
echo.

docker-compose -f %TEST_COMPOSE_FILE% run --rm test-runner pytest %PYTEST_ARGS%

set TEST_STATUS=%ERRORLEVEL%

echo.
if %TEST_STATUS%==0 (
    echo =============================
    echo ALL TESTS PASSED
    echo =============================
) else (
    echo =============================
    echo SOME TESTS FAILED
    echo =============================
)

echo.
echo Test Results: %TEST_RESULTS_DIR%\junit.xml
echo.

REM Cleanup
echo Cleaning up...
docker-compose -f %TEST_COMPOSE_FILE% down -v
echo OK Cleanup complete

exit /b %TEST_STATUS%
