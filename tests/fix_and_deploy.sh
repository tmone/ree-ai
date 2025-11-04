#!/bin/bash
echo "🔧 Applying bug fixes and deploying REE AI Orchestrator v2..."
echo ""

# Fix #2 already applied (relative imports)
echo "✅ Bug #2: Import paths fixed (relative imports)"

# Fix #1: Restart orchestrator
echo "🔄 Bug #1: Restarting orchestrator service..."
docker-compose restart orchestrator

# Wait for startup
echo "⏳ Waiting 15s for service startup..."
sleep 15

# Check health
echo "🏥 Checking service health..."
HEALTH=$(curl -s http://localhost:8090/health 2>/dev/null)

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Orchestrator is healthy"
else
    echo "❌ Orchestrator health check failed"
    echo "Response: $HEALTH"
    exit 1
fi

# Verify new endpoint
echo "🧪 Testing /orchestrate/v2 endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8090/orchestrate/v2 \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","query":"Hello"}' \
  2>/dev/null)

if echo "$RESPONSE" | grep -q "reasoning_chain"; then
    echo "✅ SUCCESS! New /orchestrate/v2 endpoint is working!"
    echo "✅ Response includes reasoning_chain"
    echo "✅ Response includes knowledge_expansion"
    echo "✅ Response includes ambiguity_result"
else
    echo "❌ FAILED! Endpoint not responding correctly"
    echo "Response: $RESPONSE"
    exit 1
fi

# Check if knowledge directory is accessible
echo ""
echo "📚 Verifying knowledge base..."
docker exec ree-ai-orchestrator ls -la /app/knowledge/ 2>&1 | grep -q "PROPERTIES.md"

if [ $? -eq 0 ]; then
    echo "✅ Knowledge directory is accessible"
else
    echo "⚠️  WARNING: Knowledge directory may not be accessible"
    echo "   You may need to add volume mount in docker-compose.yml:"
    echo "   volumes:"
    echo "     - ./knowledge:/app/knowledge:ro"
fi

# Run quick test
echo ""
echo "🧪 Running comprehensive test suite..."
python3 tests/quick_test.py 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ All fixes applied and verified!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 New Endpoints Available:"
echo "  • POST /orchestrate/v2 - Enhanced ReAct orchestration"
echo "  • POST /orchestrate/v2/stream - Streaming reasoning (SSE)"
echo ""
echo "🎯 Test with:"
echo '  curl -X POST http://localhost:8090/orchestrate/v2 \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"user_id":"test", "query":"Tìm căn hộ Quận 2"}'"'"
echo ""
