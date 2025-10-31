#!/bin/bash

# REE AI - Comprehensive Test Execution Script
# Runs all test categories and generates summary report

set -e

echo "=================================="
echo "REE AI - Comprehensive Test Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "📋 Test Categories:"
echo "  1. AI Quality Tests (13 tests)"
echo "  2. Failover Mechanism Tests (12 tests)"
echo "  3. Infrastructure Tests (16 tests)"
echo "  Total: 41 comprehensive tests"
echo ""

# Check services
echo "🔍 Checking service health..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Core Gateway: healthy${NC}"
else
    echo -e "${RED}❌ Core Gateway: down${NC}"
fi

if curl -s http://localhost:8090/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Orchestrator: healthy${NC}"
else
    echo -e "${RED}❌ Orchestrator: down${NC}"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service Registry: healthy${NC}"
else
    echo -e "${YELLOW}⚠️ Service Registry: unhealthy (tests may be limited)${NC}"
fi

echo ""
echo "🚀 Running tests..."
echo ""

# Run tests by category
echo "=================================="
echo "1. AI Quality Tests"
echo "=================================="
python3 -m pytest tests/test_ai_quality.py -v -m "not slow" --tb=short || true
echo ""

echo "=================================="
echo "2. Failover Mechanism Tests"
echo "=================================="
python3 -m pytest tests/test_failover_mechanism.py -v -m "not slow" --tb=short || true
echo ""

echo "=================================="
echo "3. Infrastructure Tests"
echo "=================================="
python3 -m pytest tests/test_infrastructure.py -v -m "not slow" --tb=short || true
echo ""

# Summary
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
python3 -m pytest tests/ --collect-only -q 2>&1 | tail -5
echo ""

echo "=================================="
echo "🎯 Critical Tests"
echo "=================================="
python3 -m pytest tests/ -v -m critical --tb=line 2>&1 | tail -20
echo ""

echo "=================================="
echo "✅ Test execution complete!"
echo "=================================="
echo ""
echo "📖 For detailed results, see:"
echo "  - Test report: tests/COMPREHENSIVE_TEST_REPORT.md"
echo "  - Test README: tests/README.md"
echo ""
echo "📌 Quick commands:"
echo "  make test-quick      # Run quick tests"
echo "  make test-critical   # Run critical tests only"
echo "  make test-ai         # Run AI quality tests"
echo "  make test-failover   # Run failover tests"
echo "  make test-coverage   # Run with coverage report"
echo ""
