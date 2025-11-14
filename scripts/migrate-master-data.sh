#!/bin/bash

# =============================================================================
# Master Data Migration Runner with Rollback Support
# =============================================================================
# This script manages database migrations for the master data system:
# - Tracks migration history
# - Supports rollback to previous versions
# - Validates migrations before applying
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MIGRATIONS_DIR="$PROJECT_ROOT/database/migrations"
POSTGRES_CONTAINER="ree-ai-postgres"
DB_USER="ree_ai_user"
DB_NAME="ree_ai"

# =============================================================================
# Utility Functions
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Execute SQL command
exec_sql() {
    docker exec $POSTGRES_CONTAINER psql -U $DB_USER -d $DB_NAME -tAc "$1"
}

# Execute SQL file
exec_sql_file() {
    docker exec -i $POSTGRES_CONTAINER psql -U $DB_USER -d $DB_NAME < "$1"
}

# =============================================================================
# Migration Tracking
# =============================================================================

create_migrations_table() {
    log_info "Creating migrations tracking table..."

    exec_sql "
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            version VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(200) NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        );

        CREATE INDEX IF NOT EXISTS idx_migrations_version ON schema_migrations(version);
    "

    log_info "Migrations table ready ✓"
}

is_migration_applied() {
    local version=$1
    local count=$(exec_sql "SELECT COUNT(*) FROM schema_migrations WHERE version='$version';")
    [ "$count" -gt 0 ]
}

record_migration() {
    local version=$1
    local name=$2
    local checksum=$3

    exec_sql "
        INSERT INTO schema_migrations (version, name, checksum)
        VALUES ('$version', '$name', '$checksum')
        ON CONFLICT (version) DO NOTHING;
    "

    log_info "Migration $version recorded ✓"
}

# =============================================================================
# Migration Operations
# =============================================================================

apply_migration() {
    local migration_file=$1
    local version=$(basename "$migration_file" .sql | cut -d'_' -f1)
    local name=$(basename "$migration_file" .sql)

    log_step "Applying migration: $name"

    if is_migration_applied "$version"; then
        log_warning "Migration $version already applied, skipping"
        return 0
    fi

    # Calculate checksum
    if command -v md5sum &> /dev/null; then
        local checksum=$(md5sum "$migration_file" | cut -d' ' -f1)
    else
        local checksum=$(md5 -q "$migration_file")
    fi

    # Create backup before migration
    create_backup "pre-migration-$version" > /dev/null

    # Apply migration
    log_info "Executing SQL..."
    if exec_sql_file "$migration_file"; then
        # Record migration
        record_migration "$version" "$name" "$checksum"
        log_info "Migration $version applied successfully ✓"
    else
        log_error "Migration failed!"
        return 1
    fi
}

rollback_last_migration() {
    log_step "Rolling back last migration..."

    # Get last migration
    local last_version=$(exec_sql "SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 1;")

    if [ -z "$last_version" ]; then
        log_warning "No migrations to rollback"
        return 0
    fi

    # Find corresponding rollback file
    local rollback_file="$MIGRATIONS_DIR/rollback_${last_version}.sql"

    if [ ! -f "$rollback_file" ]; then
        log_error "Rollback file not found: $rollback_file"
        log_warning "You may need to restore from backup"
        return 1
    fi

    # Execute rollback
    log_info "Executing rollback SQL..."
    exec_sql_file "$rollback_file"

    # Remove from migration history
    exec_sql "DELETE FROM schema_migrations WHERE version='$last_version';"

    log_info "Migration $last_version rolled back successfully ✓"
}

# =============================================================================
# Backup & Restore
# =============================================================================

create_backup() {
    local backup_name=${1:-manual-backup}
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$PROJECT_ROOT/backups"
    local backup_file="$backup_dir/${backup_name}_${timestamp}.sql"

    log_info "Creating backup: $backup_name"

    mkdir -p "$backup_dir"

    docker exec $POSTGRES_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > "$backup_file"

    log_info "Backup created: $backup_file ✓"
    echo "$backup_file"
}

