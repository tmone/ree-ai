# REE AI - Integration Test Script (PowerShell)
# Tests all services end-to-end

Write-Host "🧪 REE AI - Integration Testing" -ForegroundColor Cyan
Write-Host "================================`n"

$PASSED = 0
$FAILED = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Data = ""
    )

    Write-Host "Testing $Name... " -NoNewline

    try {
        if ($Method -eq "POST") {
            $response = Invoke-WebRequest -Uri $Url -Method POST `
                -ContentType "application/json" `
                -Body $Data `
                -TimeoutSec 5 `
                -ErrorAction Stop
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method GET `
                -TimeoutSec 5 `
                -ErrorAction Stop
        }

        if ($response.StatusCode -eq 200) {
            Write-Host "✅ PASS" -ForegroundColor Green -NoNewline
            Write-Host " (HTTP $($response.StatusCode))"
            $script:PASSED++
            return $true
        }
    } catch {
        Write-Host "❌ FAIL" -ForegroundColor Red -NoNewline
        Write-Host " ($($_.Exception.Message))"
        $script:FAILED++
        return $false
    }
}

Write-Host "📍 Step 1: Check Infrastructure"
Write-Host "--------------------------------"
Test-Endpoint -Name "OpenSearch" -Url "http://localhost:9200"
Write-Host ""

Write-Host "📍 Step 2: Check Mock Services"
Write-Host "-------------------------------"
Test-Endpoint -Name "Mock Core Gateway Health" -Url "http://localhost:8000/mockserver/status"
Test-Endpoint -Name "Mock DB Gateway Health" -Url "http://localhost:8001/mockserver/status"
Write-Host ""

Write-Host "📍 Step 3: Test Mock Core Gateway"
Write-Host "----------------------------------"
$coreData = @'
{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}
'@
Test-Endpoint -Name "Mock Core Gateway - Chat Completions" `
    -Url "http://localhost:8000/v1/chat/completions" `
    -Method "POST" `
    -Data $coreData
Write-Host ""

Write-Host "📍 Step 4: Test Mock DB Gateway"
Write-Host "--------------------------------"
$dbData = @'
{"query":"Tìm nhà","filters":{},"limit":10}
'@
Test-Endpoint -Name "Mock DB Gateway - Search" `
    -Url "http://localhost:8001/search" `
    -Method "POST" `
    -Data $dbData
Write-Host ""

Write-Host "📍 Step 5: Check Real Services (if running)"
Write-Host "--------------------------------------------"
Test-Endpoint -Name "Core Gateway Health" -Url "http://localhost:8080/health" | Out-Null
if (-not $?) {
    Write-Host "⚠️  Core Gateway not running (use: docker-compose --profile real up)" -ForegroundColor Yellow
}
Test-Endpoint -Name "DB Gateway Health" -Url "http://localhost:8081/health" | Out-Null
if (-not $?) {
    Write-Host "⚠️  DB Gateway not running" -ForegroundColor Yellow
}
Test-Endpoint -Name "Semantic Chunking Health" -Url "http://localhost:8082/health" | Out-Null
if (-not $?) {
    Write-Host "⚠️  Semantic Chunking not running" -ForegroundColor Yellow
}
Write-Host ""

if ($FAILED -eq 0 -and $PASSED -gt 0) {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Total: $PASSED passed, $FAILED failed"
    Write-Host ""
    Write-Host "✅ Infrastructure is ready for development!" -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "⚠️  SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "Total: $PASSED passed, $FAILED failed"
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "1. Check Docker services: docker-compose ps"
    Write-Host "2. Check logs: docker-compose logs"
    Write-Host "3. Restart services: docker-compose --profile mock up -d"
    Write-Host ""
    exit 1
}
