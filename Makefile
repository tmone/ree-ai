.PHONY: help setup test start-mock start-real stop clean

help:
	@echo "REE AI - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Setup environment (.env file)"
	@echo ""
	@echo "Development (Week 1 - with mocks):"
	@echo "  make start-mock     - Start infrastructure + mock services"
	@echo "  make test-mock      - Test with mock services"
	@echo ""
	@echo "Development (Week 2+ - real services):"
	@echo "  make start-real     - Start infrastructure + real services"
	@echo "  make test-real      - Test with real services"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-core      - Test Core Gateway only"
	@echo "  make test-db        - Test DB Gateway only"
	@echo "  make test-semantic  - Test Semantic Chunking only"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs           - View logs from all services"
	@echo "  make stop           - Stop all services"
	@echo "  make clean          - Clean all containers and volumes"

setup:
	@echo "📋 Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file"; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo "✅ .env file already exists"; \
	fi

start-mock:
	@echo "🚀 Starting infrastructure + mock services..."
	@docker-compose --profile mock up -d postgres redis opensearch ollama mock-core-gateway mock-db-gateway
	@echo ""
	@echo "✅ Mock services started!"
	@echo ""
	@echo "📍 Endpoints:"
	@echo "  Mock Core Gateway: http://localhost:8000"
	@echo "  Mock DB Gateway:   http://localhost:8001"
	@echo ""
	@echo "🔧 Now you can develop your Layer 3 services!"

start-real:
	@echo "🚀 Starting infrastructure + real services..."
	@docker-compose --profile real up -d
	@echo ""
	@echo "✅ Real services started!"
	@echo ""
	@echo "📍 Endpoints:"
	@echo "  Core Gateway:        http://localhost:8080"
	@echo "  DB Gateway:          http://localhost:8081"
	@echo "  Semantic Chunking:   http://localhost:8082"
	@echo ""
	@echo "📚 API Docs:"
	@echo "  Core Gateway:        http://localhost:8080/docs"
	@echo "  DB Gateway:          http://localhost:8081/docs"
	@echo "  Semantic Chunking:   http://localhost:8082/docs"

test-mock:
	@echo "🧪 Testing with mock services..."
	@export USE_REAL_CORE_GATEWAY=false && \
	export USE_REAL_DB_GATEWAY=false && \
	pytest tests/ -v

test-real:
	@echo "🧪 Testing with real services..."
	@export USE_REAL_CORE_GATEWAY=true && \
	export USE_REAL_DB_GATEWAY=true && \
	pytest tests/ -v

test:
	@echo "🧪 Running all tests..."
	@pytest tests/ -v

test-core:
	@echo "🧪 Testing Core Gateway..."
	@pytest tests/test_core_gateway.py -v

test-db:
	@echo "🧪 Testing DB Gateway..."
	@pytest tests/test_db_gateway.py -v

test-semantic:
	@echo "🧪 Testing Semantic Chunking..."
	@pytest tests/test_semantic_chunking.py -v

logs:
	@docker-compose logs -f

stop:
	@echo "🛑 Stopping all services..."
	@docker-compose --profile mock --profile real down
	@echo "✅ All services stopped"

clean:
	@echo "🧹 Cleaning all containers, volumes, and networks..."
	@docker-compose --profile mock --profile real down -v
	@echo "✅ Cleanup complete"
