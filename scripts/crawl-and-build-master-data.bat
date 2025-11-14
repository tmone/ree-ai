@echo off
REM =============================================================================
REM Crawl Real Estate Sites and Build Master Data (Windows)
REM =============================================================================

setlocal enabledelayedexpansion

REM Configuration
set CRAWLER_SERVICE_URL=http://localhost:8095
set EXTRACTION_SERVICE_URL=http://localhost:8084
set MAX_PAGES=20

echo =======================================================================
echo   Real Estate Data Crawler - Master Data Builder
echo =======================================================================
echo.
echo   This script will crawl real estate websites and automatically
echo   discover new master data (amenities, features, locations, etc.)
echo.
echo   Settings:
echo   - Sites: batdongsan, mogi
echo   - Max Pages: %MAX_PAGES% per site
echo   - Auto-Populate: Enabled
echo.
echo =======================================================================
echo.

REM =============================================================================
REM Pre-Flight Checks
REM =============================================================================

echo [INFO] Pre-Flight Checks
echo.

REM Check crawler service
curl -sf %CRAWLER_SERVICE_URL%/health >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Crawler Service is running
) else (
    echo [ERROR] Crawler Service is not running!
    echo [INFO] Please start it with: docker-compose up -d crawler-service
    exit /b 1
)

REM Check extraction service
curl -sf %EXTRACTION_SERVICE_URL%/health >NUL 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Extraction Service is running
) else (
    echo [WARNING] Extraction Service is not running (optional)
)

echo.

REM =============================================================================
REM Crawl Batdongsan
REM =============================================================================

echo =======================================================================
echo   Crawling: batdongsan
echo =======================================================================
echo [INFO] Max pages: %MAX_PAGES%
echo [INFO] Extract master data: YES
echo [INFO] Auto-populate: YES
echo.

echo [INFO] Starting crawl (this may take a few minutes)...

curl -X POST %CRAWLER_SERVICE_URL%/crawl ^
    -H "Content-Type: application/json" ^
    -d "{\"site\": \"batdongsan\", \"max_pages\": %MAX_PAGES%, \"extract_master_data\": true, \"auto_populate\": true}" ^
    -o crawl_result_batdongsan.json

if %ERRORLEVEL% equ 0 (
    echo [INFO] Crawl completed successfully!
    echo.
    type crawl_result_batdongsan.json
    echo.
) else (
    echo [ERROR] Crawl failed for batdongsan
)

echo.
echo [INFO] Waiting 10 seconds before next crawl...
timeout /t 10 /nobreak >NUL

REM =============================================================================
REM Crawl Mogi
REM =============================================================================

echo =======================================================================
echo   Crawling: mogi
echo =======================================================================
echo [INFO] Max pages: %MAX_PAGES%
echo.

echo [INFO] Starting crawl (this may take a few minutes)...

curl -X POST %CRAWLER_SERVICE_URL%/crawl ^
    -H "Content-Type: application/json" ^
    -d "{\"site\": \"mogi\", \"max_pages\": %MAX_PAGES%, \"extract_master_data\": true, \"auto_populate\": true}" ^
    -o crawl_result_mogi.json

if %ERRORLEVEL% equ 0 (
    echo [INFO] Crawl completed successfully!
    echo.
    type crawl_result_mogi.json
    echo.
) else (
    echo [ERROR] Crawl failed for mogi
)

echo.

REM =============================================================================
REM Master Data Status
REM =============================================================================

echo =======================================================================
echo   Master Data Status
echo =======================================================================
echo.

curl -sf "%EXTRACTION_SERVICE_URL%/admin/pending-items?status=pending&limit=20" -o pending_items.json

if %ERRORLEVEL% equ 0 (
    echo [INFO] Pending master data items:
    type pending_items.json
    echo.
) else (
    echo [WARNING] Could not retrieve pending items
)

REM =============================================================================
REM Next Steps
REM =============================================================================

echo =======================================================================
echo   Next Steps
echo =======================================================================
echo.
echo 1. Review pending master data items:
echo    curl http://localhost:%EXTRACTION_SERVICE_URL%/admin/pending-items?status=pending
echo.
echo 2. View crawl results:
echo    - Batdongsan: crawl_result_batdongsan.json
echo    - Mogi: crawl_result_mogi.json
echo.
echo 3. View master data growth in Grafana:
echo    http://localhost:3001/d/master-data-growth
echo.
echo 4. Run extraction test with new master data:
echo    curl -X POST http://localhost:%EXTRACTION_SERVICE_URL%/extract-with-master-data ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"text\": \"Can ho 2PN Quan 1\"}"
echo.

echo =======================================================================
echo   Crawl completed!
echo =======================================================================

REM Cleanup temp files
del crawl_result_batdongsan.json crawl_result_mogi.json pending_items.json 2>NUL

exit /b 0
