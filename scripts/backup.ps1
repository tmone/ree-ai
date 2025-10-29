# ============================================================================
# REE AI Platform - Backup Automation Script (Windows PowerShell)
# ============================================================================
#
# DESCRIPTION:
#   Automated backup script for the REE AI platform with support for:
#   - PostgreSQL database backups
#   - OpenSearch indices backup (optional)
#   - Configuration files backup
#   - Automatic compression and timestamping
#   - S3 or local storage upload
#   - Automatic cleanup of old backups (30-day retention)
#   - Email notifications on failure
#
# USAGE:
#   .\backup.ps1                    # Standard backup
#   .\backup.ps1 -DryRun            # Dry run mode (no actual changes)
#   .\backup.ps1 -Help              # Display this help message
#
# EXECUTION POLICY:
#   If you encounter execution policy errors, run:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#
# CONFIGURATION:
#   Configure via environment variables or .backup.env file in script directory
#
# ENVIRONMENT VARIABLES:
#   BACKUP_DIR              - Local backup directory (default: .\backups)
#   POSTGRES_HOST           - PostgreSQL host (default: localhost)
#   POSTGRES_PORT           - PostgreSQL port (default: 5432)
#   POSTGRES_DB             - Database name to backup (default: ree_ai)
#   POSTGRES_USER           - PostgreSQL user (default: ree_ai_user)
#   POSTGRES_PASSWORD       - PostgreSQL password (required)
#   OPENSEARCH_HOST         - OpenSearch host (default: localhost)
#   OPENSEARCH_PORT         - OpenSearch port (default: 9200)
#   OPENSEARCH_ENABLED      - Enable OpenSearch backup (default: true)
#   BACKUP_CONFIG_FILES     - Config files to backup (semicolon-separated)
#   S3_ENABLED              - Enable S3 upload (default: false)
#   S3_BUCKET               - S3 bucket name
#   S3_REGION               - AWS region
#   AWS_ACCESS_KEY_ID       - AWS access key
#   AWS_SECRET_ACCESS_KEY   - AWS secret key
#   S3_PREFIX               - S3 prefix path (default: ree-ai-backups)
#   RETENTION_DAYS          - Days to retain backups (default: 30)
#   ENABLE_EMAIL            - Enable email notifications (default: false)
#   EMAIL_RECIPIENT         - Email recipient for notifications
#   SMTP_SERVER             - SMTP server address
#   SMTP_PORT               - SMTP port (default: 587)
#   SMTP_USER               - SMTP username
#   SMTP_PASSWORD           - SMTP password
#   LOG_FILE                - Log file path (default: .\backup.log)
#   DRY_RUN                 - Dry run mode (default: false)
#
# REQUIREMENTS:
#   - PowerShell 5.0 or higher
#   - PostgreSQL client tools (psql, pg_dump)
#   - 7-Zip or similar compression utility
#   - Optional: AWS Tools for PowerShell for S3 uploads
#   - Optional: SMTP server access for email notifications
#
# EXIT CODES:
#   0   - Success
#   1   - General error
#   2   - Configuration error
#   3   - Backup error
#   4   - Upload error
#   5   - Cleanup error
#
# ============================================================================

param(
    [switch]$DryRun,
    [switch]$Help
)

# Display help
if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

# Load environment variables from .backup.env if exists
$EnvFile = Join-Path $ScriptDir ".backup.env"
if (Test-Path $EnvFile) {
    Write-Host "Loading configuration from: $EnvFile"
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+?)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

