#!/bin/bash

# Production Server Setup Script for REE AI
# Run this script on the production server (192.168.1.11)

set -e

echo "🏗️ REE AI Production Server Setup"
echo "================================="
echo ""
echo "This script will:"
echo "1. Install required dependencies (Docker, Git)"
echo "2. Setup user and directories"  
echo "3. Configure firewall for REE AI services"
echo "4. Create systemd service for auto-start"
echo ""

# Check if running as tmone user
if [ "$USER" != "tmone" ]; then
    echo "❌ This script should be run as user 'tmone'"
    echo "   Switch user: su - tmone"
    exit 1
fi

echo "🔍 System Information:"
echo "User: $USER"
echo "Home: $HOME"
echo "OS: $(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown Linux')"
echo "Architecture: $(uname -m)"
echo ""

# Confirm before proceeding
read -p "Continue with setup? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    htop \
    ufw \
    fail2ban

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Set up Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose (standalone)
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow REE AI service ports
echo "🌐 Opening REE AI service ports..."
declare -A SERVICES=(
    ["3000"]="Open WebUI (Frontend)"
    ["8000"]="Service Registry"
    ["8080"]="Core Gateway (API)"
    ["8081"]="DB Gateway"
    ["8090"]="Orchestrator"
    ["8091"]="RAG Service"
    ["3002"]="Admin Dashboard"
    ["9200"]="OpenSearch"
    ["5432"]="PostgreSQL"
    ["6379"]="Redis"
)

for port in "${!SERVICES[@]}"; do
    echo "  Opening port $port - ${SERVICES[$port]}"
    sudo ufw allow $port/tcp
done

# Enable firewall
sudo ufw --force enable

# Setup project directory
echo "📁 Setting up project directory..."
PROJECT_DIR="$HOME/ree-ai"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Clone or initialize repository
if [ ! -d ".git" ]; then
    echo "📥 Cloning REE AI repository..."
    git clone https://github.com/tmone/ree-ai.git .
else
    echo "✅ Repository already exists"
fi

# Create basic environment file
echo "⚙️ Creating environment file..."
cat > .env << 'EOF'
# REE AI Production Environment Configuration
# ===========================================

# Database Configuration
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=ree_ai_pass_2025
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# OpenAI Configuration (REQUIRED - Add your key)
OPENAI_API_KEY=your-openai-api-key-here

# Ollama Configuration (Optional)
OLLAMA_BASE_URL=
PRODUCTION_MODE=true

# OpenSearch Configuration  
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200
OPENSEARCH_PASSWORD=Admin123!@#

# WebUI Configuration
WEBUI_SECRET_KEY=production-secret-key-change-me
TASK_MODEL=llama3.2:latest

# JWT Configuration
JWT_SECRET_KEY=production-jwt-secret-key-change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Feature Flags
USE_REAL_CORE_GATEWAY=true
USE_REAL_DB_GATEWAY=true
USE_ADVANCED_RAG=true

# Debug Settings
DEBUG=false
LOG_LEVEL=INFO

# Auto-generation Features
ENABLE_FOLLOW_UP_GENERATION=true
ENABLE_TITLE_GENERATION=true
ENABLE_TAGS_GENERATION=true
ENABLE_AUTOCOMPLETE_GENERATION=false

# Performance Settings
MEMORY_RETENTION_DAYS=90
MEMORY_CONSOLIDATION_THRESHOLD=10
REFLECTION_QUALITY_THRESHOLD=0.7
DOCUMENT_GRADER_THRESHOLD=0.5
AGENT_TIMEOUT_SECONDS=30
SUPERVISOR_MAX_RETRIES=2
EOF

# Create systemd service for auto-start
echo "🚀 Creating systemd service..."
sudo tee /etc/systemd/system/ree-ai.service > /dev/null << EOF
[Unit]
Description=REE AI Real Estate Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose --profile real up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=tmone

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable ree-ai.service

# Create management scripts
echo "📋 Creating management scripts..."

# Start script
cat > start-ree-ai.sh << 'EOF'
#!/bin/bash
cd ~/ree-ai
echo "🚀 Starting REE AI services..."
docker-compose --profile real up -d
echo "✅ REE AI started! Access at http://localhost:3000"
EOF

