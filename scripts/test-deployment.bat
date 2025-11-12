@echo off
REM Quick deployment test script for Windows
REM Test the production deployment

set SERVER_IP=192.168.1.11
set TIMEOUT=10

echo 🧪 Testing REE AI Production Deployment
echo ======================================
echo Server: %SERVER_IP%
echo Timeout: %TIMEOUT%s per service
echo.

REM Test function using PowerShell
echo 🔍 Testing Services:
echo ===================

REM Test Open WebUI
echo Testing Open WebUI (http://%SERVER_IP%:3000)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:3000' -TimeoutSec %TIMEOUT% -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Core Gateway  
echo Testing Core Gateway (http://%SERVER_IP%:8080/health)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:8080/health' -TimeoutSec %TIMEOUT% -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Service Registry
echo Testing Service Registry (http://%SERVER_IP%:8000/health)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:8000/health' -TimeoutSec %TIMEOUT% -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Orchestrator
echo Testing Orchestrator (http://%SERVER_IP%:8090/health)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:8090/health' -TimeoutSec %TIMEOUT% -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test RAG Service
echo Testing RAG Service (http://%SERVER_IP%:8091/health)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:8091/health' -TimeoutSec %TIMEOUT% -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Admin Dashboard
echo Testing Admin Dashboard (http://%SERVER_IP%:3002)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://%SERVER_IP%:3002' -TimeoutSec %TIMEOUT% -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

echo.
echo 🔧 API Tests:
echo =============

REM Test Orchestrator API
echo Testing Orchestrator API...
powershell -Command "$body = @{user_id='test_user'; query='hello'} | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://%SERVER_IP%:8090/orchestrate' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec %TIMEOUT%; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

echo.
echo 🎯 Summary:
echo ===========
echo If most tests show ✅ OK, your deployment is successful!
echo.
echo 🌐 Access URLs:
echo   - Open WebUI: http://%SERVER_IP%:3000
echo   - Admin Dashboard: http://%SERVER_IP%:3002  
echo   - API Gateway: http://%SERVER_IP%:8080
echo.
echo 🔧 Debug commands (run in PowerShell/CMD):
echo   ssh tmone@%SERVER_IP% "cd ~/ree-ai && ./status-ree-ai.sh"
echo   ssh tmone@%SERVER_IP% "cd ~/ree-ai && ./logs-ree-ai.sh"

pause