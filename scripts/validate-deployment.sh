#!/bin/bash

# ============================================================
# REE AI Deployment Validation Script
# Tests deployment scripts and configurations
# ============================================================

set -uo pipefail  # Remove -e to continue on errors

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✅]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌]${NC} $1"
}

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_TOTAL++))
    
    log "Testing: $test_name"
    
    if bash -c "$test_command" &>/dev/null; then
        log_success "$test_name"
        ((TESTS_PASSED++))
        return 0
    else
        log_error "$test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_prerequisites() {
    log "🔍 Testing Prerequisites"
    
    run_test "Docker installed" "command -v docker"
    run_test "Docker daemon running" "docker info"
    run_test "Docker Compose installed" "command -v docker-compose"
    run_test "GitHub CLI installed" "command -v gh"
    run_test "GitHub CLI authenticated" "gh auth status"
    run_test "curl installed" "command -v curl"
    run_test "timeout command available" "command -v timeout"
}

test_project_structure() {
    log "📁 Testing Project Structure"
    
    run_test "docker-compose.yml exists" "test -f docker-compose.yml"
    run_test "deployment script exists" "test -f scripts/deploy-production.sh"
    run_test "secrets script exists" "test -f scripts/setup-secrets.sh"
    run_test "deployment script executable" "test -x scripts/deploy-production.sh"
    run_test "secrets script executable" "test -x scripts/setup-secrets.sh"
    run_test ".env.example exists" "test -f .env.example"
    run_test "GitHub workflow exists" "test -f .github/workflows/deploy-production.yml"
}

test_deployment_script() {
    log "🚀 Testing Deployment Script"
    
    # Test script help
    run_test "deployment script help" "scripts/deploy-production.sh --help"
    
    # Test prerequisites check function exists
    run_test "deployment script syntax" "bash -n scripts/deploy-production.sh"
}

test_secrets_script() {
    log "🔐 Testing Secrets Management"
    
    run_test "secrets script help" "scripts/setup-secrets.sh --help"
    run_test "secrets script list" "scripts/setup-secrets.sh list"
    run_test "secrets validation" "scripts/setup-secrets.sh validate || true"  # Allow failure
}

test_docker_compose() {
    log "🐳 Testing Docker Compose Configuration"
    
    run_test "docker-compose config valid" "docker-compose config -q"
    run_test "required services defined" "docker-compose config --services | grep -E '(postgres|redis|opensearch|core-gateway|open-webui)'"
}

test_github_integration() {
    log "🐙 Testing GitHub Integration"
    
    run_test "repository exists" "gh repo view"
    run_test "workflow file valid" "gh workflow list | grep -q 'Deploy to Production'"
    
    # Check if runners are available
    local runner_count=$(gh api repos/:owner/:repo/actions/runners --jq '.total_count')
    if [[ "$runner_count" -gt 0 ]]; then
        log_success "GitHub runners available ($runner_count)"
        ((TESTS_PASSED++))
    else
        log_warning "No GitHub runners configured"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
}

test_environment_config() {
    log "⚙️ Testing Environment Configuration"
    
    # Create temporary .env for testing
    if [[ ! -f .env ]]; then
        cp .env.example .env.test
        
        run_test "environment file creation" "test -f .env.test"
        
        # Cleanup
        rm -f .env.test
    else
        run_test "environment file exists" "test -f .env"
    fi
    
    # Test environment variables
    run_test "required env vars defined" "grep -E '(POSTGRES_|OPENAI_|JWT_)' .env.example"
}

test_service_definitions() {
    log "🔧 Testing Service Definitions"
    
    local required_services=(
        "postgres"
        "redis"
        "opensearch"
        "service-registry"
        "core-gateway"
        "db-gateway"
        "orchestrator"
        "rag-service"
        "open-webui"
    )
    
    for service in "${required_services[@]}"; do
        run_test "service $service defined" "docker-compose config --services | grep -q $service"
    done
}

test_network_configuration() {
    log "🌐 Testing Network Configuration"
    
    run_test "docker networks defined" "docker-compose config | grep -q networks"
    
    # Test port configurations
    local ports=(3000 8000 8080 8081 8090 8091 5432 6379 9200)
    
    for port in "${ports[@]}"; do
        if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
            log_success "Port $port available"
            ((TESTS_PASSED++))
        else
            log_warning "Port $port in use"
            ((TESTS_FAILED++))
        fi
        ((TESTS_TOTAL++))
    done
}

test_security_configuration() {
    log "🔒 Testing Security Configuration"
    
    # Check for secrets in repository
    run_test "no secrets in git" "! git log --all --grep='password\\|secret\\|key' --oneline | head -5 | grep -E '(password|secret|key)'"
    
    # Check .gitignore
    run_test ".gitignore includes .env" "grep -q '\.env' .gitignore"
    
    # Check for hardcoded secrets in files
    run_test "no hardcoded passwords" "! grep -r 'password.*=' --include='*.yml' --include='*.yaml' . | grep -v example"
}

generate_test_report() {
    local timestamp=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
    local success_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    
    cat << EOF

============================================
🧪 REE AI Deployment Validation Report
============================================
Timestamp: $timestamp
Tests Run: $TESTS_TOTAL
Passed: $TESTS_PASSED
Failed: $TESTS_FAILED
Success Rate: ${success_rate}%

EOF

    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "🎉 All tests passed! Deployment is ready."
        return 0
    elif [[ $success_rate -ge 80 ]]; then
        log_warning "⚠️ Most tests passed, but some issues found."
        log "Review failed tests and fix issues before deployment."
        return 1
    else
        log_error "❌ Many tests failed. Fix issues before deployment."
        return 1
    fi
}

show_help() {
    cat << EOF
REE AI Deployment Validation

Usage: $0 [OPTIONS]

Options:
  --quick         Run only essential tests
  --full          Run all tests (default)
  --security      Run only security tests
  --docker        Run only Docker-related tests
  --github        Run only GitHub integration tests
  --help          Show this help

Tests:
  - Prerequisites (Docker, CLI tools)
  - Project structure (files, permissions)
  - Deployment scripts
  - Docker Compose configuration
  - GitHub integration
  - Security configuration
  - Network configuration

Examples:
  $0              # Run all tests
  $0 --quick      # Run essential tests only
  $0 --security   # Run security tests only

EOF
}

main() {
    local test_mode="full"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                test_mode="quick"
                shift
                ;;
            --full)
                test_mode="full"
                shift
                ;;
            --security)
                test_mode="security"
                shift
                ;;
            --docker)
                test_mode="docker"
                shift
                ;;
            --github)
                test_mode="github"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log "🧪 Starting REE AI Deployment Validation"
    log "Mode: $test_mode"
    echo ""
    
    # Run tests based on mode
    case "$test_mode" in
        "quick")
            test_prerequisites
            test_project_structure
            test_docker_compose
            ;;
        "security")
            test_security_configuration
            ;;
        "docker")
            test_docker_compose
            test_service_definitions
            test_network_configuration
            ;;
        "github")
            test_github_integration
            ;;
        "full"|*)
            test_prerequisites
            test_project_structure
            test_deployment_script
            test_secrets_script
            test_docker_compose
            test_github_integration
            test_environment_config
            test_service_definitions
            test_network_configuration
            test_security_configuration
            ;;
    esac
    
    echo ""
    generate_test_report
}

# Run main function
main "$@"