# Stop script  
cat > stop-ree-ai.sh << 'EOF'
#!/bin/bash
cd ~/ree-ai
echo "🛑 Stopping REE AI services..."
docker-compose down
echo "✅ REE AI stopped!"
EOF

# Status script
cat > status-ree-ai.sh << 'EOF'
#!/bin/bash
cd ~/ree-ai
echo "📊 REE AI Service Status:"
echo "========================"
docker-compose ps
echo ""
echo "🏥 Health Checks:"
curl -f http://localhost:3000 >/dev/null 2>&1 && echo "✅ Frontend (Open WebUI)" || echo "❌ Frontend (Open WebUI)"
curl -f http://localhost:8080/health >/dev/null 2>&1 && echo "✅ Core Gateway" || echo "❌ Core Gateway" 
curl -f http://localhost:8090/health >/dev/null 2>&1 && echo "✅ Orchestrator" || echo "❌ Orchestrator"
curl -f http://localhost:8091/health >/dev/null 2>&1 && echo "✅ RAG Service" || echo "❌ RAG Service"
EOF

# Logs script
cat > logs-ree-ai.sh << 'EOF'
#!/bin/bash
cd ~/ree-ai
if [ "$1" ]; then
    echo "📜 Showing logs for $1..."
    docker-compose logs -f "$1"
else
    echo "📜 Showing all logs..."
    docker-compose logs -f
fi
EOF

# Make scripts executable
chmod +x *.sh

# Create backup script
cat > backup-data.sh << 'EOF'
#!/bin/bash
cd ~/ree-ai
BACKUP_DIR="$HOME/ree-ai-backups/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Creating backup..."
echo "Backup directory: $BACKUP_DIR"

# Backup PostgreSQL
echo "📊 Backing up PostgreSQL..."
docker exec ree-ai-postgres pg_dumpall -U ree_ai_user > "$BACKUP_DIR/postgres-backup.sql"

# Backup OpenSearch data (if possible)
echo "🔍 Backing up configuration..."
cp .env "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x backup-data.sh

# Setup log rotation
echo "📜 Setting up log rotation..."
sudo tee /etc/logrotate.d/ree-ai > /dev/null << EOF
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 0644 root root
    postrotate
        /usr/bin/docker kill -s USR1 \$(docker ps -q) 2>/dev/null || true
    endscript
}
EOF

# Show summary
echo ""
echo "✅ Production Server Setup Complete!"
echo "===================================="
echo ""
echo "📊 Installed Components:"
echo "  - Docker & Docker Compose"
echo "  - UFW Firewall (configured)"
echo "  - Git"
echo "  - REE AI systemd service"
echo ""
echo "🌐 Open Ports:"
for port in "${!SERVICES[@]}"; do
    echo "  - $port: ${SERVICES[$port]}"
done
echo ""
echo "📁 Project Directory: $PROJECT_DIR"
echo ""
echo "🎮 Management Commands:"
echo "  ./start-ree-ai.sh    - Start all services"
echo "  ./stop-ree-ai.sh     - Stop all services" 
echo "  ./status-ree-ai.sh   - Check service status"
echo "  ./logs-ree-ai.sh     - View logs"
echo "  ./backup-data.sh     - Backup data"
echo ""
echo "🔧 System Commands:"
echo "  sudo systemctl start ree-ai     - Start REE AI service"
echo "  sudo systemctl stop ree-ai      - Stop REE AI service"
echo "  sudo systemctl status ree-ai    - Check service status"
echo ""
echo "⚠️  Important Next Steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Setup SSH keys for GitHub Actions deployment"
echo "3. Reboot server to ensure Docker group membership"
echo ""
echo "🚀 Quick Start:"
echo "  nano .env                    # Add your OPENAI_API_KEY"
echo "  sudo reboot                  # Reboot to apply group changes"
echo "  ./start-ree-ai.sh            # Start REE AI after reboot"
echo ""

# Final notes
echo "💡 Tips:"
echo "  - Firewall status: sudo ufw status"
echo "  - View open ports: sudo netstat -tulpn"
echo "  - Docker info: docker info"
echo "  - Disk usage: df -h"
echo ""
echo "📖 After reboot, run ./status-ree-ai.sh to check everything is working!"