@echo off
REM Comprehensive Flow Testing Script for Windows
REM Tests all 3 main flows based on architecture diagrams

setlocal enabledelayedexpansion

echo ======================================================================================================
echo 🧪 REE AI - Comprehensive Flow Testing
echo ======================================================================================================
echo.

REM Check if Docker is running
docker info >NUL 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Start services if not running
echo 📦 Checking services...
curl -s http://localhost:8000/health >NUL 2>&1
if errorlevel 1 (
    echo 🚀 Starting services...
    docker-compose --profile real up -d

    echo ⏳ Waiting for services to be healthy (30s)...
    timeout /t 30 /nobreak >NUL
)

REM Verify critical services
echo ✓ Verifying services...

set all_healthy=1

curl -s http://localhost:8000/health >NUL 2>&1
if not errorlevel 1 (
    echo   ✅ Service Registry
) else (
    echo   ❌ Service Registry (port 8000 not responding)
    set all_healthy=0
)

curl -s http://localhost:8090/health >NUL 2>&1
if not errorlevel 1 (
    echo   ✅ Orchestrator
) else (
    echo   ❌ Orchestrator (port 8090 not responding)
    set all_healthy=0
)

curl -s http://localhost:8083/health >NUL 2>&1
if not errorlevel 1 (
    echo   ✅ Classification
) else (
    echo   ❌ Classification (port 8083 not responding)
    set all_healthy=0
)

curl -s http://localhost:8084/health >NUL 2>&1
if not errorlevel 1 (
    echo   ✅ Extraction
) else (
    echo   ❌ Extraction (port 8084 not responding)
    set all_healthy=0
)

curl -s http://localhost:8086/health >NUL 2>&1
if not errorlevel 1 (
    echo   ✅ Completeness
) else (
    echo   ❌ Completeness (port 8086 not responding)
    set all_healthy=0
)

curl -s http://localhost:8081/health >NUL 2>&1
if not errorlevel 1 (
    echo   ✅ DB Gateway
) else (
    echo   ❌ DB Gateway (port 8081 not responding)
    set all_healthy=0
)

if !all_healthy! == 0 (
    echo.
    echo ❌ Some services are not healthy. Please check logs:
    echo   docker-compose logs -f orchestrator
    exit /b 1
)

echo.
echo ✅ All services healthy!
echo.

REM Run tests
echo 🧪 Running comprehensive flow tests...
echo.

docker run --rm --network host -v "%cd%:/app" -w /app python:3.11-slim bash -c "pip install -q asyncpg httpx && python tests/test_flow_comprehensive.py"

set exit_code=%errorlevel%

echo.
if %exit_code% == 0 (
    echo ✅ All tests completed!
) else (
    echo ❌ Tests failed with exit code %exit_code%
)

echo.
echo ======================================================================================================
echo 📁 Test results saved to: flow_test_results_*.json
echo ======================================================================================================

exit /b %exit_code%
