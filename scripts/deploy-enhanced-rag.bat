@echo off
REM Deploy Enhanced RAG Service (Windows)
REM This script switches from basic RAG to enhanced RAG with all advanced features

echo.
echo Deploying Enhanced RAG Service...
echo.

REM Check if docker-compose is available
where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: docker-compose not found. Please install Docker Compose.
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Created .env file. Please review and update settings.
)

REM Confirm deployment
echo This will deploy Enhanced RAG Service with:
echo   - Modular RAG operators (grading, reranking, query rewriting)
echo   - Agentic memory system (episodic, semantic, procedural)
echo   - Multi-agent coordination (supervisor + 4 specialists)
echo   - Self-reflection and quality control
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    exit /b 1
)

REM Stop existing RAG service
echo Stopping existing RAG service...
docker-compose stop rag-service 2>nul

REM Build RAG service
echo Building RAG service...
docker-compose build rag-service

REM Deploy Enhanced RAG (now default in docker-compose.yml)
echo Deploying Enhanced RAG service...
docker-compose up -d rag-service

REM Wait for service to be healthy
echo Waiting for service to be healthy...
timeout /t 5 /nobreak >nul

REM Health check
echo Checking service health...
curl -f http://localhost:8091/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Enhanced RAG service is healthy!
) else (
    echo Health check failed. Checking logs...
    docker-compose logs --tail=50 rag-service
    exit /b 1
)

REM Stats check
echo Checking advanced features...
curl -f http://localhost:8091/stats >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Advanced features are available!
    echo.
    echo Service Stats:
    curl -s http://localhost:8091/stats
) else (
    echo Warning: Stats endpoint not available
)

echo.
echo Enhanced RAG Service deployed successfully!
echo.
echo Next Steps:
echo   1. Test basic query:
echo      curl -X POST http://localhost:8091/query -H "Content-Type: application/json" -d "{\"query\": \"Tìm căn hộ 2PN Quận 2\", \"limit\": 5}"
echo.
echo   2. Test advanced query:
echo      curl -X POST http://localhost:8091/query -H "Content-Type: application/json" -d "{\"query\": \"Tìm căn hộ gần trường quốc tế\", \"user_id\": \"user123\", \"use_advanced_rag\": true, \"limit\": 5}"
echo.
echo   3. Monitor logs:
echo      docker-compose logs -f rag-service
echo.
echo   4. Rollback (if needed):
echo      scripts\rollback-basic-rag.bat
echo.

exit /b 0
