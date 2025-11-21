#!/bin/bash

# UI-to-DB Test Runner Script
# Automates the process of running end-to-end UI tests with proper setup and teardown

set -e  # Exit on error

echo "================================================================================================"
echo "🚀 UI-TO-DB AUTOMATED TESTING RUNNER"
echo "================================================================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HEADLESS=${HEADLESS:-false}
SLOW_MO=${SLOW_MO:-300}
CLEANUP=${CLEANUP:-true}

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if service is healthy
check_service() {
    local service_name=$1
    local service_url=$2
    local max_attempts=30
    local attempt=1

    print_info "Checking $service_name..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$service_url" > /dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi

        echo -n "."
        sleep 1
        ((attempt++))
    done

    print_error "$service_name is not responding after $max_attempts attempts"
    return 1
}

# Step 1: Check prerequisites
echo ""
echo "📋 Step 1: Checking prerequisites..."
echo "------------------------------------------------------------------------------------------------"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    print_error "Python is not installed. Please install Python 3.8+ and try again."
    exit 1
fi
print_success "Python is installed"

# Check Python version
python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_info "Python version: $python_version"

# Step 2: Check and install dependencies
echo ""
echo "📦 Step 2: Checking Python dependencies..."
echo "------------------------------------------------------------------------------------------------"

required_packages=("playwright" "opensearch-py" "psycopg2-binary" "httpx")
missing_packages=()

for package in "${required_packages[@]}"; do
    if ! python -c "import ${package//-/_}" 2>/dev/null; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    print_warning "Missing packages: ${missing_packages[*]}"
    print_info "Installing missing packages..."
    pip install "${missing_packages[@]}"
    print_success "Packages installed"
else
    print_success "All required packages are installed"
fi

# Check if Playwright browsers are installed
if ! playwright --version > /dev/null 2>&1; then
    print_info "Installing Playwright..."
    pip install playwright
fi

print_info "Installing Playwright browsers (chromium)..."
playwright install chromium > /dev/null 2>&1 || true
print_success "Playwright browsers ready"

# Step 3: Check if services are running
echo ""
echo "🔍 Step 3: Checking if services are running..."
echo "------------------------------------------------------------------------------------------------"

services_running=true

if ! check_service "Service Registry" "http://localhost:8000/health"; then
    services_running=false
fi

if ! check_service "Orchestrator" "http://localhost:8090/health"; then
    services_running=false
fi

if ! check_service "DB Gateway" "http://localhost:8081/health"; then
    services_running=false
fi

if ! check_service "Open WebUI" "http://localhost:3000"; then
    services_running=false
fi

if ! check_service "OpenSearch" "http://localhost:9200/_cluster/health"; then
    services_running=false
fi

if [ "$services_running" = false ]; then
    print_warning "Some services are not running"
    print_info "Starting services with docker-compose..."

    # Start services
    docker-compose up -d

    # Wait for services to be healthy
    print_info "Waiting for services to be ready (this may take 30-60 seconds)..."
    sleep 10

    # Check again
    check_service "Service Registry" "http://localhost:8000/health" || exit 1
    check_service "Orchestrator" "http://localhost:8090/health" || exit 1
    check_service "DB Gateway" "http://localhost:8081/health" || exit 1
    check_service "Open WebUI" "http://localhost:3000" || exit 1
    check_service "OpenSearch" "http://localhost:9200/_cluster/health" || exit 1
fi

print_success "All services are running and healthy"

# Step 4: Run UI-to-DB tests
echo ""
echo "🧪 Step 4: Running UI-to-DB tests..."
echo "------------------------------------------------------------------------------------------------"

# Set environment variables
export HEADLESS=$HEADLESS
export SLOW_MO=$SLOW_MO

# Run tests
print_info "Starting test execution..."
print_info "Configuration: HEADLESS=$HEADLESS, SLOW_MO=$SLOW_MO"
echo ""

if python tests/test_ui_to_db_ai_automated.py; then
    print_success "Tests completed successfully!"
    test_exit_code=0
else
    print_error "Tests failed!"
    test_exit_code=1
fi

# Step 5: Show test results
echo ""
echo "📊 Step 5: Test results"
echo "------------------------------------------------------------------------------------------------"

# Find latest test report
latest_report=$(ls -t tests/ui_to_db_report_*.json 2>/dev/null | head -1)

if [ -n "$latest_report" ]; then
    print_success "Test report generated: $latest_report"

    # Parse and display summary (requires jq)
    if command -v jq &> /dev/null; then
        echo ""
        print_info "Test Summary:"
        jq -r '.summary | to_entries | .[] | "  \(.key): \(.value)"' "$latest_report"
    else
        print_warning "Install 'jq' to see formatted test summary"
        print_info "View full report: cat $latest_report | python -m json.tool"
    fi
else
    print_warning "No test report found"
fi

# Show screenshots
screenshots=$(ls tests/*.png 2>/dev/null)
if [ -n "$screenshots" ]; then
    echo ""
    print_info "Screenshots saved:"
    echo "$screenshots" | while read -r screenshot; do
        echo "  - $screenshot"
    done
fi

# Step 6: Cleanup (optional)
if [ "$CLEANUP" = true ]; then
    echo ""
    echo "🧹 Step 6: Cleanup"
    echo "------------------------------------------------------------------------------------------------"

    print_info "Cleaning up test data..."
    # Test properties are automatically cleaned up by the test script
    print_success "Cleanup completed"
fi

# Final summary
echo ""
echo "================================================================================================"
if [ $test_exit_code -eq 0 ]; then
    print_success "UI-TO-DB TESTING COMPLETED SUCCESSFULLY!"
else
    print_error "UI-TO-DB TESTING FAILED!"
fi
echo "================================================================================================"
echo ""

# Show next steps
print_info "Next steps:"
echo "  - View detailed report: cat $latest_report | python -m json.tool"
echo "  - View screenshots: ls tests/*.png"
echo "  - Check logs: docker-compose logs orchestrator | tail -100"
echo ""

exit $test_exit_code
