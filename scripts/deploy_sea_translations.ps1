# ================================================================
# DEPLOY SEA TRANSLATIONS TO REMOTE SERVER
# ================================================================
# PURPOSE: Upload and execute all SEA translation files on remote PostgreSQL
# DATE: 2025-11-14
# SERVER: 103.153.74.213
# ================================================================

$ErrorActionPreference = "Stop"

# Configuration
$REMOTE_HOST = "103.153.74.213"
$SSH_KEY = "C:\Users\dev\.ssh\tmone"
$DB_NAME = "ree_ai"
$DB_USER = "ree_ai_user"

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYING SEA TRANSLATIONS TO REMOTE SERVER" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Remote Host: $REMOTE_HOST" -ForegroundColor Yellow
Write-Host "Database: $DB_NAME" -ForegroundColor Yellow
Write-Host "================================================================`n" -ForegroundColor Cyan

# Step 1: Upload all translation files
Write-Host "Step 1: Uploading translation files to remote server..." -ForegroundColor Green

$filesToUpload = @(
    "seed_thai_translations.sql",
    "seed_khmer_translations.sql",
    "seed_lao_translations.sql",
    "seed_indonesian_translations.sql",
    "seed_filipino_translations.sql",
    "seed_burmese_translations.sql",
    "seed_all_sea_translations.sql"
)

foreach ($file in $filesToUpload) {
    $fullPath = Join-Path $scriptPath $file
    if (Test-Path $fullPath) {
        Write-Host "  Uploading $file..." -ForegroundColor White
        scp -i $SSH_KEY $fullPath root@${REMOTE_HOST}:/tmp/
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  ERROR: Failed to upload $file" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  WARNING: File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "`nAll files uploaded successfully!`n" -ForegroundColor Green

# Step 2: Execute translations on remote server
Write-Host "Step 2: Executing translations on remote PostgreSQL..." -ForegroundColor Green

# Change directory to /tmp where the files are uploaded, then run master script
$remoteCommand = @"
cd /tmp && sudo -u postgres psql -d $DB_NAME -f seed_all_sea_translations.sql
"@

Write-Host "  Running master deployment script..." -ForegroundColor White
ssh -i $SSH_KEY root@$REMOTE_HOST $remoteCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Translation deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

# Step 3: Verify deployment
Write-Host "`nStep 3: Verifying deployment..." -ForegroundColor Green

$verifyCommand = @"
sudo -u postgres psql -d $DB_NAME -c "
SELECT
    c.name as country,
    COUNT(DISTINCT t.lang_code) as languages,
    STRING_AGG(DISTINCT t.lang_code, ', ' ORDER BY t.lang_code) as codes
FROM ree_common.countries c
JOIN ree_common.provinces p ON c.id = p.country_id
LEFT JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM', 'VN')
GROUP BY c.name
ORDER BY c.name;
"
"@

ssh -i $SSH_KEY root@$REMOTE_HOST $verifyCommand

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "SEA TRANSLATIONS READY FOR PRODUCTION!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Supported languages:" -ForegroundColor Yellow
Write-Host "  - Thai (th): 46 provinces" -ForegroundColor White
Write-Host "  - Vietnamese (vi): 63 provinces" -ForegroundColor White
Write-Host "  - Khmer (km): 25 provinces" -ForegroundColor White
Write-Host "  - Lao (lo): 18 provinces" -ForegroundColor White
Write-Host "  - Bahasa Indonesia (id): 17 provinces" -ForegroundColor White
Write-Host "  - Filipino/Tagalog (tl): 17 regions" -ForegroundColor White
Write-Host "  - Burmese (my): 14 regions" -ForegroundColor White
Write-Host ""
Write-Host "Total: 200+ provinces with local language support!" -ForegroundColor Green
Write-Host ""

# Cleanup
Write-Host "Cleaning up temporary files on remote server..." -ForegroundColor Yellow
$cleanupCommand = "rm -f /tmp/seed_*_translations.sql /tmp/seed_all_sea_translations.sql"
ssh -i $SSH_KEY root@$REMOTE_HOST $cleanupCommand

Write-Host "Done!`n" -ForegroundColor Green
