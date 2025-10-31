#!/bin/bash

# REE AI - Comprehensive Integration Test
# Tests all major functionality including failover mechanism

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test results array
declare -a TEST_RESULTS

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}[TEST $((TOTAL_TESTS + 1))]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ PASS:${NC} $1"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
    TEST_RESULTS+=("✅ $1")
}

print_failure() {
    echo -e "${RED}❌ FAIL:${NC} $1"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    TEST_RESULTS+=("❌ $1")
}

print_info() {
    echo -e "${BLUE}ℹ️${NC}  $1"
}

# Test 1: Service Health Checks
test_health_checks() {
    print_header "Test 1: Service Health Checks"

    # Test Service Registry
    print_test "Service Registry health check"
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Service Registry is healthy"
    else
        print_failure "Service Registry is unhealthy"
    fi

    # Test Core Gateway
    print_test "Core Gateway health check"
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Core Gateway is healthy"
    else
        print_failure "Core Gateway is unhealthy"
    fi

    # Test Orchestrator
    print_test "Orchestrator health check"
    if curl -sf http://localhost:8090/health > /dev/null 2>&1; then
        print_success "Orchestrator is healthy"
    else
        print_failure "Orchestrator is unhealthy"
    fi
}

# Test 2: Service Registry
test_service_registry() {
    print_header "Test 2: Service Registry"

    print_test "Get list of registered services"
    SERVICES=$(curl -s http://localhost:8000/services)

    if echo "$SERVICES" | jq -e '.services | length > 0' > /dev/null 2>&1; then
        SERVICE_COUNT=$(echo "$SERVICES" | jq '.services | length')
        print_success "Service Registry has $SERVICE_COUNT registered services"
        print_info "Registered services: $(echo "$SERVICES" | jq -r '.services[].name' | tr '\n' ', ')"
    else
        print_failure "Service Registry has no services registered"
    fi
}

# Test 3: Direct Ollama Call
test_direct_ollama() {
    print_header "Test 3: Direct Ollama Call (via ollama/ prefix)"

    print_test "Calling Core Gateway with ollama/qwen2.5:0.5b"

    RESPONSE=$(curl -s -X POST http://localhost:8080/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "ollama/qwen2.5:0.5b",
            "messages": [{"role": "user", "content": "What is 1+1?"}],
            "max_tokens": 10
        }')

    if echo "$RESPONSE" | jq -e '.content' > /dev/null 2>&1; then
        CONTENT=$(echo "$RESPONSE" | jq -r '.content')
        MODEL=$(echo "$RESPONSE" | jq -r '.model')
        print_success "Direct Ollama call successful"
        print_info "Model: $MODEL"
        print_info "Response: $CONTENT"
    else
        print_failure "Direct Ollama call failed"
        print_info "Response: $RESPONSE"
    fi
}

# Test 4: OpenAI → Ollama Failover
test_failover() {
    print_header "Test 4: OpenAI → Ollama Failover"

    print_test "Triggering failover (OpenAI rate limit → Ollama)"
    print_info "This will hit OpenAI rate limit and fallback to Ollama"

    

    RESPONSE=$(curl -s -X POST http://localhost:8080/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }')

    
    

    if echo "$RESPONSE" | jq -e '.content' > /dev/null 2>&1; then
        CONTENT=$(echo "$RESPONSE" | jq -r '.content')
        MODEL=$(echo "$RESPONSE" | jq -r '.model')
        ID=$(echo "$RESPONSE" | jq -r '.id')

        # Check if it's from Ollama (id starts with "ollama-")
        if [[ "$ID" == ollama-* ]]; then
            print_success "Failover to Ollama successful "
            print_info "Fallback Model: $MODEL"
            print_info "Response: $CONTENT"
        else
            print_info "Request served by OpenAI (no failover needed)"
            print_info "Model: $MODEL"
        fi
    else
        print_failure "Failover test failed"
        print_info "Response: $RESPONSE"
    fi
}

# Test 5: Orchestrator Integration
test_orchestrator() {
    print_header "Test 5: Orchestrator Integration"

    print_test "Calling Orchestrator endpoint"

    RESPONSE=$(curl -s -X POST http://localhost:8090/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "What is AI?"}],
            "max_tokens": 20
        }')

    if echo "$RESPONSE" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
        print_success "Orchestrator successfully routed request"
        print_info "Response: ${CONTENT:0:100}..."
    else
        print_failure "Orchestrator request failed"
        print_info "Response: $RESPONSE"
    fi
}

# Test 6: Multiple Sequential Requests (Stress Test)
test_stress() {
    print_header "Test 6: Stress Test (5 sequential requests)"

    SUCCESS_COUNT=0
    

    for i in {1..5}; do
        print_test "Request $i/5"

        
        RESPONSE=$(curl -s -X POST http://localhost:8080/chat/completions \
            -H "Content-Type: application/json" \
            -d "{
                \"model\": \"gpt-4o-mini\",
                \"messages\": [{\"role\": \"user\", \"content\": \"Count to $i\"}],
                \"max_tokens\": 10
            }")
        
        
        

        if echo "$RESPONSE" | jq -e '.content' > /dev/null 2>&1; then
            ((SUCCESS_COUNT++))
            print_info "Request $i succeeded "
        else
            print_info "Request $i failed"
        fi
    done

    

    if [ $SUCCESS_COUNT -eq 5 ]; then
        print_success "All 5 requests successful "
    elif [ $SUCCESS_COUNT -ge 3 ]; then
        print_success "$SUCCESS_COUNT/5 requests successful "
    else
        print_failure "Only $SUCCESS_COUNT/5 requests successful"
    fi
}

# Test 7: Error Handling
test_error_handling() {
    print_header "Test 7: Error Handling"

    # Test with invalid model
    print_test "Request with invalid model (should fail gracefully)"
    RESPONSE=$(curl -s -X POST http://localhost:8080/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "invalid-model-xyz",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }')

    if echo "$RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.detail')
        print_success "Error handled gracefully"
        print_info "Error: $ERROR_MSG"
    else
        print_failure "Error not handled properly"
    fi

    # Test with empty message
    print_test "Request with empty messages (should fail gracefully)"
    RESPONSE=$(curl -s -X POST http://localhost:8080/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "gpt-4o-mini",
            "messages": [],
            "max_tokens": 10
        }')

    if echo "$RESPONSE" | jq -e 'has("detail") or has("error")' > /dev/null 2>&1; then
        print_success "Empty message handled gracefully"
    else
        print_failure "Empty message not handled properly"
    fi
}

# Test 8: Response Format Validation
test_response_format() {
    print_header "Test 8: Response Format Validation"

    print_test "Validating response schema"

    RESPONSE=$(curl -s -X POST http://localhost:8080/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }')

    # Check required fields
    HAS_ID=$(echo "$RESPONSE" | jq -e 'has("id")' > /dev/null 2>&1 && echo "yes" || echo "no")
    HAS_MODEL=$(echo "$RESPONSE" | jq -e 'has("model")' > /dev/null 2>&1 && echo "yes" || echo "no")
    HAS_CONTENT=$(echo "$RESPONSE" | jq -e 'has("content")' > /dev/null 2>&1 && echo "yes" || echo "no")
    HAS_ROLE=$(echo "$RESPONSE" | jq -e 'has("role")' > /dev/null 2>&1 && echo "yes" || echo "no")
    HAS_USAGE=$(echo "$RESPONSE" | jq -e 'has("usage")' > /dev/null 2>&1 && echo "yes" || echo "no")

    if [ "$HAS_ID" == "yes" ] && [ "$HAS_MODEL" == "yes" ] && [ "$HAS_CONTENT" == "yes" ] && [ "$HAS_ROLE" == "yes" ]; then
        print_success "Response schema is valid"
        print_info "Has id: $HAS_ID, model: $HAS_MODEL, content: $HAS_CONTENT, role: $HAS_ROLE, usage: $HAS_USAGE"
    else
        print_failure "Response schema is invalid"
    fi
}

# Main execution
main() {
    print_header "REE AI - Comprehensive Integration Test Suite"
    print_info "Starting comprehensive tests..."
    print_info "Date: $(date)"
    echo ""

    # Run all tests
    test_health_checks
    test_service_registry
    test_direct_ollama
    test_failover
    test_orchestrator
    test_stress
    test_error_handling
    test_response_format

    # Print summary
    print_header "Test Summary"
    echo ""
    for result in "${TEST_RESULTS[@]}"; do
        echo "$result"
    done

    echo ""
    echo -e "${BLUE}Total Tests:${NC} $TOTAL_TESTS"
    echo -e "${GREEN}Passed:${NC} $PASSED_TESTS"
    echo -e "${RED}Failed:${NC} $FAILED_TESTS"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}⚠️  Some tests failed!${NC}"
        exit 1
    fi
}

# Run main
main
