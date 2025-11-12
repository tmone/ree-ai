#!/bin/bash

# Setup GitHub Self-hosted Runner on Production Server
# Run this script on the production server (192.168.1.11)

set -e

echo "🏗️ GitHub Self-hosted Runner Setup for Production"
echo "================================================="
echo ""
echo "This script will install GitHub Actions self-hosted runner"
echo "on the production server (192.168.1.11)"
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
echo "Server: $(hostname -I | awk '{print $1}')"
echo ""

# Confirm before proceeding
read -p "Continue with GitHub runner setup? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled."
    exit 1
fi

# Create runner directory
RUNNER_DIR="$HOME/github-actions-runner"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

echo "📁 Created runner directory: $RUNNER_DIR"

# Download GitHub Actions Runner (latest version)
echo "📥 Downloading GitHub Actions Runner..."

# Get latest runner version
RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
echo "Latest runner version: $RUNNER_VERSION"

# Download runner
curl -o actions-runner-linux-x64.tar.gz -L "https://github.com/actions/runner/releases/download/$RUNNER_VERSION/actions-runner-linux-x64-$RUNNER_VERSION.tar.gz"

# Verify checksum (optional but recommended)
echo "🔍 Verifying download..."
if curl -s "https://github.com/actions/runner/releases/download/$RUNNER_VERSION/actions-runner-linux-x64-$RUNNER_VERSION.tar.gz.sha256" | sha256sum -c; then
    echo "✅ Download verified"
else
    echo "⚠️  Could not verify download (continuing anyway)"
fi

# Extract runner
echo "📦 Extracting runner..."
tar xzf actions-runner-linux-x64.tar.gz

# Install dependencies
echo "🔧 Installing dependencies..."
sudo ./bin/installdependencies.sh

echo ""
echo "✅ GitHub Actions Runner installed successfully!"
echo ""
echo "🔧 Next Steps:"
echo "============="
echo ""
echo "1. Get registration token from GitHub:"
echo "   - Go to: https://github.com/tmone/ree-ai/settings/actions/runners/new"
echo "   - Select 'Linux' and copy the token"
echo ""
echo "2. Configure the runner:"
echo "   cd $RUNNER_DIR"
echo "   ./config.sh --url https://github.com/tmone/ree-ai --token YOUR_TOKEN_HERE"
echo ""
echo "3. Set runner labels (when prompted):"
echo "   Labels: self-hosted,linux,x64,production"
echo ""
echo "4. Install as service:"
echo "   sudo ./svc.sh install"
echo "   sudo ./svc.sh start"
echo ""
echo "5. Check status:"
echo "   sudo ./svc.sh status"
echo ""
echo "📋 Configuration Example:"
echo "========================"
echo "Repository URL: https://github.com/tmone/ree-ai"
echo "Runner group: Default"
echo "Runner name: production-server"
echo "Labels: self-hosted,linux,x64,production"
echo "Work folder: _work"
echo ""
echo "💡 After setup, update .github/workflows/deploy-production.yml:"
echo "   runs-on: [self-hosted, linux, x64, production]"
echo ""

# Create helper scripts
echo "📝 Creating helper scripts..."

# Status script
cat > check-runner-status.sh << 'EOF'
#!/bin/bash
echo "🏃 GitHub Actions Runner Status"
echo "==============================="
echo ""
echo "Service Status:"
sudo ./svc.sh status
echo ""
echo "Runner Logs (last 20 lines):"
tail -20 _diag/Runner_*.log 2>/dev/null || echo "No logs found"
EOF

# Start script
cat > start-runner.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting GitHub Actions Runner..."
sudo ./svc.sh start
sudo ./svc.sh status
EOF

# Stop script
cat > stop-runner.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping GitHub Actions Runner..."
sudo ./svc.sh stop
sudo ./svc.sh status
EOF

# Restart script
cat > restart-runner.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting GitHub Actions Runner..."
sudo ./svc.sh stop
sleep 2
sudo ./svc.sh start
sudo ./svc.sh status
EOF

# Make scripts executable
chmod +x *.sh

echo "✅ Helper scripts created:"
echo "  - check-runner-status.sh"
echo "  - start-runner.sh"
echo "  - stop-runner.sh"
echo "  - restart-runner.sh"
echo ""

echo "🎯 Quick Setup Guide:"
echo "===================="
echo ""
echo "# 1. Get token from GitHub (copy the command):"
echo "curl -X POST https://api.github.com/repos/tmone/ree-ai/actions/runners/registration-token \\"
echo "  -H 'Authorization: token YOUR_GITHUB_PAT' | jq -r .token"
echo ""
echo "# 2. Configure runner:"
echo "./config.sh --url https://github.com/tmone/ree-ai --token TOKEN_FROM_STEP_1"
echo ""
echo "# 3. Install as service:"
echo "sudo ./svc.sh install"
echo "sudo ./svc.sh start"
echo ""
echo "# 4. Verify:"
echo "./check-runner-status.sh"
echo ""
echo "🌐 After setup, your workflows will run on this server!"
echo "No more SSH needed - direct deployment! 🎉"