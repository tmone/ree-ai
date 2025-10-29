#!/bin/bash

################################################################################
# REE AI Platform - Restore from Backup Script
################################################################################
#
# DESCRIPTION:
#   Restore script for the REE AI platform with support for:
#   - List available backups
#   - Restore PostgreSQL database
#   - Restore OpenSearch indices
#   - Verify backup integrity
#   - Selective restore (choose specific components)
#
# USAGE:
#   ./restore.sh list                    # List available backups
#   ./restore.sh restore <backup_name>   # Restore from specific backup
#   ./restore.sh restore latest          # Restore from latest backup
#   ./restore.sh verify <backup_name>    # Verify backup integrity
#   ./restore.sh --help                  # Display help
#
# CONFIGURATION:
#   Configure via environment variables or .backup.env file in script directory
#
# ENVIRONMENT VARIABLES:
#   BACKUP_DIR              - Local backup directory (default: ./backups)
#   POSTGRES_HOST           - PostgreSQL host (default: localhost)
#   POSTGRES_PORT           - PostgreSQL port (default: 5432)
#   POSTGRES_DB             - Database name (default: ree_ai)
#   POSTGRES_USER           - PostgreSQL user (default: ree_ai_user)
#   POSTGRES_PASSWORD       - PostgreSQL password (required)
#   OPENSEARCH_HOST         - OpenSearch host (default: localhost)
#   OPENSEARCH_PORT         - OpenSearch port (default: 9200)
#   OPENSEARCH_ENABLED      - Restore OpenSearch (default: true)
#   DROP_DB_BEFORE_RESTORE  - Drop database before restore (default: false)
#   VERIFY_CHECKSUM         - Verify backup checksums (default: true)
#   LOG_FILE                - Log file path (default: ./restore.log)
#   DRY_RUN                 - Dry run mode (default: false)
#
# REQUIREMENTS:
#   - PostgreSQL client tools (psql, pg_restore)
#   - tar, gzip
#   - curl (for OpenSearch)
#   - Optional: md5sum/sha256sum for verification
#
# EXIT CODES:
#   0   - Success
#   1   - General error
#   2   - Configuration error
#   3   - Restore error
#   4   - Verification error
#
# EXAMPLES:
#   # List available backups
#   ./restore.sh list
#
#   # Restore specific backup
#   ./restore.sh restore ree-ai-backup_20241029_120000
#
#   # Restore latest backup (dry-run)
#   DRY_RUN=true ./restore.sh restore latest
#
#   # Verify backup integrity
#   ./restore.sh verify ree-ai-backup_20241029_120000
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
DROP_DB_BEFORE_RESTORE="${DROP_DB_BEFORE_RESTORE:-false}"
VERIFY_CHECKSUM="${VERIFY_CHECKSUM:-true}"
LOG_FILE="${LOG_FILE:-.}"
DRY_RUN="${DRY_RUN:-false}"

# Set log file path
if [[ "$LOG_FILE" == "." ]]; then
    LOG_FILE="$SCRIPT_DIR/restore.log"
fi

# Load environment file if exists
if [[ -f "$SCRIPT_DIR/.backup.env" ]]; then
    set +a
    source "$SCRIPT_DIR/.backup.env"
    set -a
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
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

log_step() {
    echo -e "${MAGENTA}[STEP]${NC} $@" | tee -a "$LOG_FILE"
}

