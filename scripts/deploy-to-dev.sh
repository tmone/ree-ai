#!/bin/bash
################################################################################
# Quick Deployment Script - Anti-Hallucination Fix to Dev Server
################################################################################

set -e  # Exit on error

# Configuration
DEV_SERVER="103.153.74.213"
DEV_USER="user"  # Update with actual username
PROJECT_PATH="/path/to/ree-ai"  # Update with actual path
TARGET_COMMIT="4af6011"

echo "=============================================================================="
echo "DEPLOYING ANTI-HALLUCINATION FIX TO DEV SERVER"
echo "=============================================================================="
echo ""
echo "Target: $DEV_SERVER"
echo "Commit: $TARGET_COMMIT"
echo ""

# Step 1: SSH and pull
echo "[1/5] Pulling latest changes..."
ssh ${DEV_USER}@${DEV_SERVER} << 'EOF'
cd ${PROJECT_PATH}
git pull origin main
git log -1 --oneline
EOF

# Step 2: Rebuild RAG service
echo ""
echo "[2/5] Rebuilding RAG service..."
ssh ${DEV_USER}@${DEV_SERVER} << 'EOF'
cd ${PROJECT_PATH}
docker-compose build rag_service
EOF

# Step 3: Restart service
echo ""
echo "[3/5] Restarting RAG service..."
ssh ${DEV_USER}@${DEV_SERVER} << 'EOF'
cd ${PROJECT_PATH}
docker-compose restart rag_service
EOF

# Step 4: Wait for service to be ready
echo ""
echo "[4/5] Waiting for service to be ready (30 seconds)..."
sleep 30

# Step 5: Health check
echo ""
echo "[5/5] Running health check..."
HEALTH_STATUS=$(curl -s http://${DEV_SERVER}:8090/health)
echo "Health Status: $HEALTH_STATUS"

# Verification tests
echo ""
echo "=============================================================================="
echo "RUNNING VERIFICATION TESTS"
echo "=============================================================================="
echo ""

# Test 1: Health check
echo "[TEST 1] Health Check"
curl -s http://${DEV_SERVER}:8090/health
echo ""

# Test 2: Original issue query
echo ""
echo "[TEST 2] Original Issue Query - Should return only 1 real property"
curl -s -X POST http://${DEV_SERVER}:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm nhà dưới 50 tỷ ở TP.HCM",
    "user_id": "deployment_test"
  }' | jq '.response' | head -20
echo ""

# Test 3: Zero results test
echo ""
echo "[TEST 3] Impossible Search - Should say 'không tìm thấy'"
curl -s -X POST http://${DEV_SERVER}:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm lâu đài 50 phòng ngủ giá 100 đồng",
    "user_id": "deployment_test"
  }' | jq '.response'
echo ""

# Test 4: POST flow test
echo ""
echo "[TEST 4] POST Flow - Should ask questions, not suggest properties"
curl -s -X POST http://${DEV_SERVER}:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tôi muốn bán nhà ở Quận 7",
    "user_id": "deployment_test"
  }' | jq '.response'
echo ""

echo "=============================================================================="
echo "DEPLOYMENT COMPLETE"
echo "=============================================================================="
echo ""
echo "Next steps:"
echo "1. Review test results above"
echo "2. Check for fake patterns (District 1/7, 45B/38B/42B/30B)"
echo "3. Monitor logs: ssh ${DEV_USER}@${DEV_SERVER} 'cd ${PROJECT_PATH} && docker-compose logs -f rag_service'"
echo "4. Test with real user queries"
echo ""
echo "Expected results:"
echo "  ✓ Test 1: Health check passes"
echo "  ✓ Test 2: Returns ONLY 1 real property (2BR Binh Thanh, 4.5B)"
echo "  ✓ Test 3: Says 'không tìm thấy' with NO fake data"
echo "  ✓ Test 4: Asks questions, NO property listings"
echo ""
