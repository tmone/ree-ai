@echo off
REM REE AI Frontend Build Script for Windows
REM Builds the custom Open WebUI frontend for production

echo.
echo ========================================
echo    REE AI Frontend Build Script
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found
    echo Please run this script from the project root directory
    exit /b 1
)

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed
    echo Please install Docker first: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check for --local flag
if "%1"=="--local" (
    echo.
    echo [INFO] Building locally with Node.js...

    REM Check if Node is installed
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Node.js is not installed
        echo Please install Node.js 18+ first
        exit /b 1
    )

    cd frontend\open-webui

    echo [INFO] Installing dependencies...
    call npm ci --force

    echo [INFO] Building frontend...
    call npm run build

    echo.
    echo [SUCCESS] Local build completed!
    echo Build output is in: frontend\open-webui\build\
    exit /b 0
)

REM Build Docker image
echo.
echo [INFO] Building Docker image...
echo This may take 10-15 minutes on first build...
echo.

docker compose build open-webui

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Docker image built successfully!
    echo.
    echo Next steps:
    echo 1. Start the frontend:
    echo    docker compose --profile real up -d open-webui
    echo.
    echo 2. Access the frontend:
    echo    http://localhost:3000
    echo.
    echo 3. View logs:
    echo    docker compose logs -f open-webui
    echo.
    echo 4. Stop the frontend:
    echo    docker compose stop open-webui
    echo.
    echo For local development without Docker:
    echo    scripts\build-frontend.bat --local
    echo    cd frontend\open-webui ^&^& npm run dev
) else (
    echo.
    echo [ERROR] Docker build failed
    exit /b 1
)
