#!/bin/bash

# Quick deployment test script
# Run this to test the production deployment

SERVER_IP="192.168.1.11"
TIMEOUT=10

echo "🧪 Testing REE AI Production Deployment"
echo "======================================"
echo "Server: $SERVER_IP"
echo "Timeout: ${TIMEOUT}s per service"
echo ""

# Array of services to test
declare -a services=(
    "3000:Open WebUI (Frontend)"
    "8000:Service Registry"
    "8080:Core Gateway" 
    "8081:DB Gateway"
    "8090:Orchestrator"
    "8091:RAG Service"
    "3002:Admin Dashboard"
    "9200:OpenSearch"
)

# Test function
test_service() {
    local port=$1
    local name=$2
    local url="http://${SERVER_IP}:${port}"
    
    echo -n "Testing $name ($url)... "
    
    if timeout $TIMEOUT curl -f -s "$url" >/dev/null 2>&1; then
        echo "✅ OK"
        return 0
    elif timeout $TIMEOUT curl -s "$url/health" >/dev/null 2>&1; then
        echo "✅ OK (health endpoint)"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

# Test all services
failed=0
passed=0

echo "🔍 Testing Services:"
echo "==================="

for service in "${services[@]}"; do
    IFS=':' read -r port name <<< "$service"
    if test_service "$port" "$name"; then
        ((passed++))
    else
        ((failed++))
    fi
done

echo ""
echo "📊 Test Results:"
echo "==============="
echo "✅ Passed: $passed"
echo "❌ Failed: $failed"
echo "Total: $((passed + failed))"

# Test specific API endpoints
echo ""
echo "🔧 API Tests:"
echo "============="

# Test health endpoints
health_endpoints=(
    "8000:/health:Service Registry"
    "8080:/health:Core Gateway"
    "8081:/health:DB Gateway" 
    "8090:/health:Orchestrator"
    "8091:/health:RAG Service"
)

api_passed=0
api_failed=0

for endpoint in "${health_endpoints[@]}"; do
    IFS=':' read -r port path name <<< "$endpoint"
    url="http://${SERVER_IP}:${port}${path}"
    echo -n "Testing $name health... "
    
    if timeout $TIMEOUT curl -f -s "$url" >/dev/null 2>&1; then
        echo "✅ OK"
        ((api_passed++))
    else
        echo "❌ FAIL"
        ((api_failed++))
    fi
done

# Test orchestrator API
echo -n "Testing Orchestrator API... "
orchestrator_test=$(timeout $TIMEOUT curl -s -X POST "http://${SERVER_IP}:8090/orchestrate" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test_user","query":"hello"}' 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$orchestrator_test" ]; then
    echo "✅ OK"
    ((api_passed++))
else
    echo "❌ FAIL"
    ((api_failed++))
fi

echo ""
echo "📊 API Test Results:"
echo "==================="
echo "✅ Passed: $api_passed"
echo "❌ Failed: $api_failed"

# Overall summary
echo ""
echo "🎯 Overall Summary:"
echo "==================="

total_tests=$((passed + failed + api_passed + api_failed))
total_passed=$((passed + api_passed))
total_failed=$((failed + api_failed))

echo "Total Tests: $total_tests"
echo "✅ Total Passed: $total_passed"
echo "❌ Total Failed: $total_failed"

if [ $total_failed -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! Deployment is successful!"
    echo ""
    echo "🌐 Access URLs:"
    echo "  - Open WebUI: http://${SERVER_IP}:3000"
    echo "  - Admin Dashboard: http://${SERVER_IP}:3002"
    echo "  - API Gateway: http://${SERVER_IP}:8080"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Check the deployment."
    echo ""
    echo "🔧 Debug commands:"
    echo "  ssh tmone@${SERVER_IP} 'cd ~/ree-ai && ./status-ree-ai.sh'"
    echo "  ssh tmone@${SERVER_IP} 'cd ~/ree-ai && ./logs-ree-ai.sh'"
    exit 1
fi