#!/bin/bash

# REE AI - Automated Test Runner
# Runs all tests in Docker containers

set -e

echo "🧪 REE AI - Automated Testing"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TEST_COMPOSE_FILE="docker-compose.test.yml"
TEST_RESULTS_DIR="./test-results"

# Parse arguments
RUN_FAST=false
RUN_INTEGRATION=false
RUN_E2E=false
RUN_ALL=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --fast)
            RUN_FAST=true
            RUN_ALL=false
            shift
            ;;
        --integration)
            RUN_INTEGRATION=true
            RUN_ALL=false
            shift
            ;;
        --e2e)
            RUN_E2E=true
            RUN_ALL=false
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./run-tests.sh [--fast|--integration|--e2e|--all]"
            exit 1
            ;;
    esac
done

# Create test results directory
mkdir -p "$TEST_RESULTS_DIR"

echo "📋 Test Configuration:"
if [ "$RUN_ALL" = true ]; then
    echo "  - Running: ALL tests"
else
    [ "$RUN_FAST" = true ] && echo "  - Running: Unit tests only"
    [ "$RUN_INTEGRATION" = true ] && echo "  - Running: Integration tests"
    [ "$RUN_E2E" = true ] && echo "  - Running: End-to-end tests"
fi
echo ""

# Function to check if services are healthy
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1

    echo -n "⏳ Waiting for $service to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$TEST_COMPOSE_FILE" ps | grep "$service" | grep -q "healthy"; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e " ${RED}✗${NC}"
    echo -e "${RED}ERROR: $service failed to become healthy${NC}"
    return 1
}

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    docker-compose -f "$TEST_COMPOSE_FILE" down -v
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Step 1: Start infrastructure
echo "🚀 Step 1: Starting infrastructure services..."
docker-compose -f "$TEST_COMPOSE_FILE" up -d postgres redis opensearch ollama
sleep 5

# Wait for infrastructure
check_service_health "postgres" || exit 1
check_service_health "redis" || exit 1
check_service_health "opensearch" || exit 1

echo -e "${GREEN}✓ Infrastructure ready${NC}"
echo ""

# Step 2: Start Service Registry
echo "🚀 Step 2: Starting Service Registry..."
docker-compose -f "$TEST_COMPOSE_FILE" up -d service-registry
check_service_health "service-registry" || exit 1
echo -e "${GREEN}✓ Service Registry ready${NC}"
echo ""

# Step 3: Start Core Services
echo "🚀 Step 3: Starting Core Services..."
docker-compose -f "$TEST_COMPOSE_FILE" up -d core-gateway db-gateway
sleep 5
echo -e "${GREEN}✓ Core Services started${NC}"
echo ""

# Step 4: Start AI Services
echo "🚀 Step 4: Starting AI Services..."
docker-compose -f "$TEST_COMPOSE_FILE" up -d semantic-chunking classification
sleep 5
echo -e "${GREEN}✓ AI Services started${NC}"
echo ""

# Step 5: Start Orchestrator
echo "🚀 Step 5: Starting Orchestrator..."
docker-compose -f "$TEST_COMPOSE_FILE" up -d orchestrator
sleep 5
echo -e "${GREEN}✓ Orchestrator started${NC}"
echo ""

# Wait for all services to register
echo "⏳ Waiting for services to register (10 seconds)..."
sleep 10

# Step 6: Run Tests
echo "🧪 Step 6: Running Tests..."
echo ""

# Build pytest command based on options
PYTEST_ARGS="-v --tb=short --junit-xml=/app/test-results/junit.xml"

if [ "$RUN_ALL" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS /app/tests"
else
    [ "$RUN_FAST" = true ] && PYTEST_ARGS="$PYTEST_ARGS -m unit"
    [ "$RUN_INTEGRATION" = true ] && PYTEST_ARGS="$PYTEST_ARGS -m integration"
    [ "$RUN_E2E" = true ] && PYTEST_ARGS="$PYTEST_ARGS -m e2e"
fi

# Run tests
if docker-compose -f "$TEST_COMPOSE_FILE" run --rm test-runner pytest $PYTEST_ARGS; then
    echo ""
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    TEST_STATUS=0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    TEST_STATUS=1
fi

echo ""
echo "📊 Test Results: $TEST_RESULTS_DIR/junit.xml"
echo ""

exit $TEST_STATUS
