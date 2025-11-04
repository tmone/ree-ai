#!/bin/bash

# Deploy Enhanced RAG Service
# This script switches from basic RAG to enhanced RAG with all advanced features

set -e

echo "🚀 Deploying Enhanced RAG Service..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please review and update settings."
fi

# Confirm deployment
echo "This will deploy Enhanced RAG Service with:"
echo "  - Modular RAG operators (grading, reranking, query rewriting)"
echo "  - Agentic memory system (episodic, semantic, procedural)"
echo "  - Multi-agent coordination (supervisor + 4 specialists)"
echo "  - Self-reflection and quality control"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

# Stop existing RAG service
echo "🛑 Stopping existing RAG service..."
docker-compose stop rag-service || true

# Build RAG service (ensures latest code)
echo "🔨 Building RAG service..."
docker-compose build rag-service

# Deploy Enhanced RAG (now default in docker-compose.yml)
echo "🚀 Deploying Enhanced RAG service..."
docker-compose up -d rag-service

# Wait for service to be healthy
echo "⏳ Waiting for service to be healthy..."
sleep 5

# Health check
echo "🏥 Checking service health..."
if curl -f http://localhost:8091/health > /dev/null 2>&1; then
    echo "✅ Enhanced RAG service is healthy!"
else
    echo "❌ Health check failed. Checking logs..."
    docker-compose logs --tail=50 rag-service
    exit 1
fi

# Stats check
echo "📊 Checking advanced features..."
if curl -f http://localhost:8091/stats > /dev/null 2>&1; then
    echo "✅ Advanced features are available!"
    echo ""
    echo "📊 Service Stats:"
    curl -s http://localhost:8091/stats | python3 -m json.tool || echo "(Stats endpoint returned non-JSON)"
else
    echo "⚠️  Stats endpoint not available (may be OK if advanced features disabled)"
fi

echo ""
echo "✅ Enhanced RAG Service deployed successfully!"
echo ""
echo "📚 Next Steps:"
echo "  1. Test basic query:"
echo "     curl -X POST http://localhost:8091/query -H 'Content-Type: application/json' -d '{\"query\": \"Tìm căn hộ 2PN Quận 2\", \"limit\": 5}'"
echo ""
echo "  2. Test advanced query with memory:"
echo "     curl -X POST http://localhost:8091/query -H 'Content-Type: application/json' -d '{\"query\": \"Tìm căn hộ gần trường quốc tế\", \"user_id\": \"user123\", \"use_advanced_rag\": true, \"limit\": 5}'"
echo ""
echo "  3. Monitor logs:"
echo "     docker-compose logs -f rag-service"
echo ""
echo "  4. View stats:"
echo "     curl http://localhost:8091/stats | python3 -m json.tool"
echo ""
echo "  5. Rollback to basic RAG (if needed):"
echo "     ./scripts/rollback-basic-rag.sh"
echo ""
