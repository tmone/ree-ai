# ============================================================================
# REE AI Platform - Backup Setup Helper Script (Windows PowerShell)
# ============================================================================
#
# DESCRIPTION:
#   Interactive setup script to create backup configuration and test backups.
#   Walks through configuration options and validates the setup.
#
# USAGE:
#   .\backup-setup.ps1
#
# FEATURES:
#   - Interactive configuration wizard
#   - Configuration validation
#   - Backup testing
#   - Windows Task Scheduler setup
#
# ============================================================================

param(
    [switch]$Help
)

# Check execution policy
if ((Get-ExecutionPolicy) -eq "Restricted") {
    Write-Host "PowerShell execution policy is Restricted." -ForegroundColor Yellow
    Write-Host "To enable script execution, run:" -ForegroundColor Yellow
    Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

# Colors
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error-Custom { Write-Host $args -ForegroundColor Red }

Write-Info "=================================="
Write-Info "REE AI Platform - Backup Setup"
Write-Info "==================================`n"

# Check if .backup.env exists
$EnvFile = Join-Path $ScriptDir ".backup.env"
if (Test-Path $EnvFile) {
    Write-Warning "Warning: .backup.env already exists"
    $response = Read-Host "Do you want to reconfigure? (y/n)"
    if ($response -ne "y") {
        Write-Info "Using existing configuration"
        exit 0
    }
}

# PostgreSQL Configuration
Write-Info "`nPostgreSQL Configuration"
$pg_host = Read-Host "PostgreSQL Host [localhost]"
$pg_host = if ($pg_host) { $pg_host } else { "localhost" }

$pg_port = Read-Host "PostgreSQL Port [5432]"
$pg_port = if ($pg_port) { $pg_port } else { "5432" }

$pg_db = Read-Host "PostgreSQL Database [ree_ai]"
$pg_db = if ($pg_db) { $pg_db } else { "ree_ai" }

$pg_user = Read-Host "PostgreSQL User [ree_ai_user]"
$pg_user = if ($pg_user) { $pg_user } else { "ree_ai_user" }

$pg_password = Read-Host "PostgreSQL Password" -AsSecureString
$pg_password_plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($pg_password)
)

if (-not $pg_password_plain) {
    Write-Error-Custom "Error: Password is required"
    exit 1
}

# Backup Configuration
Write-Info "`nBackup Configuration"
$backup_dir = Read-Host "Backup Directory [./backups]"
$backup_dir = if ($backup_dir) { $backup_dir } else { ".\backups" }

$retention_days = Read-Host "Retention Days [30]"
$retention_days = if ($retention_days) { $retention_days } else { "30" }

# OpenSearch
Write-Info "`nOpenSearch Configuration"
$response = Read-Host "Enable OpenSearch backup? (y/n) [y]"
$opensearch_enabled = if ($response -eq "n") { "false" } else { "true" }

if ($opensearch_enabled -eq "true") {
    $os_host = Read-Host "OpenSearch Host [localhost]"
    $os_host = if ($os_host) { $os_host } else { "localhost" }
} else {
    $os_host = "localhost"
}

# S3
Write-Info "`nS3 Configuration"
$response = Read-Host "Enable S3 upload? (y/n) [n]"
$s3_enabled = if ($response -eq "y") { "true" } else { "false" }

$s3_bucket = ""
$s3_region = "us-east-1"
$aws_key_id = ""
$aws_secret_key = ""

if ($s3_enabled -eq "true") {
    $s3_bucket = Read-Host "S3 Bucket"
    $s3_region = Read-Host "S3 Region [us-east-1]"
    $s3_region = if ($s3_region) { $s3_region } else { "us-east-1" }
    $aws_key_id = Read-Host "AWS Access Key ID"
    $aws_secret = Read-Host "AWS Secret Access Key" -AsSecureString
    $aws_secret_key = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($aws_secret)
    )
}

# Email
Write-Info "`nEmail Notifications"
$response = Read-Host "Enable email notifications? (y/n) [n]"
$email_enabled = if ($response -eq "y") { "true" } else { "false" }

$email_recipient = ""
$smtp_server = ""
$smtp_port = "587"
$smtp_user = ""
$smtp_password = ""

if ($email_enabled -eq "true") {
    $email_recipient = Read-Host "Email Recipient"
    $smtp_server = Read-Host "SMTP Server"
    $smtp_port = Read-Host "SMTP Port [587]"
    $smtp_port = if ($smtp_port) { $smtp_port } else { "587" }
    $smtp_user = Read-Host "SMTP User"
    $smtp_password_sec = Read-Host "SMTP Password" -AsSecureString
    $smtp_password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($smtp_password_sec)
    )
}

# Create configuration file
Write-Info "`nCreating configuration file..."

$config_content = @"
# REE AI Platform - Backup Configuration
# Generated by backup-setup.ps1 on $(Get-Date)

# Backup Location
BACKUP_DIR=$backup_dir

# PostgreSQL Configuration
POSTGRES_HOST=$pg_host
POSTGRES_PORT=$pg_port
POSTGRES_DB=$pg_db
POSTGRES_USER=$pg_user
POSTGRES_PASSWORD=$pg_password_plain

# OpenSearch Configuration
OPENSEARCH_ENABLED=$opensearch_enabled
OPENSEARCH_HOST=$os_host
OPENSEARCH_PORT=9200

