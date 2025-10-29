@echo off
echo ========================================
echo REE AI - Quick Start Script (Windows)
echo ========================================
echo.

echo [1/6] Checking Docker...
docker --version
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo.
echo [2/6] Building images (this may take 5-10 minutes)...
docker-compose --profile real build
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [3/6] Starting infrastructure (postgres, redis, opensearch)...
docker-compose up -d postgres redis opensearch ollama
timeout /t 30 /nobreak

echo.
echo [4/6] Starting core services...
docker-compose --profile real up -d service-registry core-gateway db-gateway auth-service
timeout /t 20 /nobreak

echo.
echo [5/6] Starting AI services...
docker-compose --profile real up -d orchestrator rag-service classification semantic-chunking attribute-extraction completeness-check price-suggestion reranking
timeout /t 20 /nobreak

echo.
echo [6/6] Starting gateway and frontend...
docker-compose --profile real up -d api-gateway admin-dashboard open-webui
timeout /t 15 /nobreak

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Services running:
docker ps --format "table {{.Names}}\t{{.Status}}"

echo.
echo Access URLs:
echo   Open WebUI:       http://localhost:3000
echo   API Gateway:      http://localhost:8888
echo   Admin Dashboard:  http://localhost:3002
echo   Grafana:          http://localhost:3001
echo.
echo Press any key to exit...
pause
