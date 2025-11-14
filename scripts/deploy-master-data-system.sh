#!/bin/bash

# =============================================================================
# Master Data Extraction System - Deployment Script
# =============================================================================
# This script automates the deployment of the complete master data system:
# - PostgreSQL schema migrations
# - Attribute Extraction Service
# - Crawler Service
# - Health checks and validation
# =============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# Service configuration
POSTGRES_CONTAINER="ree-ai-postgres"
EXTRACTION_SERVICE_PORT=8084
CRAWLER_SERVICE_PORT=8095
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_DELAY=2

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

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

wait_for_postgres() {
    log_info "Waiting for PostgreSQL to be ready..."

    retries=0
    while [ $retries -lt $HEALTH_CHECK_RETRIES ]; do
        if docker exec $POSTGRES_CONTAINER pg_isready -U ree_ai_user -d ree_ai &> /dev/null; then
            log_info "PostgreSQL is ready!"
            return 0
        fi

        retries=$((retries + 1))
        log_warning "PostgreSQL not ready yet (attempt $retries/$HEALTH_CHECK_RETRIES)..."
        sleep $HEALTH_CHECK_DELAY
    done

    log_error "PostgreSQL failed to become ready after $HEALTH_CHECK_RETRIES attempts"
    return 1
}

wait_for_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-/health}

    log_info "Waiting for $service_name to be ready..."

    retries=0
    while [ $retries -lt $HEALTH_CHECK_RETRIES ]; do
        if curl -sf "http://localhost:$port$endpoint" &> /dev/null; then
            log_info "$service_name is ready!"
            return 0
        fi

        retries=$((retries + 1))
        log_warning "$service_name not ready yet (attempt $retries/$HEALTH_CHECK_RETRIES)..."
        sleep $HEALTH_CHECK_DELAY
    done

    log_error "$service_name failed to become ready after $HEALTH_CHECK_RETRIES attempts"
    return 1
}

# =============================================================================
# Deployment Steps
# =============================================================================

step_check_prerequisites() {
    log_info "Step 1/7: Checking prerequisites..."

    check_command docker
    check_command docker-compose
    check_command psql
    check_command curl

    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env file not found at $ENV_FILE"
        log_info "Please copy .env.example to .env and configure it"
        exit 1
    fi

    log_info "All prerequisites met ✓"
}

step_start_infrastructure() {
    log_info "Step 2/7: Starting infrastructure services..."

    cd "$PROJECT_ROOT"

    # Start PostgreSQL and Redis
    docker-compose up -d postgres redis

    wait_for_postgres || exit 1

    log_info "Infrastructure services started ✓"
}

step_run_migrations() {
    log_info "Step 3/7: Running database migrations..."

    # Run master data schema migration
    log_info "Creating master data schema..."
    docker exec -i $POSTGRES_CONTAINER psql -U ree_ai_user -d ree_ai < \
        "$PROJECT_ROOT/database/migrations/001_create_master_data_schema.sql"

    # Run seed data migration
    log_info "Seeding master data..."
    docker exec -i $POSTGRES_CONTAINER psql -U ree_ai_user -d ree_ai < \
        "$PROJECT_ROOT/database/migrations/002_seed_master_data.sql"

    log_info "Database migrations completed ✓"
}

