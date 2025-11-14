@echo off
REM =============================================================================
REM Master Data Extraction System - Deployment Script (Windows)
REM =============================================================================

setlocal enabledelayedexpansion

REM Configuration
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set ENV_FILE=%PROJECT_ROOT%\.env

set POSTGRES_CONTAINER=ree-ai-postgres
set EXTRACTION_SERVICE_PORT=8084
set CRAWLER_SERVICE_PORT=8095
set HEALTH_CHECK_RETRIES=30
set HEALTH_CHECK_DELAY=2

echo =======================================================================
echo   Master Data Extraction System - Deployment (Windows)
echo =======================================================================
echo.

REM =============================================================================
REM Step 1: Check prerequisites
REM =============================================================================

echo [INFO] Step 1/7: Checking prerequisites...

where docker >NUL 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

where docker-compose >NUL 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] docker-compose is not installed.
    exit /b 1
)

if not exist "%ENV_FILE%" (
    echo [ERROR] .env file not found at %ENV_FILE%
    echo [INFO] Please copy .env.example to .env and configure it
    exit /b 1
)

echo [INFO] All prerequisites met
echo.

REM =============================================================================
REM Step 2: Start infrastructure
REM =============================================================================

echo [INFO] Step 2/7: Starting infrastructure services...

cd /d "%PROJECT_ROOT%"
docker-compose up -d postgres redis

REM Wait for PostgreSQL
echo [INFO] Waiting for PostgreSQL to be ready...
set retries=0
:wait_postgres
docker exec %POSTGRES_CONTAINER% pg_isready -U ree_ai_user -d ree_ai >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] PostgreSQL is ready!
    goto postgres_ready
)

set /a retries+=1
if %retries% geq %HEALTH_CHECK_RETRIES% (
    echo [ERROR] PostgreSQL failed to become ready
    exit /b 1
)

echo [WARNING] PostgreSQL not ready yet (attempt %retries%/%HEALTH_CHECK_RETRIES%)...
timeout /t %HEALTH_CHECK_DELAY% /nobreak >NUL
goto wait_postgres

:postgres_ready
echo [INFO] Infrastructure services started
echo.

REM =============================================================================
REM Step 3: Run migrations
REM =============================================================================

echo [INFO] Step 3/7: Running database migrations...

echo [INFO] Creating master data schema...
docker exec -i %POSTGRES_CONTAINER% psql -U ree_ai_user -d ree_ai < "%PROJECT_ROOT%\database\migrations\001_create_master_data_schema.sql"

echo [INFO] Seeding master data...
docker exec -i %POSTGRES_CONTAINER% psql -U ree_ai_user -d ree_ai < "%PROJECT_ROOT%\database\migrations\002_seed_master_data.sql"

echo [INFO] Database migrations completed
echo.

REM =============================================================================
REM Step 4: Verify schema
REM =============================================================================

echo [INFO] Step 4/7: Verifying database schema...

for %%t in (cities districts property_types amenities directions furniture_types pending_master_data) do (
    echo [INFO] Checking table '%%t'...
    docker exec %POSTGRES_CONTAINER% psql -U ree_ai_user -d ree_ai -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='%%t';" >NUL
)

echo [INFO] Schema verification completed
echo.

REM =============================================================================
REM Step 5: Start services
REM =============================================================================

echo [INFO] Step 5/7: Starting master data services...

docker-compose up -d attribute-extraction crawler-service

echo [INFO] Services started
echo.

REM =============================================================================
REM Step 6: Health checks
REM =============================================================================

echo [INFO] Step 6/7: Running health checks...

REM Wait for Attribute Extraction Service
echo [INFO] Waiting for Attribute Extraction Service...
set retries=0
:wait_extraction
curl -sf http://localhost:%EXTRACTION_SERVICE_PORT%/health >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Attribute Extraction Service is ready!
    goto extraction_ready
)

set /a retries+=1
if %retries% geq %HEALTH_CHECK_RETRIES% (
    echo [ERROR] Attribute Extraction Service failed to become ready
    exit /b 1
)

echo [WARNING] Service not ready yet (attempt %retries%/%HEALTH_CHECK_RETRIES%)...
timeout /t %HEALTH_CHECK_DELAY% /nobreak >NUL
goto wait_extraction

:extraction_ready

REM Wait for Crawler Service
echo [INFO] Waiting for Crawler Service...
set retries=0
:wait_crawler
curl -sf http://localhost:%CRAWLER_SERVICE_PORT%/health >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Crawler Service is ready!
    goto crawler_ready
)

set /a retries+=1
if %retries% geq %HEALTH_CHECK_RETRIES% (
    echo [ERROR] Crawler Service failed to become ready
    exit /b 1
)

echo [WARNING] Service not ready yet (attempt %retries%/%HEALTH_CHECK_RETRIES%)...
timeout /t %HEALTH_CHECK_DELAY% /nobreak >NUL
goto wait_crawler

:crawler_ready
echo [INFO] All services healthy
echo.

REM =============================================================================
REM Step 7: Smoke tests
REM =============================================================================

echo [INFO] Step 7/7: Running smoke tests...

echo [INFO] Testing extraction endpoint...
curl -sf -X POST http://localhost:%EXTRACTION_SERVICE_PORT%/extract-with-master-data ^
    -H "Content-Type: application/json" ^
    -d "{\"text\": \"Can ho 2PN Quan 1\", \"confidence_threshold\": 0.7}" >NUL

if %ERRORLEVEL% equ 0 (
    echo [INFO] Extraction endpoint working
) else (
    echo [ERROR] Extraction endpoint test failed!
    exit /b 1
)

echo [INFO] Testing crawler endpoint...
curl -sf http://localhost:%CRAWLER_SERVICE_PORT%/crawlers >NUL

if %ERRORLEVEL% equ 0 (
    echo [INFO] Crawler endpoint working
) else (
    echo [ERROR] Crawler endpoint test failed!
    exit /b 1
)

echo [INFO] Smoke tests completed
echo.

REM =============================================================================
REM Success
REM =============================================================================

echo =======================================================================
echo   Deployment Completed Successfully!
echo =======================================================================
echo.
echo Services available at:
echo   - Attribute Extraction: http://localhost:%EXTRACTION_SERVICE_PORT%
echo   - Crawler Service: http://localhost:%CRAWLER_SERVICE_PORT%
echo.
echo API Documentation:
echo   - http://localhost:%EXTRACTION_SERVICE_PORT%/docs
echo   - http://localhost:%CRAWLER_SERVICE_PORT%/docs
echo.
echo Next steps:
echo   1. Run integration tests: pytest tests/integration/
echo   2. Check service logs: docker-compose logs -f attribute-extraction
echo   3. Start crawling: curl -X POST http://localhost:%CRAWLER_SERVICE_PORT%/crawl ...
echo.

exit /b 0
