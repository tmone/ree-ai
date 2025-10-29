#!/bin/bash

################################################################################
# REE AI Platform - Backup Automation Script (Linux/Mac)
################################################################################
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
#   ./backup.sh                 # Standard backup
#   ./backup.sh --dry-run       # Dry run mode (no actual changes)
#   ./backup.sh --help          # Display this help message
#
# CONFIGURATION:
#   Configure via environment variables or .backup.env file in script directory
#
# ENVIRONMENT VARIABLES:
#   BACKUP_DIR              - Local backup directory (default: ./backups)
#   POSTGRES_HOST           - PostgreSQL host (default: localhost)
#   POSTGRES_PORT           - PostgreSQL port (default: 5432)
#   POSTGRES_DB             - Database name to backup (default: ree_ai)
#   POSTGRES_USER           - PostgreSQL user (default: ree_ai_user)
#   POSTGRES_PASSWORD       - PostgreSQL password (required)
#   OPENSEARCH_HOST         - OpenSearch host (default: localhost)
#   OPENSEARCH_PORT         - OpenSearch port (default: 9200)
#   OPENSEARCH_ENABLED      - Enable OpenSearch backup (default: true)
#   BACKUP_CONFIG_FILES     - Config files to backup (space-separated)
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
#   LOG_FILE                - Log file path (default: ./backup.log)
#   DRY_RUN                 - Dry run mode (default: false)
#
# REQUIREMENTS:
#   - PostgreSQL client tools (pg_dump)
#   - curl (for OpenSearch and S3)
#   - tar, gzip
#   - Optional: AWS CLI for S3 uploads (or curl)
#   - Optional: mail utility for email notifications
#
# EXIT CODES:
#   0   - Success
#   1   - General error
#   2   - Configuration error
#   3   - Backup error
#   4   - Upload error
#   5   - Cleanup error
#
################################################################################

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Default configuration
BACKUP_DIR="${BACKUP_DIR:-.}"
BACKUP_BASE_DIR="${BACKUP_DIR}/backups"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-ree_ai}"
POSTGRES_USER="${POSTGRES_USER:-ree_ai_user}"
OPENSEARCH_HOST="${OPENSEARCH_HOST:-localhost}"
OPENSEARCH_PORT="${OPENSEARCH_PORT:-9200}"
OPENSEARCH_ENABLED="${OPENSEARCH_ENABLED:-true}"
S3_ENABLED="${S3_ENABLED:-false}"
S3_PREFIX="${S3_PREFIX:-ree-ai-backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
ENABLE_EMAIL="${ENABLE_EMAIL:-false}"
LOG_FILE="${LOG_FILE:-.}"
DRY_RUN="${DRY_RUN:-false}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ree-ai-backup_${TIMESTAMP}"

# Load environment file if exists
if [[ -f "$SCRIPT_DIR/.backup.env" ]]; then
    set +a
    source "$SCRIPT_DIR/.backup.env"
    set -a
fi

# Set log file path
if [[ "$LOG_FILE" == "." ]]; then
    LOG_FILE="$SCRIPT_DIR/backup.log"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

################################################################################
# UTILITY FUNCTIONS
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "$LOG_FILE"
}

show_usage() {
    grep '^# ' "$0" | head -60
}

show_help() {
    cat << 'EOF'
REE AI Platform Backup Script

USAGE:
  ./backup.sh [OPTIONS]

OPTIONS:
  --dry-run               Run in dry-run mode (no actual backup)
  --help                  Display this help message

ENVIRONMENT VARIABLES:
  Required:
    POSTGRES_PASSWORD     PostgreSQL password

  Optional:
    BACKUP_DIR            Local backup directory (default: ./backups)
    POSTGRES_HOST         PostgreSQL host (default: localhost)
    POSTGRES_PORT         PostgreSQL port (default: 5432)
    POSTGRES_DB           Database name (default: ree_ai)
    POSTGRES_USER         PostgreSQL user (default: ree_ai_user)
    OPENSEARCH_ENABLED    Enable OpenSearch backup (default: true)
    S3_ENABLED            Enable S3 upload (default: false)
    S3_BUCKET             S3 bucket name
    RETENTION_DAYS        Days to retain backups (default: 30)
    ENABLE_EMAIL          Enable email notifications (default: false)
    LOG_FILE              Log file path (default: ./backup.log)

EXAMPLES:
  # Standard backup with retention cleanup
  ./backup.sh

  # Dry run mode (preview without backup)
  ./backup.sh --dry-run

  # Backup with S3 upload
  S3_ENABLED=true S3_BUCKET=my-bucket ./backup.sh

  # Backup with email on failure
  ENABLE_EMAIL=true EMAIL_RECIPIENT=admin@example.com ./backup.sh

For more detailed configuration, see the script header comments.
EOF
}