# Default configuration
$BackupDir = if ([System.Environment]::GetEnvironmentVariable("BACKUP_DIR")) { [System.Environment]::GetEnvironmentVariable("BACKUP_DIR") } else { "." }
$BackupBaseDir = Join-Path $BackupDir "backups"
$PostgresHost = [System.Environment]::GetEnvironmentVariable("POSTGRES_HOST") -or "localhost"
$PostgresPort = [System.Environment]::GetEnvironmentVariable("POSTGRES_PORT") -or "5432"
$PostgresDb = [System.Environment]::GetEnvironmentVariable("POSTGRES_DB") -or "ree_ai"
$PostgresUser = [System.Environment]::GetEnvironmentVariable("POSTGRES_USER") -or "ree_ai_user"
$PostgresPassword = [System.Environment]::GetEnvironmentVariable("POSTGRES_PASSWORD")
$OpenSearchHost = [System.Environment]::GetEnvironmentVariable("OPENSEARCH_HOST") -or "localhost"
$OpenSearchPort = [System.Environment]::GetEnvironmentVariable("OPENSEARCH_PORT") -or "9200"
$OpenSearchEnabled = [System.Environment]::GetEnvironmentVariable("OPENSEARCH_ENABLED") -or "true"
$S3Enabled = [System.Environment]::GetEnvironmentVariable("S3_ENABLED") -or "false"
$S3Bucket = [System.Environment]::GetEnvironmentVariable("S3_BUCKET")
$S3Region = [System.Environment]::GetEnvironmentVariable("S3_REGION") -or "us-east-1"
$S3Prefix = [System.Environment]::GetEnvironmentVariable("S3_PREFIX") -or "ree-ai-backups"
$AWSAccessKeyId = [System.Environment]::GetEnvironmentVariable("AWS_ACCESS_KEY_ID")
$AWSSecretAccessKey = [System.Environment]::GetEnvironmentVariable("AWS_SECRET_ACCESS_KEY")
$RetentionDays = [System.Environment]::GetEnvironmentVariable("RETENTION_DAYS") -or "30"
$EnableEmail = [System.Environment]::GetEnvironmentVariable("ENABLE_EMAIL") -or "false"
$EmailRecipient = [System.Environment]::GetEnvironmentVariable("EMAIL_RECIPIENT")
$SmtpServer = [System.Environment]::GetEnvironmentVariable("SMTP_SERVER")
$SmtpPort = [System.Environment]::GetEnvironmentVariable("SMTP_PORT") -or "587"
$SmtpUser = [System.Environment]::GetEnvironmentVariable("SMTP_USER")
$SmtpPassword = [System.Environment]::GetEnvironmentVariable("SMTP_PASSWORD")
$LogFile = if ([System.Environment]::GetEnvironmentVariable("LOG_FILE")) { [System.Environment]::GetEnvironmentVariable("LOG_FILE") } else { "." }

# Set log file path
if ($LogFile -eq ".") {
    $LogFile = Join-Path $ScriptDir "backup.log"
}

# Create timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "ree-ai-backup_${Timestamp}"

# Color codes for output
$Colors = @{
    Info    = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Debug   = "Gray"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoConsole
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"

    # Write to file
    Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue

    # Write to console
    if (-not $NoConsole) {
        $Color = $Colors[$Level]
        if ($Color) {
            Write-Host "[$Level] $Message" -ForegroundColor $Color
        } else {
            Write-Host "[$Level] $Message"
        }
    }
}

function Write-Info { Write-Log -Message $args -Level "INFO" }
function Write-Success { Write-Log -Message $args -Level "SUCCESS" }
function Write-Warning { Write-Log -Message $args -Level "WARNING" }
function Write-Error-Custom { Write-Log -Message $args -Level "ERROR" }

