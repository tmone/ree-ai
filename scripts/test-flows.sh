#!/bin/bash
#
# Comprehensive Flow Testing Script
# Tests all 3 main flows based on architecture diagrams
#

set -e

echo "======================================================================================================"
echo "🧪 REE AI - Comprehensive Flow Testing"
echo "======================================================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Start services if not running
echo -e "${YELLOW}📦 Checking services...${NC}"
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}🚀 Starting services...${NC}"
    docker-compose --profile real up -d

    echo -e "${YELLOW}⏳ Waiting for services to be healthy (30s)...${NC}"
    sleep 30
fi

# Verify critical services
echo -e "${YELLOW}✓ Verifying services...${NC}"
services=(
    "Service Registry:8000"
    "Orchestrator:8090"
    "Classification:8083"
    "Extraction:8084"
    "Completeness:8086"
    "DB Gateway:8081"
)

all_healthy=true
for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"

    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ $name${NC}"
    else
        echo -e "  ${RED}❌ $name (port $port not responding)${NC}"
        all_healthy=false
    fi
done

if [ "$all_healthy" = false ]; then
    echo ""
    echo -e "${RED}❌ Some services are not healthy. Please check logs:${NC}"
    echo "  docker-compose logs -f orchestrator"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All services healthy!${NC}"
echo ""

# Run tests
echo -e "${YELLOW}🧪 Running comprehensive flow tests...${NC}"
echo ""

docker run --rm --network host \
    -v "$(pwd):/app" -w /app \
    python:3.11-slim bash -c "pip install -q asyncpg httpx && python tests/test_flow_comprehensive.py"

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ All tests completed!${NC}"
else
    echo -e "${RED}❌ Tests failed with exit code $exit_code${NC}"
fi

echo ""
echo "======================================================================================================"
echo "📁 Test results saved to: flow_test_results_*.json"
echo "======================================================================================================"

exit $exit_code