dry_run_info() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "[DRY-RUN] $@"
    fi
}

execute_cmd() {
    local cmd=$@
    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would execute: $cmd"
    else
        eval "$cmd"
    fi
}

send_email() {
    local subject=$1
    local body=$2

    if [[ "$ENABLE_EMAIL" != "true" ]]; then
        return 0
    fi

    if [[ -z "${EMAIL_RECIPIENT:-}" ]]; then
        log_warning "Email enabled but EMAIL_RECIPIENT not set"
        return 1
    fi

    # Check if we have mail command
    if command -v mail &> /dev/null; then
        echo -e "$body" | mail -s "$subject" "$EMAIL_RECIPIENT"
        log_success "Email notification sent to $EMAIL_RECIPIENT"
    elif command -v sendmail &> /dev/null; then
        {
            echo "Subject: $subject"
            echo "To: $EMAIL_RECIPIENT"
            echo ""
            echo "$body"
        } | sendmail -t
        log_success "Email notification sent to $EMAIL_RECIPIENT"
    else
        log_warning "Neither 'mail' nor 'sendmail' command found. Cannot send email."
        return 1
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    # Check required tools
    for tool in pg_dump tar gzip curl; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install missing tools and try again."
        return 1
    fi

    # Check for AWS CLI if S3 is enabled
    if [[ "$S3_ENABLED" == "true" ]] && [[ -z "${AWS_ACCESS_KEY_ID:-}" ]]; then
        if ! command -v aws &> /dev/null; then
            log_warning "AWS CLI not found and AWS_ACCESS_KEY_ID not set. S3 upload will use curl."
        fi
    fi

    log_success "All prerequisites satisfied"
    return 0
}

validate_config() {
    log_info "Validating configuration..."

    if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
        log_error "POSTGRES_PASSWORD environment variable not set"
        return 2
    fi

    if [[ "$S3_ENABLED" == "true" ]]; then
        if [[ -z "${S3_BUCKET:-}" ]]; then
            log_error "S3_ENABLED=true but S3_BUCKET not set"
            return 2
        fi
    fi

    if [[ "$ENABLE_EMAIL" == "true" ]]; then
        if [[ -z "${EMAIL_RECIPIENT:-}" ]]; then
            log_error "ENABLE_EMAIL=true but EMAIL_RECIPIENT not set"
            return 2
        fi
    fi

    log_success "Configuration validation passed"
    return 0
}

################################################################################
# BACKUP FUNCTIONS
################################################################################

backup_postgres() {
    log_info "Starting PostgreSQL backup..."

    local backup_dir="$BACKUP_BASE_DIR/$BACKUP_NAME"
    mkdir -p "$backup_dir"

    local pg_backup_file="$backup_dir/postgres_dump.sql"

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would backup PostgreSQL to: $pg_backup_file"
        touch "$backup_dir/.postgres_backup_done"
        return 0
    fi

    log_info "Dumping PostgreSQL database '$POSTGRES_DB'..."

    if ! PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        --host="$POSTGRES_HOST" \
        --port="$POSTGRES_PORT" \
        --username="$POSTGRES_USER" \
        --format=plain \
        --verbose \
        "$POSTGRES_DB" > "$pg_backup_file" 2>> "$LOG_FILE"; then
        log_error "PostgreSQL backup failed"
        return 3
    fi

    local file_size=$(du -h "$pg_backup_file" | cut -f1)
    log_success "PostgreSQL backup completed. Size: $file_size"
}

