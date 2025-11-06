#!/bin/bash

# Run database migrations for REE AI platform
# Usage: ./scripts/run-migrations.sh [migration_number]
# Example: ./scripts/run-migrations.sh 001  (runs only 001)
#          ./scripts/run-migrations.sh       (runs all)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_USER="${POSTGRES_USER:-ree_ai_user}"
DB_NAME="${POSTGRES_DB:-ree_ai}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
MIGRATIONS_DIR="database/migrations"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   REE AI Database Migration Runner      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check if running in Docker or locally
if [ -f /.dockerenv ]; then
    echo -e "${YELLOW}🐳 Running inside Docker container${NC}"
    PSQL_CMD="psql -U $DB_USER -d $DB_NAME"
else
    echo -e "${YELLOW}💻 Running on local machine${NC}"
    PSQL_CMD="psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
fi

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ Error: psql command not found${NC}"
    echo "Please install PostgreSQL client or run this script inside Docker"
    exit 1
fi

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo -e "${RED}❌ Error: Migrations directory not found: $MIGRATIONS_DIR${NC}"
    exit 1
fi

# Function to run a single migration
run_migration() {
    local migration_file=$1
    local migration_name=$(basename "$migration_file")

    echo -e "${BLUE}🔄 Running: $migration_name${NC}"

    if $PSQL_CMD -f "$migration_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Success: $migration_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed: $migration_name${NC}"
        echo -e "${YELLOW}   Trying with verbose output...${NC}"
        $PSQL_CMD -f "$migration_file"
        return 1
    fi
}

# Main execution
if [ -n "$1" ]; then
    # Run specific migration
    MIGRATION_FILE="$MIGRATIONS_DIR/$1*.sql"
    if ls $MIGRATION_FILE 1> /dev/null 2>&1; then
        for file in $MIGRATION_FILE; do
            run_migration "$file"
        done
    else
        echo -e "${RED}❌ Migration not found: $1${NC}"
        exit 1
    fi
else
    # Run all migrations in order
    echo -e "${YELLOW}📦 Running all migrations...${NC}"
    echo ""

    SUCCESS_COUNT=0
    FAIL_COUNT=0

    for migration_file in $MIGRATIONS_DIR/*.sql; do
        if [ -f "$migration_file" ]; then
            if run_migration "$migration_file"; then
                ((SUCCESS_COUNT++))
            else
                ((FAIL_COUNT++))
            fi
            echo ""
        fi
    done

    # Summary
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Migration Summary              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo -e "${GREEN}✅ Successful: $SUCCESS_COUNT${NC}"
    if [ $FAIL_COUNT -gt 0 ]; then
        echo -e "${RED}❌ Failed: $FAIL_COUNT${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✨ All migrations completed successfully!${NC}"
echo ""

# Verify schema
echo -e "${BLUE}🔍 Verifying database schema...${NC}"
echo ""

# Check if new tables exist
TABLES=("favorites" "saved_searches" "inquiries" "user_actions")

for table in "${TABLES[@]}"; do
    if $PSQL_CMD -c "\d $table" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Table exists: $table"
    else
        echo -e "${RED}✗${NC} Table missing: $table"
    fi
done

# Check user table columns
echo ""
echo -e "${BLUE}Checking user table columns:${NC}"
USER_COLUMNS=("user_type" "company_name" "verified")

for col in "${USER_COLUMNS[@]}"; do
    if $PSQL_CMD -c "SELECT $col FROM \"user\" LIMIT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Column exists: user.$col"
    else
        echo -e "${RED}✗${NC} Column missing: user.$col"
    fi
done

echo ""
echo -e "${GREEN}🎉 Database migration complete!${NC}"