function Show-Help {
    @"
REE AI Platform Backup Script

SYNOPSIS:
    .\backup.ps1 [-DryRun] [-Help]

DESCRIPTION:
    Automated backup script for the REE AI platform with support for:
    - PostgreSQL database backups
    - OpenSearch indices backup (optional)
    - Configuration files backup
    - Automatic compression and timestamping
    - S3 or local storage upload
    - Automatic cleanup of old backups

PARAMETERS:
    -DryRun
        Run in dry-run mode (preview without making actual changes)

    -Help
        Display this help message

ENVIRONMENT VARIABLES:
    Required:
        POSTGRES_PASSWORD       PostgreSQL password

    Optional:
        BACKUP_DIR              Local backup directory (default: .\backups)
        POSTGRES_HOST           PostgreSQL host (default: localhost)
        POSTGRES_PORT           PostgreSQL port (default: 5432)
        POSTGRES_DB             Database name (default: ree_ai)
        POSTGRES_USER           PostgreSQL user (default: ree_ai_user)
        OPENSEARCH_ENABLED      Enable OpenSearch backup (default: true)
        S3_ENABLED              Enable S3 upload (default: false)
        S3_BUCKET               S3 bucket name
        RETENTION_DAYS          Days to retain backups (default: 30)
        ENABLE_EMAIL            Enable email notifications (default: false)
        LOG_FILE                Log file path (default: .\backup.log)

EXAMPLES:
    # Standard backup with retention cleanup
    .\backup.ps1

    # Dry run mode (preview without backup)
    .\backup.ps1 -DryRun

    # Backup with S3 upload
    `$env:S3_ENABLED = "true"
    `$env:S3_BUCKET = "my-bucket"
    .\backup.ps1

    # Backup with email on failure
    `$env:ENABLE_EMAIL = "true"
    `$env:EMAIL_RECIPIENT = "admin@example.com"
    .\backup.ps1

NOTES:
    For detailed configuration options, see the script comments at the top of the file.
"@
}

function DryRunInfo {
    param([string]$Message)
    if ($DryRun) {
        Write-Warning "[DRY-RUN] $Message"
    }
}

function ExecuteCommand {
    param(
        [string]$Command,
        [string]$Description
    )

    if ($DryRun) {
        DryRunInfo "Would execute: $Description"
        return $true
    }

    try {
        Write-Info "Executing: $Description"
        Invoke-Expression $Command | Out-Null
        return $true
    } catch {
        Write-Error-Custom "Command failed: $_"
        return $false
    }
}

function SendEmail {
    param(
        [string]$Subject,
        [string]$Body
    )

    if ($EnableEmail -ne "true") {
        return $true
    }

    if (-not $EmailRecipient) {
        Write-Warning "Email enabled but EMAIL_RECIPIENT not set"
        return $false
    }

    try {
        $MailParams = @{
            To         = $EmailRecipient
            Subject    = $Subject
            Body       = $Body
            SmtpServer = $SmtpServer
            Port       = $SmtpPort
            UseSsl     = $true
        }

        if ($SmtpUser -and $SmtpPassword) {
            $Credential = New-Object System.Management.Automation.PSCredential(
                $SmtpUser,
                (ConvertTo-SecureString $SmtpPassword -AsPlainText -Force)
            )
            $MailParams['Credential'] = $Credential
        }

        Send-MailMessage @MailParams
        Write-Success "Email notification sent to $EmailRecipient"
        return $true
    } catch {
        Write-Warning "Failed to send email: $_"
        return $false
    }
}

function CheckPrerequisites {
    Write-Info "Checking prerequisites..."

    $MissingTools = @()

    # Check required tools
    @("pg_dump", "psql") | ForEach-Object {
        if (-not (Get-Command $_ -ErrorAction SilentlyContinue)) {
            $MissingTools += $_
        }
    }

    # Check for 7-Zip or other compression
    if (-not ((Get-Command "7z" -ErrorAction SilentlyContinue) -or
              (Get-Command "powershell" -ErrorAction SilentlyContinue))) {
        Write-Warning "No compression utility found. Will use built-in Compress-Archive."
    }

    if ($MissingTools.Count -gt 0) {
        Write-Error-Custom "Missing required tools: $($MissingTools -join ', ')"
        Write-Error-Custom "Please install PostgreSQL client tools and try again."
        return $false
    }

    Write-Success "All prerequisites satisfied"
    return $true
}

