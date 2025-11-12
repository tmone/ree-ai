#!/bin/bash

# Test deployment status script
echo "🧪 Testing REE AI Deployment Status"
echo "===================================="
echo ""

# Check if we have the required commands
if ! command -v curl &> /dev/null; then
    echo "❌ curl not found. Please install curl"
    exit 1
fi

echo "🔍 Testing Production Deployment..."
echo "Server: 192.168.1.11"
echo ""

# Test function
test_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    echo -n "Testing $name... "
    
    if timeout $timeout curl -f -s "$url" >/dev/null 2>&1; then
        echo "✅ OK"
        return 0
    elif timeout $timeout curl -s "$url" | grep -q "html\|json\|REE" 2>/dev/null; then
        echo "✅ OK (responding)"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

# Production endpoints
echo "📊 Production Services (192.168.1.11):"
echo "======================================"
production_endpoints=(
    "http://192.168.1.11:3000:Open WebUI"
    "http://192.168.1.11:8080/health:Core Gateway"
    "http://192.168.1.11:8000/health:Service Registry"
    "http://192.168.1.11:8090/health:Orchestrator"
    "http://192.168.1.11:8091/health:RAG Service"
    "http://192.168.1.11:3002:Admin Dashboard"
)

prod_passed=0
prod_failed=0

for endpoint in "${production_endpoints[@]}"; do
    IFS=':' read -r url name <<< "$endpoint"
    if test_endpoint "$url" "$name"; then
        ((prod_passed++))
    else
        ((prod_failed++))
    fi
done

echo ""
echo "📊 Production Results:"
echo "✅ Passed: $prod_passed"
echo "❌ Failed: $prod_failed"

# WSL endpoints (if accessible)
echo ""
echo "🖥️ WSL Test Services (localhost):"
echo "=================================="
wsl_endpoints=(
    "http://localhost:4000:Open WebUI"
    "http://localhost:9080/health:Core Gateway"
    "http://localhost:9000/health:Service Registry"
    "http://localhost:9090/health:Orchestrator"
    "http://localhost:9091/health:RAG Service"
    "http://localhost:4002:Admin Dashboard"
)

wsl_passed=0
wsl_failed=0

for endpoint in "${wsl_endpoints[@]}"; do
    IFS=':' read -r url name <<< "$endpoint"
    if test_endpoint "$url" "$name"; then
        ((wsl_passed++))
    else
        ((wsl_failed++))
    fi
done

echo ""
echo "📊 WSL Results:"
echo "✅ Passed: $wsl_passed"
echo "❌ Failed: $wsl_failed"

# Overall summary
echo ""
echo "🎯 Overall Summary:"
echo "==================="
total_tests=$((prod_passed + prod_failed + wsl_passed + wsl_failed))
total_passed=$((prod_passed + wsl_passed))
total_failed=$((prod_failed + wsl_failed))

echo "Total Tests: $total_tests"
echo "✅ Total Passed: $total_passed"
echo "❌ Total Failed: $total_failed"

# Status
if [ $prod_passed -gt 0 ] && [ $prod_failed -eq 0 ]; then
    echo ""
    echo "🎉 Production deployment successful!"
    echo "🌐 Access: http://192.168.1.11:3000"
elif [ $prod_passed -gt 0 ]; then
    echo ""
    echo "⚠️ Production partially deployed"
    echo "🔧 Some services may need attention"
else
    echo ""
    echo "❌ Production deployment failed"
    echo "🔍 Check GitHub Actions logs"
fi

if [ $wsl_passed -gt 0 ] && [ $wsl_failed -eq 0 ]; then
    echo "✅ WSL test environment healthy!"
elif [ $wsl_passed -gt 0 ]; then
    echo "⚠️ WSL test environment partially working"
else
    echo "❌ WSL test environment not accessible"
fi

echo ""
echo "🔗 Useful Links:"
echo "  - GitHub Actions: https://github.com/tmone/ree-ai/actions"
echo "  - Production UI: http://192.168.1.11:3000"
echo "  - WSL Test UI: http://localhost:4000"
echo ""