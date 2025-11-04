#!/bin/bash

# Rollback to Basic RAG Service
# This script reverts from enhanced RAG back to basic RAG

set -e

echo "🔄 Rolling back to Basic RAG Service..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Confirm rollback
echo "This will rollback to Basic RAG Service:"
echo "  - Simple 3-step pipeline (retrieve → augment → generate)"
echo "  - No memory, no agents, no advanced operators"
echo "  - Faster, simpler, but less intelligent"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Rollback cancelled."
    exit 1
fi

# Stop current RAG service
echo "🛑 Stopping current RAG service..."
docker-compose stop rag-service

# Edit docker-compose.yml to use basic RAG
echo "📝 Switching to basic RAG (main.py)..."
sed -i.bak 's/services.rag_service.enhanced_main:app/services.rag_service.main:app/' docker-compose.yml

# Rebuild and start basic RAG service
echo "🚀 Starting Basic RAG service..."
docker-compose build rag-service
docker-compose up -d rag-service

# Wait for service to be healthy
echo "⏳ Waiting for service to be healthy..."
sleep 5

# Health check
echo "🏥 Checking service health..."
if curl -f http://localhost:8091/health > /dev/null 2>&1; then
    echo "✅ Basic RAG service is healthy!"
else
    echo "❌ Health check failed. Checking logs..."
    docker-compose logs --tail=50 rag-service
    exit 1
fi

echo ""
echo "✅ Rollback to Basic RAG completed successfully!"
echo ""
echo "📚 Next Steps:"
echo "  1. Test basic query:"
echo "     curl -X POST http://localhost:8091/query -H 'Content-Type: application/json' -d '{\"query\": \"Tìm căn hộ 2PN Quận 2\", \"limit\": 5}'"
echo ""
echo "  2. Monitor logs:"
echo "     docker-compose logs -f rag-service"
echo ""
echo "  3. Re-deploy enhanced RAG (if needed):"
echo "     ./scripts/deploy-enhanced-rag.sh"
echo ""