function ValidateConfig {
    Write-Info "Validating configuration..."

    if (-not $PostgresPassword) {
        Write-Error-Custom "POSTGRES_PASSWORD environment variable not set"
        return $false
    }

    if ($S3Enabled -eq "true") {
        if (-not $S3Bucket) {
            Write-Error-Custom "S3_ENABLED=true but S3_BUCKET not set"
            return $false
        }
    }

    if ($EnableEmail -eq "true") {
        if (-not $EmailRecipient) {
            Write-Error-Custom "ENABLE_EMAIL=true but EMAIL_RECIPIENT not set"
            return $false
        }
        if (-not $SmtpServer) {
            Write-Error-Custom "Email enabled but SMTP_SERVER not set"
            return $false
        }
    }

    Write-Success "Configuration validation passed"
    return $true
}

# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================

function BackupPostgres {
    Write-Info "Starting PostgreSQL backup..."

    $BackupDirPath = Join-Path $BackupBaseDir $BackupName
    New-Item -ItemType Directory -Path $BackupDirPath -Force | Out-Null

    $PgBackupFile = Join-Path $BackupDirPath "postgres_dump.sql"

    if ($DryRun) {
        DryRunInfo "Would backup PostgreSQL to: $PgBackupFile"
        return $true
    }

    try {
        Write-Info "Dumping PostgreSQL database '$PostgresDb'..."

        $Env:PGPASSWORD = $PostgresPassword
        & pg_dump `
            --host=$PostgresHost `
            --port=$PostgresPort `
            --username=$PostgresUser `
            --format=plain `
            --verbose `
            $PostgresDb | Out-File -FilePath $PgBackupFile -Encoding UTF8

        if (-not (Test-Path $PgBackupFile)) {
            Write-Error-Custom "PostgreSQL backup file not created"
            return $false
        }

        $FileSize = (Get-Item $PgBackupFile).Length / 1MB
        Write-Success "PostgreSQL backup completed. Size: $($FileSize.ToString('F2')) MB"
        return $true
    } catch {
        Write-Error-Custom "PostgreSQL backup failed: $_"
        return $false
    } finally {
        $Env:PGPASSWORD = $null
    }
}

function BackupOpenSearch {
    if ($OpenSearchEnabled -ne "true") {
        Write-Info "OpenSearch backup disabled. Skipping..."
        return $true
    }

    Write-Info "Starting OpenSearch backup..."

    $BackupDirPath = Join-Path $BackupBaseDir $BackupName
    New-Item -ItemType Directory -Path $BackupDirPath -Force | Out-Null

    $OSBackupFile = Join-Path $BackupDirPath "opensearch_snapshot.json"

    if ($DryRun) {
        DryRunInfo "Would backup OpenSearch to: $OSBackupFile"
        return $true
    }

    try {
        Write-Info "Exporting OpenSearch indices..."

        # Get list of indices
        $IndicesResponse = Invoke-RestMethod `
            -Uri "http://$OpenSearchHost`:$OpenSearchPort/_cat/indices?format=json" `
            -Method GET `
            -ErrorAction Stop

        $IndicesResponse | ConvertTo-Json | Out-File -FilePath (Join-Path $BackupDirPath "opensearch_indices.json") -Encoding UTF8

        # Export cluster state
        $StateResponse = Invoke-RestMethod `
            -Uri "http://$OpenSearchHost`:$OpenSearchPort/_cluster/state?pretty" `
            -Method GET `
            -ErrorAction Stop

        $StateResponse | ConvertTo-Json -Depth 100 | Out-File -FilePath $OSBackupFile -Encoding UTF8

        $FileSize = (Get-Item $OSBackupFile).Length / 1MB
        Write-Success "OpenSearch backup completed. Size: $($FileSize.ToString('F2')) MB"
        return $true
    } catch {
        Write-Warning "OpenSearch backup warning: $_"
        return $true  # Don't fail the entire backup for OpenSearch
    }
}