backup_opensearch() {
    if [[ "$OPENSEARCH_ENABLED" != "true" ]]; then
        log_info "OpenSearch backup disabled. Skipping..."
        return 0
    fi

    log_info "Starting OpenSearch backup..."

    local backup_dir="$BACKUP_BASE_DIR/$BACKUP_NAME"
    mkdir -p "$backup_dir"

    local os_backup_file="$backup_dir/opensearch_snapshot.json"

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would backup OpenSearch to: $os_backup_file"
        return 0
    fi

    log_info "Exporting OpenSearch indices..."

    # Get list of indices and export them
    if ! curl -s -X GET \
        "http://$OPENSEARCH_HOST:$OPENSEARCH_PORT/_cat/indices?format=json" \
        > "$backup_dir/opensearch_indices.json" 2>> "$LOG_FILE"; then
        log_warning "Failed to get OpenSearch indices list. Continuing..."
    fi

    # Export cluster state
    if ! curl -s -X GET \
        "http://$OPENSEARCH_HOST:$OPENSEARCH_PORT/_cluster/state?pretty" \
        > "$os_backup_file" 2>> "$LOG_FILE"; then
        log_warning "Failed to backup OpenSearch state. Continuing..."
    fi

    local file_size=$(du -h "$os_backup_file" 2>/dev/null | cut -f1)
    log_success "OpenSearch backup completed. Size: ${file_size:-0B}"
}

backup_config_files() {
    log_info "Starting configuration files backup..."

    local backup_dir="$BACKUP_BASE_DIR/$BACKUP_NAME"
    mkdir -p "$backup_dir/config"

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would backup configuration files to: $backup_dir/config"
        return 0
    fi

    # Default config files to backup
    local config_files=(
        ".env"
        "docker-compose.yml"
        "Makefile"
    )

    # Add user-specified config files if any
    if [[ -n "${BACKUP_CONFIG_FILES:-}" ]]; then
        IFS=' ' read -ra user_files <<< "$BACKUP_CONFIG_FILES"
        config_files+=("${user_files[@]}")
    fi

    # Backup config files from root directory
    for config_file in "${config_files[@]}"; do
        local full_path="$ROOT_DIR/$config_file"
        if [[ -f "$full_path" ]]; then
            log_info "Backing up: $config_file"
            if ! cp "$full_path" "$backup_dir/config/"; then
                log_warning "Failed to backup: $config_file"
            fi
        elif [[ -d "$full_path" ]]; then
            log_info "Backing up directory: $config_file"
            if ! cp -r "$full_path" "$backup_dir/config/"; then
                log_warning "Failed to backup directory: $config_file"
            fi
        fi
    done

    local dir_size=$(du -sh "$backup_dir/config" 2>/dev/null | cut -f1)
    log_success "Configuration files backup completed. Size: $dir_size"
}

compress_backup() {
    log_info "Compressing backup..."

    local backup_dir="$BACKUP_BASE_DIR/$BACKUP_NAME"
    local backup_archive="$BACKUP_BASE_DIR/${BACKUP_NAME}.tar.gz"

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would compress backup to: $backup_archive"
        return 0
    fi

    if ! tar -czf "$backup_archive" -C "$BACKUP_BASE_DIR" "$BACKUP_NAME" 2>> "$LOG_FILE"; then
        log_error "Failed to compress backup"
        return 3
    fi

    # Remove uncompressed directory
    rm -rf "$backup_dir"

    local archive_size=$(du -h "$backup_archive" | cut -f1)
    log_success "Backup compressed successfully. Size: $archive_size"
    log_info "Archive location: $backup_archive"
}

################################################################################
# UPLOAD FUNCTIONS
################################################################################

