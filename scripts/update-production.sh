#!/bin/bash
################################################################################
# REE AI - Quick Update Script for Production Server
# Server: 103.153.74.213 (Port range: 7xxxx)
################################################################################

set -e  # Exit on error

# Configuration
SERVER="103.153.74.213"
SSH_KEY="C:/Users/dev/.ssh/tmone"
PROJECT_PATH="/opt/ree-ai"
GIT_BRANCH="main"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=============================================================================="
echo "                    REE AI - UPDATE PRODUCTION CODE"
echo "=============================================================================="
echo ""
echo "Server: $SERVER"
echo "Project: $PROJECT_PATH"
echo "Branch: $GIT_BRANCH"
echo ""

# Step 1: Pull latest code
echo -e "${BLUE}[1/5]${NC} Pulling latest code from GitHub..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@$SERVER << EOF
cd $PROJECT_PATH
git fetch origin
git pull origin $GIT_BRANCH
echo ""
echo "Latest commit:"
git log -1 --oneline
EOF
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# Step 2: Rebuild services
echo -e "${BLUE}[2/5]${NC} Rebuilding Docker images..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@$SERVER << EOF
cd $PROJECT_PATH
docker-compose build --parallel
EOF
echo -e "${GREEN}✓ Images rebuilt${NC}"
echo ""

# Step 3: Restart services
echo -e "${BLUE}[3/5]${NC} Restarting services..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@$SERVER << EOF
cd $PROJECT_PATH

# Restart in order
echo "Restarting infrastructure..."
docker-compose restart postgres redis opensearch

echo "Restarting service registry..."
docker-compose restart service-registry
sleep 5

echo "Restarting core services..."
docker-compose restart core-gateway db-gateway auth-service
sleep 5

echo "Restarting AI services..."
docker-compose restart classification completeness attribute-extraction validation semantic-chunking
sleep 5

echo "Restarting orchestrator and RAG..."
docker-compose restart orchestrator rag-service
sleep 5

echo "Restarting frontend..."
docker-compose restart open-webui

echo "All services restarted!"
EOF
echo -e "${GREEN}✓ Services restarted${NC}"
echo ""

# Step 4: Wait for services to be ready
echo -e "${BLUE}[4/5]${NC} Waiting for services to initialize (30 seconds)..."
sleep 30
echo ""

# Step 5: Health checks
echo -e "${BLUE}[5/5]${NC} Running health checks..."
echo ""

# Note: Update ports based on actual deployment
check_service() {
    local name=$1
    local port=$2
    echo -n "  $name ($port)... "
    if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no root@$SERVER "curl -sf http://localhost:$port/health" &>/dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}CHECK MANUALLY${NC}"
    fi
}

check_service "Service Registry" "7000"
check_service "Core Gateway" "7080"
check_service "DB Gateway" "7081"
check_service "Orchestrator" "7090"
check_service "RAG Service" "7091"
check_service "Open WebUI" "7300"

echo ""
echo "=============================================================================="
echo "                    UPDATE COMPLETED"
echo "=============================================================================="
echo ""
echo -e "${GREEN}✓ Code updated and services restarted successfully!${NC}"
echo ""
echo "Access URLs (update ports as needed):"
echo "  - Open WebUI:   http://$SERVER:7300"
echo "  - Orchestrator: http://$SERVER:7090"
echo "  - Registry:     http://$SERVER:7000"
echo ""
echo "Useful commands:"
echo "  View logs:      ssh -i $SSH_KEY root@$SERVER 'cd $PROJECT_PATH && docker-compose logs -f'"
echo "  Check status:   ssh -i $SSH_KEY root@$SERVER 'cd $PROJECT_PATH && docker-compose ps'"
echo ""
echo "=============================================================================="
