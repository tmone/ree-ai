# REE AI - Makefile for Development and Testing

.PHONY: help install test test-ai test-failover test-critical test-quick test-all test-coverage clean

# Default target
help:
	@echo "REE AI - Available Commands:"
	@echo ""
	@echo "  Setup:"
	@echo "    make install          - Install all dependencies including test dependencies"
	@echo "    make install-test     - Install only test dependencies"
	@echo ""
	@echo "  Testing:"
	@echo "    make test             - Run all tests"
	@echo "    make test-quick       - Run quick tests only (no slow tests)"
	@echo "    make test-critical    - Run critical tests only"
	@echo "    make test-ai          - Run AI quality tests"
	@echo "    make test-failover    - Run failover tests"
	@echo "    make test-cto         - Run CTO business logic tests"
	@echo "    make test-integration - Run integration tests"
	@echo "    make test-coverage    - Run tests with coverage report"
	@echo ""
	@echo "  Development:"
	@echo "    make build            - Build Docker images"
	@echo "    make up               - Start all services"
	@echo "    make down             - Stop all services"
	@echo "    make logs             - View service logs"
	@echo "    make clean            - Clean test artifacts and cache"
	@echo ""
	@echo "  Reports:"
	@echo "    make report           - Generate and open test report"
	@echo "    make coverage-report  - Generate and open coverage report"

# Installation
install:
	pip install -r requirements.txt
	pip install -r tests/requirements-test.txt

install-test:
	pip install -r tests/requirements-test.txt

# Testing
test:
	python3 -m pytest tests/ -v

test-quick:
	python3 -m pytest tests/ -v -m "not slow"

test-critical:
	python3 -m pytest tests/ -v -m critical

test-ai:
	python3 -m pytest tests/test_ai_quality.py -v

test-failover:
	python3 -m pytest tests/test_failover_mechanism.py -v

test-cto:
	python3 -m pytest tests/test_cto_business_logic.py -v

test-integration:
	@echo "Running integration tests..."
	@./tests/test_comprehensive.sh

test-coverage:
	python3 -m pytest tests/ --cov=services --cov=shared \
		--cov-report=html:tests/coverage \
		--cov-report=term-missing

test-all: test-quick test-integration

# Docker operations
build:
	docker build -t ree-ai-service-registry -f services/service_registry/Dockerfile .
	docker build -t ree-ai-core-gateway -f services/core_gateway/Dockerfile .
	docker build -t ree-ai-orchestrator -f services/orchestrator/Dockerfile .

up:
	docker-compose -f docker-compose.test.yml up -d

down:
	docker-compose -f docker-compose.test.yml down

logs:
	docker-compose -f docker-compose.test.yml logs -f

# Reports
report:
	pytest tests/ --html=tests/reports/report.html --self-contained-html
	@echo "Opening test report..."
	@open tests/reports/report.html || xdg-open tests/reports/report.html

coverage-report: test-coverage
	@echo "Opening coverage report..."
	@open tests/coverage/index.html || xdg-open tests/coverage/index.html

# Cleanup
clean:
	rm -rf tests/reports/*.html
	rm -rf tests/coverage/
	rm -rf tests/.pytest_cache/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned test artifacts"

# Development helpers
check-services:
	@echo "Checking service health..."
	@curl -sf http://localhost:8000/health && echo "✅ Service Registry: healthy" || echo "❌ Service Registry: down"
	@curl -sf http://localhost:8080/health && echo "✅ Core Gateway: healthy" || echo "❌ Core Gateway: down"
	@curl -sf http://localhost:8090/health && echo "✅ Orchestrator: healthy" || echo "❌ Orchestrator: down"

restart-services:
	docker-compose -f docker-compose.test.yml restart core-gateway orchestrator

# CI/CD simulation
ci:
	@echo "🚀 Running CI/CD pipeline..."
	@echo "Step 1: Critical tests"
	pytest tests/ -m critical -v --tb=short
	@echo "Step 2: AI quality tests"
	pytest tests/test_ai_quality.py -v --tb=short
	@echo "Step 3: Failover tests"
	pytest tests/test_failover_mechanism.py -v --tb=short
	@echo "Step 4: Integration tests"
	./tests/test_comprehensive.sh
	@echo "✅ CI/CD pipeline completed"

# Quick smoke test
smoke:
	@echo "🔥 Running smoke tests..."
	pytest tests/ -m smoke -v
	@./tests/test_comprehensive.sh

# Watch mode (requires pytest-watch)
watch:
	ptw tests/ -- -v

# Format and lint
format:
	black tests/ services/ shared/
	@echo "✅ Code formatted"


lint:
	python3 -m flake8 tests/ services/ shared/ --max-line-length=100
	python3 -m mypy tests/ services/ shared/ --ignore-missing-imports
	@echo "✅ Linting completed"