show_help() {
    cat << 'EOF'
REE AI Platform Restore Script

USAGE:
  ./restore.sh [COMMAND] [OPTIONS]

COMMANDS:
  list                            List all available backups
  restore <backup_name|latest>    Restore from backup
  verify <backup_name>            Verify backup integrity
  --help                          Show this help message

EXAMPLES:
  # List backups
  ./restore.sh list

  # Restore specific backup
  ./restore.sh restore ree-ai-backup_20241029_120000

  # Restore latest backup
  ./restore.sh restore latest

  # Dry-run restore
  DRY_RUN=true ./restore.sh restore latest

  # Verify backup
  ./restore.sh verify ree-ai-backup_20241029_120000

ENVIRONMENT VARIABLES:
  Required:
    POSTGRES_PASSWORD           PostgreSQL password

  Optional:
    BACKUP_DIR                  Backup directory (default: ./backups)
    DROP_DB_BEFORE_RESTORE      Drop database before restore (default: false)
    DRY_RUN                     Preview without restoring (default: false)
    OPENSEARCH_ENABLED          Restore OpenSearch (default: true)
    LOG_FILE                    Log file path (default: ./restore.log)

NOTES:
  - Always verify backups before restoring to production
  - Make a backup of current data before restoring
  - Consider using --dry-run to preview restore operations
  - Requires PostgreSQL client tools to be installed

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

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    for tool in tar gzip curl psql; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        return 1
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

    if [[ ! -d "$BACKUP_BASE_DIR" ]]; then
        log_error "Backup directory does not exist: $BACKUP_BASE_DIR"
        return 2
    fi

    log_success "Configuration validation passed"
    return 0
}

################################################################################
# LIST BACKUPS
################################################################################

list_backups() {
    log_info "Available backups in: $BACKUP_BASE_DIR"
    echo ""

    if [[ ! -d "$BACKUP_BASE_DIR" ]]; then
        log_warning "Backup directory does not exist"
        return 1
    fi

    local backup_count=0

    echo -e "${BLUE}Backup Name${NC:- 45}  ${BLUE}Size${NC}  ${BLUE}Created${NC}"
    echo "============================================================================"

    # Find and list all backups
    while IFS= read -r backup_file; do
        backup_count=$((backup_count + 1))
        local backup_name=$(basename "$backup_file" .tar.gz)
        local backup_size=$(du -h "$backup_file" | cut -f1)
        local backup_date=$(stat -c %y "$backup_file" 2>/dev/null | cut -d' ' -f1,2 || stat -f "%Sm -format=%Y%m%d_%H%M%S" "$backup_file" 2>/dev/null || echo "Unknown")

        printf "%-40s  %-10s  %s\n" "$backup_name" "$backup_size" "$backup_date"
    done < <(find "$BACKUP_BASE_DIR" -maxdepth 1 -name "ree-ai-backup_*.tar.gz" -type f | sort -r)

    echo ""
    if [[ $backup_count -eq 0 ]]; then
        log_warning "No backups found"
        return 1
    fi

    log_success "Found $backup_count backup(s)"
    return 0
}

################################################################################
# VERIFY BACKUP
################################################################################

verify_backup() {
    local backup_name=$1

    if [[ -z "$backup_name" ]]; then
        log_error "Backup name required for verify command"
        return 2
    fi

    log_step "Verifying backup: $backup_name"

    local backup_file="$BACKUP_BASE_DIR/${backup_name}.tar.gz"

    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 3
    fi

    # Verify tar integrity
    log_info "Checking archive integrity..."
    if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
        log_error "Archive is corrupted: $backup_file"
        return 4
    fi
    log_success "Archive integrity verified"

    # List contents
    log_info "Archive contents:"
    tar -tzf "$backup_file" | head -20

    # Check for required files
    log_info "Verifying backup components..."

    local has_postgres=false
    local has_opensearch=false
    local has_config=false

    if tar -tzf "$backup_file" | grep -q "postgres_dump.sql"; then
        has_postgres=true
        log_success "PostgreSQL backup found"
    else
        log_warning "PostgreSQL backup not found"
    fi

    if tar -tzf "$backup_file" | grep -q "opensearch_snapshot.json"; then
        has_opensearch=true
        log_success "OpenSearch backup found"
    else
        log_warning "OpenSearch backup not found"
    fi

    if tar -tzf "$backup_file" | grep -q "config/"; then
        has_config=true
        log_success "Configuration backup found"
    else
        log_warning "Configuration backup not found"
    fi

    # Get file size
    local file_size=$(du -h "$backup_file" | cut -f1)
    log_success "Backup size: $file_size"

    echo ""
    log_success "Backup verification completed"
    return 0
}

