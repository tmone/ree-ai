#!/bin/bash

# ============================================================
# GitHub Actions Self-Hosted Runner Setup for Production
# ============================================================

echo "🚀 Setting up GitHub Actions Runner for Production..."

# Configuration
RUNNER_DIR="$HOME/actions-runner-production"
REPO_URL="https://github.com/tmone/ree-ai"
RUNNER_NAME="production-runner"
LABELS="self-hosted,linux,x64,production,ubuntu"
REGISTRATION_TOKEN="AGEQ3JRDIFROLR5DJE3UVLTJCR6UM"

# Create runner directory
echo "📁 Creating runner directory..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download runner if not exists
if [ ! -f "config.sh" ]; then
    echo "⬇️ Downloading GitHub Actions Runner..."
    
    # Get latest runner version
    RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep tag_name | cut -d'"' -f4 | cut -d'v' -f2)
    echo "Latest runner version: v$RUNNER_VERSION"
    
    # Download and extract
    curl -o actions-runner-linux-x64.tar.gz -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
    tar xzf actions-runner-linux-x64.tar.gz
    rm actions-runner-linux-x64.tar.gz
fi

# Configure runner
echo "⚙️ Configuring runner..."
./config.sh \
    --url "$REPO_URL" \
    --token "$REGISTRATION_TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "$LABELS" \
    --runnergroup "Default" \
    --work "_work" \
    --replace

# Install service
echo "🔧 Installing runner as systemd service..."
sudo ./svc.sh install

# Start service
echo "▶️ Starting runner service..."
sudo ./svc.sh start

# Check status
echo "📊 Checking runner status..."
sudo ./svc.sh status

echo ""
echo "✅ GitHub Actions Runner setup completed!"
echo ""
echo "🔍 Runner Details:"
echo "  - Name: $RUNNER_NAME"
echo "  - Labels: $LABELS"
echo "  - Directory: $RUNNER_DIR"
echo "  - Repository: $REPO_URL"
echo ""
echo "📋 Service Management Commands:"
echo "  - Start:  sudo systemctl start actions.runner.tmone-ree-ai.production-runner"
echo "  - Stop:   sudo systemctl stop actions.runner.tmone-ree-ai.production-runner" 
echo "  - Status: sudo systemctl status actions.runner.tmone-ree-ai.production-runner"
echo "  - Logs:   journalctl -f -u actions.runner.tmone-ree-ai.production-runner"
echo ""