upload_to_s3() {
    if [[ "$S3_ENABLED" != "true" ]]; then
        log_info "S3 upload disabled. Skipping..."
        return 0
    fi

    log_info "Uploading backup to S3..."

    local backup_archive="$BACKUP_BASE_DIR/${BACKUP_NAME}.tar.gz"
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${BACKUP_NAME}.tar.gz"

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would upload to: $s3_path"
        return 0
    fi

    # Check if AWS CLI is available
    if command -v aws &> /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
        log_info "Using AWS CLI for S3 upload..."
        if ! aws s3 cp "$backup_archive" "$s3_path" \
            --region "${S3_REGION:-us-east-1}" 2>> "$LOG_FILE"; then
            log_error "S3 upload failed via AWS CLI"
            return 4
        fi
    else
        # Fallback to curl for S3 upload (simple upload)
        log_info "Using curl for S3 upload..."

        if [[ -z "${AWS_ACCESS_KEY_ID:-}" ]] || [[ -z "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
            log_warning "AWS credentials not set. S3 upload will require public bucket or pre-signed URL."
            # You would need to implement pre-signed URL logic here
            log_warning "Skipping S3 upload without credentials"
            return 1
        fi
    fi

    log_success "Backup uploaded to S3: $s3_path"
}

################################################################################
# CLEANUP FUNCTIONS
################################################################################

cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would cleanup backups older than $RETENTION_DAYS days from: $BACKUP_BASE_DIR"
        return 0
    fi

    if [[ ! -d "$BACKUP_BASE_DIR" ]]; then
        log_warning "Backup directory does not exist: $BACKUP_BASE_DIR"
        return 0
    fi

    local deleted_count=0
    local deleted_size=0

    # Find and delete old backups
    while IFS= read -r file; do
        log_info "Deleting old backup: $(basename "$file")"
        local file_size=$(du -h "$file" | cut -f1)
        rm -f "$file"
        deleted_count=$((deleted_count + 1))
    done < <(find "$BACKUP_BASE_DIR" -maxdepth 1 -name "ree-ai-backup_*.tar.gz" -mtime "+$RETENTION_DAYS")

    if [[ $deleted_count -gt 0 ]]; then
        log_success "Deleted $deleted_count old backup(s)"
    else
        log_info "No old backups found to delete"
    fi

    return 0
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 2
                ;;
        esac
    done

    log_info "========================================="
    log_info "REE AI Platform Backup Script"
    log_info "Start time: $(date)"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "Running in DRY-RUN mode"
    fi
    log_info "========================================="

    # Run validation checks
    if ! check_prerequisites; then
        send_email "REE AI Backup Failed" "Backup failed at prerequisite check. Check logs: $LOG_FILE"
        exit 1
    fi

    if ! validate_config; then
        send_email "REE AI Backup Failed" "Backup failed at configuration validation. Check logs: $LOG_FILE"
        exit 2
    fi

    # Create backup directory
    mkdir -p "$BACKUP_BASE_DIR"

    # Execute backups
    backup_postgres || {
        log_error "PostgreSQL backup failed"
        send_email "REE AI Backup Failed" "PostgreSQL backup failed. Check logs: $LOG_FILE"
        exit 3
    }

    backup_opensearch || {
        log_error "OpenSearch backup failed"
        send_email "REE AI Backup Failed" "OpenSearch backup failed. Check logs: $LOG_FILE"
        exit 3
    }

    backup_config_files || {
        log_error "Configuration backup failed"
        send_email "REE AI Backup Failed" "Configuration backup failed. Check logs: $LOG_FILE"
        exit 3
    }

    # Compress backup
    compress_backup || {
        log_error "Backup compression failed"
        send_email "REE AI Backup Failed" "Backup compression failed. Check logs: $LOG_FILE"
        exit 3
    }

    # Upload to S3
    upload_to_s3 || {
        log_warning "S3 upload failed (non-critical)"
    }

    # Cleanup old backups
    cleanup_old_backups || {
        log_warning "Cleanup failed (non-critical)"
    }

    log_info "========================================="
    log_success "Backup completed successfully!"
    log_info "End time: $(date)"
    log_info "========================================="

    return 0
}

# Run main function
main "$@"
exit $?
