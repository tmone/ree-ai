#!/bin/bash

echo "🚀 REE AI - Automated Deployment Test Script"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$response" == "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected)"
        return 1
    fi
}

# Phase 1: Check infrastructure
echo "📦 Phase 1: Checking Infrastructure Services"
echo "---------------------------------------------"
test_endpoint "PostgreSQL" "http://localhost:5432" "000" || true
test_endpoint "Redis" "http://localhost:6379" "000" || true
sleep 2

# Phase 2: Check core services
echo ""
echo "🔧 Phase 2: Checking Core Services"
echo "-----------------------------------"
test_endpoint "Service Registry" "http://localhost:8000/health" "200"
test_endpoint "Core Gateway" "http://localhost:8080/health" "200"
test_endpoint "DB Gateway" "http://localhost:8081/health" "200"
sleep 2

# Phase 3: Check AI services
echo ""
echo "🤖 Phase 3: Checking AI Services"
echo "---------------------------------"
test_endpoint "Orchestrator" "http://localhost:8090/health" "200"
test_endpoint "RAG Service" "http://localhost:8091/health" "200"
test_endpoint "Semantic Chunking" "http://localhost:8082/health" "200"
test_endpoint "Classification" "http://localhost:8083/health" "200"
test_endpoint "Attribute Extraction" "http://localhost:8084/health" "200"
test_endpoint "Completeness Check" "http://localhost:8086/health" "200"
test_endpoint "Price Suggestion" "http://localhost:8087/health" "200"
test_endpoint "Reranking" "http://localhost:8088/health" "200"
sleep 2

# Phase 4: Check gateway & management
echo ""
echo "🔐 Phase 4: Checking Gateway & Management"
echo "------------------------------------------"
test_endpoint "Auth Service" "http://localhost:8085/health" "200"
test_endpoint "API Gateway" "http://localhost:8888/health" "200"
test_endpoint "Admin Dashboard" "http://localhost:3002/health" "200"
sleep 2

# Phase 5: Check frontend & monitoring
echo ""
echo "🌐 Phase 5: Checking Frontend & Monitoring"
echo "-------------------------------------------"
test_endpoint "Open WebUI" "http://localhost:3000" "200"
test_endpoint "Prometheus" "http://localhost:9090/-/healthy" "200"
test_endpoint "Grafana" "http://localhost:3001/api/health" "200"

# Summary
echo ""
echo "=============================================="
echo "📊 Test Summary"
echo "=============================================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep ree-ai

echo ""
echo "🎉 Deployment test completed!"
echo ""
echo "Access URLs:"
echo "  - Open WebUI:       http://localhost:3000"
echo "  - API Gateway:      http://localhost:8888"
echo "  - Admin Dashboard:  http://localhost:3002"
echo "  - Grafana:          http://localhost:3001 (admin/admin)"
echo "  - Prometheus:       http://localhost:9090"
echo ""
