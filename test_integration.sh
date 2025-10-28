#!/bin/bash

# REE AI - Integration Test Script
# Tests all services end-to-end

set -e

echo "🧪 REE AI - Integration Testing"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0

# Helper function
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=${4:-}

    echo -n "Testing $name... "

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo "000")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        echo "   Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "📍 Step 1: Check Infrastructure"
echo "--------------------------------"
test_endpoint "PostgreSQL" "http://localhost:5432" || echo "⚠️  PostgreSQL not accessible via HTTP (expected)"
test_endpoint "Redis" "http://localhost:6379" || echo "⚠️  Redis not accessible via HTTP (expected)"
test_endpoint "OpenSearch" "http://localhost:9200"
echo ""

echo "📍 Step 2: Check Mock Services"
echo "-------------------------------"
test_endpoint "Mock Core Gateway Health" "http://localhost:8000/mockserver/status"
test_endpoint "Mock DB Gateway Health" "http://localhost:8001/mockserver/status"
echo ""

echo "📍 Step 3: Test Mock Core Gateway"
echo "----------------------------------"
test_endpoint "Mock Core Gateway - Chat Completions" \
    "http://localhost:8000/v1/chat/completions" \
    "POST" \
    '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'
echo ""

echo "📍 Step 4: Test Mock DB Gateway"
echo "--------------------------------"
test_endpoint "Mock DB Gateway - Search" \
    "http://localhost:8001/search" \
    "POST" \
    '{"query":"Tìm nhà","filters":{},"limit":10}'
echo ""

echo "📍 Step 5: Check Real Services (if running)"
echo "--------------------------------------------"
test_endpoint "Core Gateway Health" "http://localhost:8080/health" || echo "⚠️  Core Gateway not running (use: make start-real)"
test_endpoint "DB Gateway Health" "http://localhost:8081/health" || echo "⚠️  DB Gateway not running"
test_endpoint "Semantic Chunking Health" "http://localhost:8082/health" || echo "⚠️  Semantic Chunking not running"
echo ""

if [ "$FAILED" -eq 0 ] && [ "$PASSED" -gt 0 ]; then
    echo ""
    echo "========================================="
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "========================================="
    echo "Total: $PASSED passed, $FAILED failed"
    echo ""
    echo "✅ Infrastructure is ready for development!"
    echo ""
    exit 0
else
    echo ""
    echo "========================================="
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo "========================================="
    echo "Total: $PASSED passed, $FAILED failed"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Docker services: docker-compose ps"
    echo "2. Check logs: docker-compose logs"
    echo "3. Restart services: make start-mock"
    echo ""
    exit 1
fi