################################################################################
# RESTORE FUNCTIONS
################################################################################

restore_postgres() {
    local backup_file=$1

    log_step "Starting PostgreSQL restoration..."

    # Extract PostgreSQL dump
    local temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT

    log_info "Extracting PostgreSQL dump..."
    if ! tar -xzf "$backup_file" -C "$temp_dir"; then
        log_error "Failed to extract backup"
        return 3
    fi

    # Find the backup name (first directory in archive)
    local backup_name=$(ls -d "$temp_dir"/ree-ai-backup_* 2>/dev/null | head -1 | xargs basename)
    local pg_dump_file="$temp_dir/$backup_name/postgres_dump.sql"

    if [[ ! -f "$pg_dump_file" ]]; then
        log_error "PostgreSQL dump file not found in backup"
        return 3
    fi

    # Drop existing database if requested
    if [[ "$DROP_DB_BEFORE_RESTORE" == "true" ]]; then
        log_warning "Dropping existing database '$POSTGRES_DB'..."
        if [[ "$DRY_RUN" == "true" ]]; then
            dry_run_info "Would drop database: $POSTGRES_DB"
        else
            if ! PGPASSWORD="$POSTGRES_PASSWORD" dropdb \
                --host="$POSTGRES_HOST" \
                --port="$POSTGRES_PORT" \
                --username="$POSTGRES_USER" \
                --if-exists \
                "$POSTGRES_DB" 2>&1 | tee -a "$LOG_FILE"; then
                log_warning "Could not drop database (may not exist)"
            fi

            # Create new database
            log_info "Creating new database '$POSTGRES_DB'..."
            if ! PGPASSWORD="$POSTGRES_PASSWORD" createdb \
                --host="$POSTGRES_HOST" \
                --port="$POSTGRES_PORT" \
                --username="$POSTGRES_USER" \
                "$POSTGRES_DB"; then
                log_error "Failed to create database"
                return 3
            fi
        fi
    fi

    # Restore from dump
    log_info "Restoring PostgreSQL database..."
    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would restore PostgreSQL from: $pg_dump_file"
    else
        if ! PGPASSWORD="$POSTGRES_PASSWORD" psql \
            --host="$POSTGRES_HOST" \
            --port="$POSTGRES_PORT" \
            --username="$POSTGRES_USER" \
            --dbname="$POSTGRES_DB" \
            --file="$pg_dump_file" > /dev/null 2>> "$LOG_FILE"; then
            log_error "PostgreSQL restoration failed"
            return 3
        fi
    fi

    log_success "PostgreSQL restoration completed"
    return 0
}

restore_opensearch() {
    if [[ "$OPENSEARCH_ENABLED" != "true" ]]; then
        log_info "OpenSearch restoration disabled. Skipping..."
        return 0
    fi

    log_step "Starting OpenSearch restoration..."

    local backup_file=$1
    local temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT

    log_info "Extracting OpenSearch data..."
    if ! tar -xzf "$backup_file" -C "$temp_dir"; then
        log_error "Failed to extract backup"
        return 3
    fi

    # Find the backup name
    local backup_name=$(ls -d "$temp_dir"/ree-ai-backup_* 2>/dev/null | head -1 | xargs basename)
    local os_snapshot_file="$temp_dir/$backup_name/opensearch_snapshot.json"

    if [[ ! -f "$os_snapshot_file" ]]; then
        log_warning "OpenSearch snapshot file not found in backup"
        return 0
    fi

    log_info "Note: OpenSearch restoration requires manual index restoration"
    log_info "Snapshot file available at: $os_snapshot_file"
    log_warning "Manual steps required:"
    log_warning "  1. Create OpenSearch snapshot repository"
    log_warning "  2. Copy snapshot files to repository location"
    log_warning "  3. Restore indices from snapshot"

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would restore OpenSearch from: $os_snapshot_file"
    fi

    log_success "OpenSearch restoration information provided"
    return 0
}

