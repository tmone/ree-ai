@echo off
REM Rollback to Basic RAG Service (Windows)
REM This script reverts from enhanced RAG back to basic RAG

echo.
echo Rolling back to Basic RAG Service...
echo.

REM Check if docker-compose is available
where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: docker-compose not found. Please install Docker Compose.
    exit /b 1
)

REM Confirm rollback
echo This will rollback to Basic RAG Service:
echo   - Simple 3-step pipeline (retrieve → augment → generate)
echo   - No memory, no agents, no advanced operators
echo   - Faster, simpler, but less intelligent
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Rollback cancelled.
    exit /b 1
)

REM Stop enhanced RAG service
echo Stopping Enhanced RAG service...
docker-compose -f docker-compose.yml -f docker-compose.enhanced-rag.yml down rag-service 2>nul

REM Start basic RAG service
echo Starting Basic RAG service...
docker-compose up -d rag-service

REM Wait for service to be healthy
echo Waiting for service to be healthy...
timeout /t 5 /nobreak >nul

REM Health check
echo Checking service health...
curl -f http://localhost:8091/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Basic RAG service is healthy!
) else (
    echo Health check failed. Checking logs...
    docker-compose logs --tail=50 rag-service
    exit /b 1
)

echo.
echo Rollback to Basic RAG completed successfully!
echo.
echo Next Steps:
echo   1. Test basic query:
echo      curl -X POST http://localhost:8091/query -H "Content-Type: application/json" -d "{\"query\": \"Tìm căn hộ 2PN Quận 2\", \"limit\": 5}"
echo.
echo   2. Monitor logs:
echo      docker-compose logs -f rag-service
echo.
echo   3. Re-deploy enhanced RAG (if needed):
echo      scripts\deploy-enhanced-rag.bat
echo.

exit /b 0