# S3 Configuration
S3_ENABLED=$s3_enabled
S3_BUCKET=$s3_bucket
S3_REGION=$s3_region
S3_PREFIX=ree-ai-backups
AWS_ACCESS_KEY_ID=$aws_key_id
AWS_SECRET_ACCESS_KEY=$aws_secret_key

# Backup Retention
RETENTION_DAYS=$retention_days

# Email Notifications
ENABLE_EMAIL=$email_enabled
EMAIL_RECIPIENT=$email_recipient
SMTP_SERVER=$smtp_server
SMTP_PORT=$smtp_port
SMTP_USER=$smtp_user
SMTP_PASSWORD=$smtp_password

# Logging
LOG_FILE=$ScriptDir\backup.log

# Other Settings
DRY_RUN=false
DROP_DB_BEFORE_RESTORE=false
"@

Set-Content -Path $EnvFile -Value $config_content -Encoding UTF8
Write-Success "Configuration file created: $EnvFile"

# Test configuration
Write-Info "`nTesting configuration..."

# Load config
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+?)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

# Check prerequisites
Write-Info "Checking prerequisites..."
$missing_tools = @()

@("pg_dump", "psql") | ForEach-Object {
    if (-not (Get-Command $_ -ErrorAction SilentlyContinue)) {
        $missing_tools += $_
    }
}

if ($missing_tools.Count -gt 0) {
    Write-Warning "Warning: Missing tools: $($missing_tools -join ', ')"
    Write-Warning "Please install PostgreSQL client tools before running backups"
} else {
    Write-Success "All prerequisites found"
}

# Test PostgreSQL connection
Write-Info "Testing PostgreSQL connection..."
try {
    $Env:PGPASSWORD = $pg_password_plain
    & psql -h $pg_host -p $pg_port -U $pg_user -d $pg_db -c "SELECT version();" 2>&1 | Out-Null
    Write-Success "PostgreSQL connection successful"
} catch {
    Write-Error-Custom "Failed to connect to PostgreSQL"
    Write-Error-Custom "Please verify connection parameters"
}

# Test OpenSearch connection if enabled
if ($opensearch_enabled -eq "true") {
    Write-Info "Testing OpenSearch connection..."
    try {
        $response = Invoke-RestMethod -Uri "http://$os_host:9200/" -Method Get -ErrorAction Stop
        Write-Success "OpenSearch connection successful"
    } catch {
        Write-Warning "Warning: Could not connect to OpenSearch"
    }
}

# Setup summary
Write-Info "`n=================================="
Write-Info "Setup Summary"
Write-Info "=================================="
Write-Host "PostgreSQL Host: $pg_host`:$pg_port"
Write-Host "Database: $pg_db"
Write-Host "Backup Directory: $backup_dir"
Write-Host "Retention: $retention_days days"
Write-Host "OpenSearch: $opensearch_enabled"
Write-Host "S3 Upload: $s3_enabled"
Write-Host "Email Notifications: $email_enabled"

# Option to setup task scheduler
Write-Info "`nWindows Task Scheduler Setup"
$response = Read-Host "Setup daily backup task? (y/n)"

if ($response -eq "y") {
    Write-Info "Enter the time for daily backup (HH:mm) [02:00]:"
    $backup_time = Read-Host "> "
    if (-not $backup_time) {
        $backup_time = "02:00"
    }

    # Create PowerShell wrapper script
    $wrapper_script = Join-Path $ScriptDir "backup-task.ps1"
    $wrapper_content = @"
# Auto-generated backup task wrapper
`$env:POSTGRES_PASSWORD = "$pg_password_plain"
Set-Location "$RootDir"
& ".\scripts\backup.ps1"
"@

    Set-Content -Path $wrapper_script -Value $wrapper_content -Encoding UTF8
    Write-Success "Backup wrapper script created: $wrapper_script"

    # Create task
    try {
        $taskName = "REE-AI-Backup-Daily"

        # Check if task exists
        if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
            Write-Warning "Task '$taskName' already exists"
            $response = Read-Host "Do you want to overwrite it? (y/n)"
            if ($response -ne "y") {
                Write-Info "Skipping task creation"
            } else {
                Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
                Write-Info "Old task removed"
            }
        }

        # Create new task
        $trigger = New-ScheduledTaskTrigger -Daily -At $backup_time
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -File `"$wrapper_script`""
        $settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -AllowStartIfOnBatteries $false

        Register-ScheduledTask -TaskName $taskName `
            -Trigger $trigger `
            -Action $action `
            -Settings $settings `
            -RunLevel Highest `
            -Force | Out-Null

        Write-Success "Task Scheduler job created: $taskName"
        Write-Info "Schedule: Daily at $backup_time"
        Write-Info "To view: Get-ScheduledTask -TaskName '$taskName'"
        Write-Info "To remove: Unregister-ScheduledTask -TaskName '$taskName'"
    } catch {
        Write-Error-Custom "Failed to create Task Scheduler job: $_"
        Write-Warning "You may need to run PowerShell as Administrator"
    }
}

Write-Success "`nSetup completed!"
Write-Info @"
`nNext steps:
1. Test backup: cd $RootDir; .\scripts\backup.ps1 -DryRun
2. Run backup: cd $RootDir; .\scripts\backup.ps1
3. List backups: cd $RootDir; .\scripts\restore.sh list
4. Restore: cd $RootDir; .\scripts\restore.sh restore latest

For more information, see: $ScriptDir\BACKUP_README.md
"@