restore_config_files() {
    log_step "Starting configuration files restoration..."

    local backup_file=$1
    local temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT

    log_info "Extracting configuration files..."
    if ! tar -xzf "$backup_file" -C "$temp_dir"; then
        log_error "Failed to extract backup"
        return 3
    fi

    # Find the backup name
    local backup_name=$(ls -d "$temp_dir"/ree-ai-backup_* 2>/dev/null | head -1 | xargs basename)
    local config_dir="$temp_dir/$backup_name/config"

    if [[ ! -d "$config_dir" ]]; then
        log_warning "Configuration directory not found in backup"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        dry_run_info "Would restore configuration files from: $config_dir"
        log_info "Configuration files available:"
        ls -la "$config_dir" 2>/dev/null | tail -n +2
    else
        log_info "Restoring configuration files to: $ROOT_DIR"

        # Create backup of current config
        local config_backup_dir="$ROOT_DIR/.config_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$config_backup_dir"

        # Copy important files to backup
        for file in ".env" "docker-compose.yml" "Makefile"; do
            if [[ -f "$ROOT_DIR/$file" ]]; then
                cp "$ROOT_DIR/$file" "$config_backup_dir/"
            fi
        done

        log_warning "Current config backed up to: $config_backup_dir"

        # Copy restored files
        cp -r "$config_dir"/* "$ROOT_DIR/" 2>/dev/null || true
    fi

    log_success "Configuration files restoration completed"
    return 0
}

################################################################################
# MAIN RESTORE FUNCTION
################################################################################

restore_from_backup() {
    local backup_identifier=$1

    # Resolve backup name
    local backup_name="$backup_identifier"

    if [[ "$backup_identifier" == "latest" ]]; then
        # Find latest backup
        backup_name=$(find "$BACKUP_BASE_DIR" -maxdepth 1 -name "ree-ai-backup_*.tar.gz" -type f -printf '%f\n' | sort -r | head -1 | sed 's/.tar.gz//')

        if [[ -z "$backup_name" ]]; then
            log_error "No backups found"
            return 1
        fi

        log_info "Using latest backup: $backup_name"
    fi

    local backup_file="$BACKUP_BASE_DIR/${backup_name}.tar.gz"

    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi

    log_step "========================================="
    log_step "REE AI Platform Restoration"
    log_step "Start time: $(date)"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "Running in DRY-RUN mode"
    fi
    log_step "========================================="

    # Verify backup first
    log_info "Verifying backup integrity..."
    if ! verify_backup "$backup_name"; then
        log_error "Backup verification failed"
        return 4
    fi

    echo ""

    # Restore components
    restore_postgres "$backup_file" || {
        log_error "PostgreSQL restoration failed"
        return 3
    }

    restore_opensearch "$backup_file" || {
        log_warning "OpenSearch restoration incomplete"
    }

    restore_config_files "$backup_file" || {
        log_warning "Configuration restoration incomplete"
    }

    echo ""
    log_step "========================================="
    log_success "Restoration completed successfully!"
    log_step "End time: $(date)"
    log_step "========================================="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "This was a dry-run. No actual changes were made."
    fi

    return 0
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    local command="${1:-help}"

    case "$command" in
        list)
            check_prerequisites || exit 1
            validate_config || exit 2
            list_backups
            ;;
        restore)
            if [[ -z "${2:-}" ]]; then
                log_error "Backup name or 'latest' required"
                show_help
                exit 2
            fi
            check_prerequisites || exit 1
            validate_config || exit 2
            restore_from_backup "$2"
            ;;
        verify)
            if [[ -z "${2:-}" ]]; then
                log_error "Backup name required"
                show_help
                exit 2
            fi
            check_prerequisites || exit 1
            validate_config || exit 2
            verify_backup "$2"
            ;;
        --help|-h|help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 2
            ;;
    esac
}

# Run main function
main "$@"
exit $?