function BackupConfigFiles {
    Write-Info "Starting configuration files backup..."

    $BackupDirPath = Join-Path $BackupBaseDir $BackupName
    $ConfigDir = Join-Path $BackupDirPath "config"
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null

    if ($DryRun) {
        DryRunInfo "Would backup configuration files to: $ConfigDir"
        return $true
    }

    try {
        # Default config files to backup
        $ConfigFiles = @(
            ".env",
            "docker-compose.yml",
            "Makefile",
            "pytest.ini"
        )

        # Add user-specified config files if any
        if ([System.Environment]::GetEnvironmentVariable("BACKUP_CONFIG_FILES")) {
            $UserFiles = ([System.Environment]::GetEnvironmentVariable("BACKUP_CONFIG_FILES")) -split ";"
            $ConfigFiles += $UserFiles
        }

        # Backup config files from root directory
        foreach ($ConfigFile in $ConfigFiles) {
            $FullPath = Join-Path $RootDir $ConfigFile
            if (Test-Path $FullPath -PathType Leaf) {
                Write-Info "Backing up: $ConfigFile"
                Copy-Item -Path $FullPath -Destination $ConfigDir -Force
            } elseif (Test-Path $FullPath -PathType Container) {
                Write-Info "Backing up directory: $ConfigFile"
                Copy-Item -Path $FullPath -Destination $ConfigDir -Recurse -Force
            }
        }

        $DirSize = (Get-ChildItem -Path $ConfigDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Success "Configuration files backup completed. Size: $($DirSize.ToString('F2')) MB"
        return $true
    } catch {
        Write-Error-Custom "Configuration backup failed: $_"
        return $false
    }
}

function CompressBackup {
    Write-Info "Compressing backup..."

    $BackupDirPath = Join-Path $BackupBaseDir $BackupName
    $BackupArchive = Join-Path $BackupBaseDir "$BackupName.zip"

    if ($DryRun) {
        DryRunInfo "Would compress backup to: $BackupArchive"
        return $true
    }

    try {
        if (Get-Command "7z" -ErrorAction SilentlyContinue) {
            Write-Info "Using 7-Zip for compression..."
            & 7z a -tzip "$BackupArchive" "$BackupDirPath" | Out-Null
        } else {
            Write-Info "Using built-in Compress-Archive..."
            Compress-Archive -Path $BackupDirPath -DestinationPath $BackupArchive -Force
        }

        if (-not (Test-Path $BackupArchive)) {
            Write-Error-Custom "Backup archive not created"
            return $false
        }

        # Remove uncompressed directory
        Remove-Item -Path $BackupDirPath -Recurse -Force

        $ArchiveSize = (Get-Item $BackupArchive).Length / 1MB
        Write-Success "Backup compressed successfully. Size: $($ArchiveSize.ToString('F2')) MB"
        Write-Info "Archive location: $BackupArchive"
        return $true
    } catch {
        Write-Error-Custom "Backup compression failed: $_"
        return $false
    }
}

# ============================================================================
# UPLOAD FUNCTIONS
# ============================================================================

function UploadToS3 {
    if ($S3Enabled -ne "true") {
        Write-Info "S3 upload disabled. Skipping..."
        return $true
    }

    Write-Info "Uploading backup to S3..."

    $BackupArchive = Join-Path $BackupBaseDir "$BackupName.zip"
    $S3Path = "s3://$S3Bucket/$S3Prefix/$BackupName.zip"

    if ($DryRun) {
        DryRunInfo "Would upload to: $S3Path"
        return $true
    }

    try {
        if (Get-Command "aws" -ErrorAction SilentlyContinue) {
            Write-Info "Using AWS CLI for S3 upload..."

            # Set AWS credentials if provided
            if ($AWSAccessKeyId -and $AWSSecretAccessKey) {
                $Env:AWS_ACCESS_KEY_ID = $AWSAccessKeyId
                $Env:AWS_SECRET_ACCESS_KEY = $AWSSecretAccessKey
                $Env:AWS_DEFAULT_REGION = $S3Region
            }

            & aws s3 cp $BackupArchive $S3Path --region $S3Region
            Write-Success "Backup uploaded to S3: $S3Path"
            return $true
        } else {
            Write-Warning "AWS CLI not found. Using PowerShell AWS tools..."

            if ($AWSAccessKeyId -and $AWSSecretAccessKey) {
                # Use AWS PowerShell cmdlets if available
                Write-Warning "AWS PowerShell module not configured. S3 upload requires manual setup."
            }
            return $false
        }
    } catch {
        Write-Error-Custom "S3 upload failed: $_"
        return $false
    }
}

# ============================================================================
# CLEANUP FUNCTIONS
# ============================================================================

function CleanupOldBackups {
    Write-Info "Cleaning up backups older than $RetentionDays days..."

    if ($DryRun) {
        DryRunInfo "Would cleanup backups older than $RetentionDays days from: $BackupBaseDir"
        return $true
    }

    if (-not (Test-Path $BackupBaseDir)) {
        Write-Warning "Backup directory does not exist: $BackupBaseDir"
        return $true
    }

    try {
        $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
        $OldBackups = Get-ChildItem -Path $BackupBaseDir -Filter "ree-ai-backup_*.zip" |
            Where-Object { $_.LastWriteTime -lt $CutoffDate }

        foreach ($Backup in $OldBackups) {
            Write-Info "Deleting old backup: $($Backup.Name)"
            Remove-Item -Path $Backup.FullName -Force
        }

        if ($OldBackups.Count -gt 0) {
            Write-Success "Deleted $($OldBackups.Count) old backup(s)"
        } else {
            Write-Info "No old backups found to delete"
        }

        return $true
    } catch {
        Write-Warning "Cleanup failed: $_"
        return $false
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    # Parse command line arguments
    if ($Help) {
        Show-Help
        exit 0
    }

    Write-Info "========================================="
    Write-Info "REE AI Platform Backup Script"
    Write-Info "Start time: $(Get-Date)"
    if ($DryRun) {
        Write-Warning "Running in DRY-RUN mode"
    }
    Write-Info "========================================="

    # Run validation checks
    if (-not (CheckPrerequisites)) {
        SendEmail "REE AI Backup Failed" "Backup failed at prerequisite check. Check logs: $LogFile"
        exit 1
    }

    if (-not (ValidateConfig)) {
        SendEmail "REE AI Backup Failed" "Backup failed at configuration validation. Check logs: $LogFile"
        exit 2
    }

    # Create backup directory
    New-Item -ItemType Directory -Path $BackupBaseDir -Force | Out-Null

    # Execute backups
    if (-not (BackupPostgres)) {
        Write-Error-Custom "PostgreSQL backup failed"
        SendEmail "REE AI Backup Failed" "PostgreSQL backup failed. Check logs: $LogFile"
        exit 3
    }

    if (-not (BackupOpenSearch)) {
        Write-Warning "OpenSearch backup incomplete (non-critical)"
    }

    if (-not (BackupConfigFiles)) {
        Write-Error-Custom "Configuration backup failed"
        SendEmail "REE AI Backup Failed" "Configuration backup failed. Check logs: $LogFile"
        exit 3
    }

    # Compress backup
    if (-not (CompressBackup)) {
        Write-Error-Custom "Backup compression failed"
        SendEmail "REE AI Backup Failed" "Backup compression failed. Check logs: $LogFile"
        exit 3
    }

    # Upload to S3
    if (-not (UploadToS3)) {
        Write-Warning "S3 upload failed (non-critical)"
    }

    # Cleanup old backups
    if (-not (CleanupOldBackups)) {
        Write-Warning "Cleanup failed (non-critical)"
    }

    Write-Info "========================================="
    Write-Success "Backup completed successfully!"
    Write-Info "End time: $(Get-Date)"
    Write-Info "========================================="

    exit 0
}

# Run main function
Main
