#!/bin/bash

# =============================================================================
# Master Data System - Comprehensive Health Check
# =============================================================================
# This script performs comprehensive health checks on all master data services
# and dependencies to ensure the system is functioning correctly.
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
EXTRACTION_SERVICE_URL="http://localhost:8084"
CRAWLER_SERVICE_URL="http://localhost:8095"
POSTGRES_CONTAINER="ree-ai-postgres"
REDIS_CONTAINER="ree-ai-redis"
DB_USER="ree_ai_user"
DB_NAME="ree_ai"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# =============================================================================
# Utility Functions
# =============================================================================

log_success() {
    echo -e "${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_failure() {
    echo -e "${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Execute SQL query
exec_sql() {
    docker exec $POSTGRES_CONTAINER psql -U $DB_USER -d $DB_NAME -tAc "$1" 2>/dev/null
}

# =============================================================================
# Infrastructure Health Checks
# =============================================================================

check_docker() {
    log_section "Docker Environment"

    if docker --version &> /dev/null; then
        local version=$(docker --version)
        log_success "Docker installed: $version"
    else
        log_failure "Docker not installed or not running"
    fi

    if docker-compose --version &> /dev/null; then
        local version=$(docker-compose --version)
        log_success "docker-compose installed: $version"
    else
        log_failure "docker-compose not installed"
    fi
}

check_postgres() {
    log_section "PostgreSQL Database"

    # Check container running
    if docker ps | grep -q $POSTGRES_CONTAINER; then
        log_success "PostgreSQL container is running"
    else
        log_failure "PostgreSQL container is not running"
        return 1
    fi

    # Check connection
    if docker exec $POSTGRES_CONTAINER pg_isready -U $DB_USER -d $DB_NAME &> /dev/null; then
        log_success "PostgreSQL accepting connections"
    else
        log_failure "Cannot connect to PostgreSQL"
        return 1
    fi

    # Check database size
    local db_size=$(exec_sql "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
    log_success "Database size: $db_size"

    # Check connection count
    local conn_count=$(exec_sql "SELECT count(*) FROM pg_stat_activity WHERE datname='$DB_NAME';")
    log_success "Active connections: $conn_count"

    # Check master data tables
    local required_tables=(
        "cities"
        "districts"
        "property_types"
        "amenities"
        "directions"
        "furniture_types"
        "legal_statuses"
        "view_types"
        "pending_master_data"
        "schema_migrations"
    )

    log_section "Master Data Tables"

    for table in "${required_tables[@]}"; do
        local count=$(exec_sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='$table';")
        if [ "$count" -eq "1" ]; then
            local row_count=$(exec_sql "SELECT COUNT(*) FROM $table;")
            log_success "Table '$table' exists ($row_count rows)"
        else
            log_failure "Table '$table' missing!"
        fi
    done

    # Check translation tables
    log_section "Translation Tables"

    local translation_tables=(
        "cities_translations"
        "districts_translations"
        "property_types_translations"
        "amenities_translations"
    )

    for table in "${translation_tables[@]}"; do
        local count=$(exec_sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='$table';")
        if [ "$count" -eq "1" ]; then
            local row_count=$(exec_sql "SELECT COUNT(*) FROM $table;")
            log_success "Table '$table' exists ($row_count translations)"
        else
            log_failure "Table '$table' missing!"
        fi
    done
}

check_redis() {
    log_section "Redis Cache"

    if docker ps | grep -q $REDIS_CONTAINER; then
        log_success "Redis container is running"
    else
        log_failure "Redis container is not running"
        return 1
    fi

    if docker exec $REDIS_CONTAINER redis-cli ping | grep -q PONG; then
        log_success "Redis responding to PING"
    else
        log_failure "Redis not responding"
        return 1
    fi

    local keys_count=$(docker exec $REDIS_CONTAINER redis-cli DBSIZE | cut -d':' -f2)
    log_success "Redis keys: $keys_count"
}

# =============================================================================
# Service Health Checks
# =============================================================================

check_extraction_service() {
    log_section "Attribute Extraction Service"

    # Check health endpoint
    if curl -sf "$EXTRACTION_SERVICE_URL/health" &> /dev/null; then
        log_success "Health endpoint responding"
    else
        log_failure "Health endpoint not responding"
        return 1
    fi

    # Get service info
    local info=$(curl -sf "$EXTRACTION_SERVICE_URL/info")
    if [ $? -eq 0 ]; then
        log_success "Service info endpoint working"
    else
        log_warning "Service info endpoint not available"
    fi

    # Test extraction endpoint
    log_section "Extraction Functionality"

    local test_query='{"text": "Căn hộ 2PN Quận 1 có hồ bơi", "confidence_threshold": 0.7}'
    local response=$(curl -sf -X POST "$EXTRACTION_SERVICE_URL/extract-with-master-data" \
        -H "Content-Type: application/json" \
        -d "$test_query")

    if [ $? -eq 0 ]; then
        log_success "Extraction endpoint working"

        # Check response structure
        if echo "$response" | grep -q "request_language"; then
            log_success "Language detection working"
        else
            log_failure "Language detection not working"
        fi

        if echo "$response" | grep -q "mapped"; then
            log_success "Master data mapping working"
        else
            log_failure "Master data mapping not working"
        fi

        if echo "$response" | grep -q "raw"; then
            log_success "Raw extraction working"
        else
            log_failure "Raw extraction not working"
        fi
    else
        log_failure "Extraction endpoint not working"
    fi

    # Test admin endpoints
    log_section "Admin API"

    local pending_response=$(curl -sf "$EXTRACTION_SERVICE_URL/admin/pending-items?limit=5")
    if [ $? -eq 0 ]; then
        log_success "Admin pending-items endpoint working"
    else
        log_failure "Admin pending-items endpoint not working"
    fi
}

check_crawler_service() {
    log_section "Crawler Service"

    # Check health endpoint
    if curl -sf "$CRAWLER_SERVICE_URL/health" &> /dev/null; then
        log_success "Health endpoint responding"
    else
        log_failure "Health endpoint not responding"
        return 1
    fi

    # Check crawlers list
    local crawlers=$(curl -sf "$CRAWLER_SERVICE_URL/crawlers")
    if [ $? -eq 0 ]; then
        log_success "Crawlers list endpoint working"

        local crawler_count=$(echo "$crawlers" | grep -o "\"id\"" | wc -l)
        log_success "Available crawlers: $crawler_count"
    else
        log_failure "Crawlers list endpoint not working"
    fi
}

# =============================================================================
# Data Quality Checks
# =============================================================================

check_data_quality() {
    log_section "Master Data Quality"

    # Check for missing translations
    local missing_translations=$(exec_sql "
        SELECT COUNT(*) FROM (
            SELECT d.id FROM districts d
            LEFT JOIN districts_translations dt ON d.id = dt.district_id AND dt.lang_code = 'vi'
            WHERE dt.id IS NULL
        ) AS missing;
    ")

    if [ "$missing_translations" -eq "0" ]; then
        log_success "All districts have Vietnamese translations"
    else
        log_warning "Missing Vietnamese translations for $missing_translations districts"
    fi

    # Check pending items count
    local pending_count=$(exec_sql "SELECT COUNT(*) FROM pending_master_data WHERE status = 'pending';")
    if [ "$pending_count" -gt "0" ]; then
        log_warning "Pending master data items requiring review: $pending_count"
    else
        log_success "No pending master data items"
    fi

    # Check for duplicate names in master data
    local duplicate_districts=$(exec_sql "SELECT COUNT(*) FROM (SELECT name FROM districts GROUP BY name HAVING COUNT(*) > 1) AS dupes;")
    if [ "$duplicate_districts" -eq "0" ]; then
        log_success "No duplicate district names"
    else
        log_failure "Found $duplicate_districts duplicate district names"
    fi
}

# =============================================================================
# Performance Checks
# =============================================================================

check_performance() {
    log_section "Performance Metrics"

    # Measure extraction response time
    local start_time=$(date +%s%3N)
    curl -sf -X POST "$EXTRACTION_SERVICE_URL/extract-with-master-data" \
        -H "Content-Type: application/json" \
        -d '{"text": "Căn hộ 2PN Quận 1"}' > /dev/null
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))

    if [ "$response_time" -lt 2000 ]; then
        log_success "Extraction response time: ${response_time}ms (target: <2000ms)"
    else
        log_warning "Extraction response time: ${response_time}ms (slower than target)"
    fi

    # Check PostgreSQL query performance
    local query_time=$(exec_sql "
        EXPLAIN ANALYZE SELECT d.*, dt.translated_text
        FROM districts d
        LEFT JOIN districts_translations dt ON d.id = dt.district_id
        WHERE dt.lang_code = 'vi' LIMIT 10;
    " | grep "Execution Time" | awk '{print $3}')

    log_success "PostgreSQL query time: ${query_time}ms"
}

# =============================================================================
# Summary Report
# =============================================================================

print_summary() {
    echo ""
    echo "======================================================================="
    echo "  Health Check Summary"
    echo "======================================================================="
    echo ""

    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    local success_rate=$((TESTS_PASSED * 100 / total_tests))

    echo -e "${GREEN}✓ Passed:${NC}  $TESTS_PASSED"
    echo -e "${RED}✗ Failed:${NC}  $TESTS_FAILED"
    echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
    echo ""
    echo "Success Rate: $success_rate%"
    echo ""

    if [ $TESTS_FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ System is healthy!${NC}"
        return 0
    elif [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${YELLOW}⚠️ System is operational with warnings${NC}"
        return 0
    else
        echo -e "${RED}❌ System has critical issues${NC}"
        return 1
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo "======================================================================="
    echo "  Master Data System - Health Check"
    echo "======================================================================="

    check_docker
    check_postgres
    check_redis
    check_extraction_service
    check_crawler_service
    check_data_quality
    check_performance

    print_summary
}

main "$@"
