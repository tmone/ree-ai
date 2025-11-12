@echo off
REM Test deployment status script for Windows

echo 🧪 Testing REE AI Deployment Status
echo ====================================
echo.

echo 🔍 Testing Production Deployment...
echo Server: 192.168.1.11
echo.

echo 📊 Production Services (192.168.1.11):
echo ======================================

REM Test Open WebUI
echo Testing Open WebUI...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.1.11:3000' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Core Gateway
echo Testing Core Gateway...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.1.11:8080/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Service Registry
echo Testing Service Registry...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.1.11:8000/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Orchestrator
echo Testing Orchestrator...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.1.11:8090/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test RAG Service
echo Testing RAG Service...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.1.11:8091/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test Admin Dashboard
echo Testing Admin Dashboard...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.1.11:3002' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

echo.
echo 🖥️ WSL Test Services (localhost):
echo ==================================

REM Test WSL Open WebUI
echo Testing WSL Open WebUI...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:4000' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test WSL Core Gateway
echo Testing WSL Core Gateway...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9080/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test WSL Orchestrator
echo Testing WSL Orchestrator...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9090/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

REM Test WSL RAG Service
echo Testing WSL RAG Service...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:9091/health' -TimeoutSec 10 -UseBasicParsing; Write-Host '✅ OK' } catch { Write-Host '❌ FAIL' }"

echo.
echo 🎯 Summary:
echo ===========
echo If most tests show ✅ OK, your deployment is successful!
echo.
echo 🌐 Access URLs:
echo   - Production: http://192.168.1.11:3000
echo   - WSL Test: http://localhost:4000
echo.
echo 🔗 Useful Links:
echo   - GitHub Actions: https://github.com/tmone/ree-ai/actions
echo   - Production API: http://192.168.1.11:8080
echo   - WSL Test API: http://localhost:9080

pause