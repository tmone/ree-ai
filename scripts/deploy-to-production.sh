#!/bin/bash
################################################################################
# REE AI - Production Deployment Script
# Target: 103.153.74.213
################################################################################

set -e  # Exit on error

# Configuration
PROD_SERVER="103.153.74.213"
SSH_KEY="tmone"
SSH_USER="${SSH_USER:-root}"  # Default to root, can override with environment variable
PROJECT_PATH="${PROJECT_PATH:-/opt/ree-ai}"  # Default path, can override
GIT_BRANCH="${GIT_BRANCH:-main}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    log_error "SSH key file not found: $SSH_KEY"
    log_info "Please provide the correct path to your SSH key file"
    exit 1
fi

echo ""
echo "=============================================================================="
echo "                    REE AI - PRODUCTION DEPLOYMENT"
echo "=============================================================================="
echo ""
echo "Target Server: $PROD_SERVER"
echo "SSH Key: $SSH_KEY"
echo "SSH User: $SSH_USER"
echo "Project Path: $PROJECT_PATH"
echo "Git Branch: $GIT_BRANCH"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Step 1: Test SSH connection
log_info "Testing SSH connection..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "${SSH_USER}@${PROD_SERVER}" "echo 'Connection successful'" &>/dev/null; then
    log_success "SSH connection successful"
else
    log_error "Cannot connect to server. Please check:"
    echo "  1. SSH key file is correct"
    echo "  2. SSH key has correct permissions (chmod 600 $SSH_KEY)"
    echo "  3. Server is accessible"
    echo "  4. Username is correct"
    exit 1
fi

# Step 2: Check if Docker is installed
log_info "Checking Docker installation..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" << 'EOF'
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully"
else
    echo "Docker is already installed"
    docker --version
fi
EOF
log_success "Docker check complete"

# Step 3: Check if Docker Compose is installed
log_info "Checking Docker Compose installation..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" << 'EOF'
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing..."
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose is already installed"
    docker-compose --version
fi
EOF
log_success "Docker Compose check complete"

# Step 4: Clone or update repository
log_info "Setting up project repository..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << EOF
if [ -d "$PROJECT_PATH" ]; then
    echo "Project directory exists. Pulling latest changes..."
    cd $PROJECT_PATH
    git fetch origin
    git checkout $GIT_BRANCH
    git pull origin $GIT_BRANCH
    git log -1 --oneline
else
    echo "Cloning repository..."
    mkdir -p $(dirname $PROJECT_PATH)
    git clone https://github.com/tmone/ree-ai.git $PROJECT_PATH
    cd $PROJECT_PATH
    git checkout $GIT_BRANCH
fi
EOF
log_success "Repository setup complete"

# Step 5: Setup environment file
log_info "Setting up environment variables..."
log_warning "You need to configure .env file on the server"
echo ""
echo "Required environment variables:"
echo "  - OPENAI_API_KEY (required)"
echo "  - POSTGRES_PASSWORD (recommended to change)"
echo "  - WEBUI_SECRET_KEY (required for production)"
echo "  - JWT_SECRET_KEY (required for production)"
echo ""
read -p "Do you want to copy .env from local machine? (y/n): " copy_env

if [ "$copy_env" = "y" ] || [ "$copy_env" = "Y" ]; then
    if [ -f ".env" ]; then
        log_info "Copying .env file to server..."
        scp -i "$SSH_KEY" .env "${SSH_USER}@${PROD_SERVER}:${PROJECT_PATH}/.env"
        log_success ".env file copied"
    else
        log_warning ".env file not found locally"
        log_info "Creating .env from template on server..."
        ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << EOF
cd $PROJECT_PATH
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file on server before starting services"
    echo "   SSH to server: ssh -i $SSH_KEY ${SSH_USER}@${PROD_SERVER}"
    echo "   Edit file: nano $PROJECT_PATH/.env"
fi
EOF
    fi
else
    log_info "Skipping .env copy. Make sure to configure it on the server."
fi

# Step 6: Setup credentials (if needed)
log_info "Checking credentials directory..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << EOF
cd $PROJECT_PATH
mkdir -p credentials
if [ ! -f credentials/gcs-service-account.json ]; then
    echo "⚠️  Warning: GCS service account credentials not found"
    echo "   If you need GCS integration, copy the file manually:"
    echo "   scp -i $SSH_KEY /path/to/gcs-service-account.json ${SSH_USER}@${PROD_SERVER}:${PROJECT_PATH}/credentials/"
fi
EOF

# Step 7: Pull Docker images and build
log_info "Building Docker images (this may take several minutes)..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << EOF
cd $PROJECT_PATH
docker-compose --profile all build --parallel
EOF
log_success "Docker images built successfully"