restore_backup() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi

    log_warning "This will restore the database to: $backup_file"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Restore cancelled"
        return 0
    fi

    log_info "Restoring from backup..."

    # Drop and recreate database
    docker exec $POSTGRES_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
    docker exec $POSTGRES_CONTAINER psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

    # Restore
    docker exec -i $POSTGRES_CONTAINER psql -U $DB_USER -d $DB_NAME < "$backup_file"

    log_info "Database restored successfully ✓"
}

# =============================================================================
# Migration Status
# =============================================================================

show_migration_status() {
    log_info "Migration Status:"
    echo ""

    # Get applied migrations
    local applied=$(exec_sql "SELECT version, name, TO_CHAR(applied_at, 'YYYY-MM-DD HH24:MI:SS') FROM schema_migrations ORDER BY version;" 2>/dev/null || echo "")

    if [ -z "$applied" ]; then
        log_warning "No migrations applied yet"
    else
        echo -e "${GREEN}Applied Migrations:${NC}"
        echo "$applied" | while IFS='|' read -r version name applied_at; do
            echo "  ✓ $version - $name (applied: $applied_at)"
        done
    fi

    echo ""

    # Get pending migrations
    local pending_count=0
    for file in "$MIGRATIONS_DIR"/*.sql; do
        [ -f "$file" ] || continue
        [[ "$(basename "$file")" == rollback_* ]] && continue  # Skip rollback files

        local version=$(basename "$file" .sql | cut -d'_' -f1)

        if ! is_migration_applied "$version"; then
            if [ $pending_count -eq 0 ]; then
                echo -e "${YELLOW}Pending Migrations:${NC}"
            fi
            echo "  ⏳ $(basename "$file")"
            pending_count=$((pending_count + 1))
        fi
    done

    if [ $pending_count -eq 0 ]; then
        log_info "All migrations are up to date ✓"
    fi

    echo ""
}

# =============================================================================
# Main Commands
# =============================================================================

command_up() {
    log_info "Running migrations..."

    create_migrations_table

    local migration_count=0
    for file in "$MIGRATIONS_DIR"/*.sql; do
        [ -f "$file" ] || continue
        [[ "$(basename "$file")" == rollback_* ]] && continue  # Skip rollback files

        apply_migration "$file"
        migration_count=$((migration_count + 1))
    done

    if [ $migration_count -eq 0 ]; then
        log_warning "No migration files found in $MIGRATIONS_DIR"
    else
        log_info "Applied $migration_count migration(s) ✓"
    fi
}

command_down() {
    local steps=${1:-1}

    log_warning "Rolling back $steps migration(s)..."

    create_migrations_table

    for ((i=1; i<=steps; i++)); do
        rollback_last_migration
    done

    log_info "Rollback completed ✓"
}

command_status() {
    create_migrations_table
    show_migration_status
}

command_backup() {
    local backup_name=${1:-manual}
    create_backup "$backup_name"
}

command_restore() {
    local backup_file=$1

    if [ -z "$backup_file" ]; then
        log_error "Please specify backup file to restore"
        echo "Usage: $0 restore <backup-file>"
        exit 1
    fi

    restore_backup "$backup_file"
}

show_help() {
    cat << EOF
Master Data Migration Runner

Usage: $0 <command> [options]

Commands:
  up                  Apply all pending migrations
  down [N]           Rollback last N migrations (default: 1)
  status             Show migration status
  backup [name]      Create database backup
  restore <file>     Restore from backup file
  help               Show this help message

Examples:
  $0 up                          # Apply all pending migrations
  $0 down 2                      # Rollback last 2 migrations
  $0 status                      # Show current status
  $0 backup pre-deployment       # Create named backup
  $0 restore backups/backup.sql  # Restore from file

Master Data Migrations:
  001_create_master_data_schema.sql  - Creates master data tables
  002_seed_master_data.sql           - Seeds initial data

EOF
}

# =============================================================================
# Main
# =============================================================================

main() {
    local command=${1:-help}

    case "$command" in
        up)
            command_up
            ;;
        down)
            command_down "${2:-1}"
            ;;
        status)
            command_status
            ;;
        backup)
            command_backup "${2:-manual}"
            ;;
        restore)
            command_restore "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