step_verify_schema() {
    log_info "Step 4/7: Verifying database schema..."

    # Check that master data tables exist
    local tables=(
        "cities"
        "districts"
        "property_types"
        "amenities"
        "directions"
        "furniture_types"
        "pending_master_data"
    )

    for table in "${tables[@]}"; do
        count=$(docker exec $POSTGRES_CONTAINER psql -U ree_ai_user -d ree_ai -tAc \
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='$table';")

        if [ "$count" -eq "1" ]; then
            log_info "Table '$table' exists ✓"
        else
            log_error "Table '$table' not found!"
            exit 1
        fi
    done

    # Check seed data
    log_info "Checking seed data..."

    districts_count=$(docker exec $POSTGRES_CONTAINER psql -U ree_ai_user -d ree_ai -tAc \
        "SELECT COUNT(*) FROM districts;")
    log_info "Districts seeded: $districts_count"

    amenities_count=$(docker exec $POSTGRES_CONTAINER psql -U ree_ai_user -d ree_ai -tAc \
        "SELECT COUNT(*) FROM amenities;")
    log_info "Amenities seeded: $amenities_count"

    log_info "Schema verification completed ✓"
}

step_start_services() {
    log_info "Step 5/7: Starting master data services..."

    cd "$PROJECT_ROOT"

    # Start Attribute Extraction Service
    docker-compose up -d attribute-extraction

    # Start Crawler Service
    docker-compose up -d crawler-service

    log_info "Services started ✓"
}

step_health_checks() {
    log_info "Step 6/7: Running health checks..."

    # Check Attribute Extraction Service
    wait_for_service "Attribute Extraction Service" $EXTRACTION_SERVICE_PORT || exit 1

    # Check Crawler Service
    wait_for_service "Crawler Service" $CRAWLER_SERVICE_PORT || exit 1

    log_info "All services healthy ✓"
}

step_smoke_tests() {
    log_info "Step 7/7: Running smoke tests..."

    # Test extraction endpoint
    log_info "Testing extraction endpoint..."
    response=$(curl -sf -X POST "http://localhost:$EXTRACTION_SERVICE_PORT/extract-with-master-data" \
        -H "Content-Type: application/json" \
        -d '{"text": "Căn hộ 2PN Quận 1", "confidence_threshold": 0.7}')

    if [ $? -eq 0 ]; then
        log_info "Extraction endpoint working ✓"
    else
        log_error "Extraction endpoint test failed!"
        exit 1
    fi

    # Test crawler endpoint
    log_info "Testing crawler endpoint..."
    response=$(curl -sf "http://localhost:$CRAWLER_SERVICE_PORT/crawlers")

    if [ $? -eq 0 ]; then
        log_info "Crawler endpoint working ✓"
    else
        log_error "Crawler endpoint test failed!"
        exit 1
    fi

    log_info "Smoke tests completed ✓"
}

# =============================================================================
# Rollback Function
# =============================================================================

rollback() {
    log_warning "Rolling back deployment..."

    # Stop services
    docker-compose stop attribute-extraction crawler-service

    # Rollback migrations (if needed)
    # Note: Add specific rollback SQL if required

    log_info "Rollback completed"
    exit 1
}

# =============================================================================
# Main Deployment Flow
# =============================================================================

main() {
    echo "======================================================================="
    echo "  Master Data Extraction System - Deployment"
    echo "======================================================================="
    echo ""

    # Set trap for errors
    trap rollback ERR

    # Execute deployment steps
    step_check_prerequisites
    step_start_infrastructure
    step_run_migrations
    step_verify_schema
    step_start_services
    step_health_checks
    step_smoke_tests

    echo ""
    echo "======================================================================="
    echo "  ✅ Deployment Completed Successfully!"
    echo "======================================================================="
    echo ""
    echo "Services available at:"
    echo "  - Attribute Extraction: http://localhost:$EXTRACTION_SERVICE_PORT"
    echo "  - Crawler Service: http://localhost:$CRAWLER_SERVICE_PORT"
    echo ""
    echo "API Documentation:"
    echo "  - http://localhost:$EXTRACTION_SERVICE_PORT/docs"
    echo "  - http://localhost:$CRAWLER_SERVICE_PORT/docs"
    echo ""
    echo "Next steps:"
    echo "  1. Run integration tests: pytest tests/integration/"
    echo "  2. Check service logs: docker-compose logs -f attribute-extraction"
    echo "  3. Start crawling: curl -X POST http://localhost:$CRAWLER_SERVICE_PORT/crawl ..."
    echo ""
}

# Run main function
main "$@"