# Step 8: Start services
log_info "Starting services..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << EOF
cd $PROJECT_PATH

# Stop existing services
docker-compose --profile all down

# Start infrastructure first
echo "Starting infrastructure services..."
docker-compose up -d postgres redis opensearch

# Wait for infrastructure
echo "Waiting for infrastructure to be ready..."
sleep 30

# Start service registry
echo "Starting service registry..."
docker-compose up -d service-registry
sleep 10

# Start core services
echo "Starting core services..."
docker-compose up -d core-gateway db-gateway auth-service

# Wait for core services
sleep 15

# Start AI services
echo "Starting AI services..."
docker-compose up -d classification completeness attribute-extraction validation semantic-chunking

# Wait for AI services
sleep 10

# Start orchestrator and RAG
echo "Starting orchestrator and RAG service..."
docker-compose up -d orchestrator rag-service

# Wait for orchestrator
sleep 15

# Start frontend
echo "Starting Open WebUI frontend..."
docker-compose up -d open-webui

echo "All services started!"
EOF
log_success "Services started"

# Step 9: Wait for services to be ready
log_info "Waiting for services to initialize (60 seconds)..."
sleep 60

# Step 10: Health checks
echo ""
log_info "Running health checks..."
echo ""

check_health() {
    local service=$1
    local port=$2
    local endpoint=${3:-/health}
    
    echo -n "  Checking $service ($port)... "
    if ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" "curl -sf http://localhost:$port$endpoint" &>/dev/null; then
        log_success "OK"
        return 0
    else
        log_error "FAILED"
        return 1
    fi
}

# Check core services
check_health "PostgreSQL" "5432" "" || true
check_health "Redis" "6379" "" || true
check_health "OpenSearch" "9200" "" || true
check_health "Service Registry" "8000" "/health" || true
check_health "Core Gateway" "8080" "/health" || true
check_health "DB Gateway" "8081" "/health" || true
check_health "Orchestrator" "8090" "/health" || true
check_health "RAG Service" "8091" "/health" || true
check_health "Open WebUI" "3000" "/health" || true

# Step 11: Display service status
echo ""
log_info "Checking service status..."
ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << EOF
cd $PROJECT_PATH
docker-compose ps
EOF

# Step 12: Setup firewall (optional)
echo ""
read -p "Do you want to configure firewall rules? (y/n): " setup_firewall

if [ "$setup_firewall" = "y" ] || [ "$setup_firewall" = "Y" ]; then
    log_info "Configuring firewall..."
    ssh -i "$SSH_KEY" "${SSH_USER}@${PROD_SERVER}" bash << 'EOF'
if command -v ufw &> /dev/null; then
    # Allow SSH
    ufw allow 22/tcp
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow Open WebUI
    ufw allow 3000/tcp
    
    # Enable firewall (if not already enabled)
    ufw --force enable
    
    echo "Firewall configured"
    ufw status
else
    echo "UFW not installed. Skipping firewall configuration."
fi
EOF
    log_success "Firewall configured"
fi

# Step 13: Final summary
echo ""
echo "=============================================================================="
echo "                    DEPLOYMENT COMPLETED SUCCESSFULLY"
echo "=============================================================================="
echo ""
log_success "REE AI has been deployed to $PROD_SERVER"
echo ""
echo "Access URLs:"
echo "  - Open WebUI:       http://$PROD_SERVER:3000"
echo "  - API Gateway:      http://$PROD_SERVER:8888"
echo "  - Orchestrator:     http://$PROD_SERVER:8090"
echo "  - Service Registry: http://$PROD_SERVER:8000"
echo ""
echo "Useful commands:"
echo "  View logs:    ssh -i $SSH_KEY ${SSH_USER}@${PROD_SERVER} 'cd $PROJECT_PATH && docker-compose logs -f'"
echo "  Restart:      ssh -i $SSH_KEY ${SSH_USER}@${PROD_SERVER} 'cd $PROJECT_PATH && docker-compose restart'"
echo "  Stop all:     ssh -i $SSH_KEY ${SSH_USER}@${PROD_SERVER} 'cd $PROJECT_PATH && docker-compose down'"
echo "  Check status: ssh -i $SSH_KEY ${SSH_USER}@${PROD_SERVER} 'cd $PROJECT_PATH && docker-compose ps'"
echo ""
log_warning "IMPORTANT: Make sure to:"
echo "  1. Configure .env file with production secrets"
echo "  2. Setup SSL/HTTPS for production use"
echo "  3. Configure backup strategy for PostgreSQL"
echo "  4. Monitor service logs regularly"
echo ""
echo "=============================================================================="
