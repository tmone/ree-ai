#!/bin/bash

# Script to setup SSH key for GitHub Actions deployment
# Run this script on your local machine (not on the production server)

set -e

echo "🔑 GitHub Actions SSH Setup for Production Server"
echo "=================================================="
echo ""
echo "This script will:"
echo "1. Generate an SSH key pair for GitHub Actions"
echo "2. Copy the public key to your production server" 
echo "3. Show you the private key to add to GitHub Secrets"
echo ""

# Configuration
SERVER_IP="192.168.1.11"
SERVER_USER="tmone"
SERVER_PASSWORD="1"
KEY_NAME="github-actions-ree-ai"

# Confirm before proceeding
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled."
    exit 1
fi

# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh

# Generate SSH key pair
echo "🔐 Generating SSH key pair..."
ssh-keygen -t rsa -b 4096 -f ~/.ssh/$KEY_NAME -N "" -C "github-actions@ree-ai-deployment"

echo "✅ SSH key pair generated:"
echo "   Private key: ~/.ssh/$KEY_NAME"
echo "   Public key: ~/.ssh/$KEY_NAME.pub"
echo ""

# Display public key
echo "📋 Public key content:"
echo "=================================================="
cat ~/.ssh/$KEY_NAME.pub
echo "=================================================="
echo ""

# Instructions for manual setup (since sshpass might not be available)
echo "🚀 Next Steps:"
echo ""
echo "1. Copy the public key to your production server:"
echo "   Run this command on your production server (192.168.1.11):"
echo ""
echo "   mkdir -p ~/.ssh"
echo "   echo '$(cat ~/.ssh/$KEY_NAME.pub)' >> ~/.ssh/authorized_keys"
echo "   chmod 700 ~/.ssh"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "2. Test SSH connection (run this on your local machine):"
echo "   ssh -i ~/.ssh/$KEY_NAME tmone@192.168.1.11 'echo \"SSH connection successful!\"'"
echo ""
echo "3. Add the private key to GitHub Secrets:"
echo "   - Go to: https://github.com/tmone/ree-ai/settings/secrets/actions"
echo "   - Click 'New repository secret'"
echo "   - Name: PRODUCTION_SSH_KEY"
echo "   - Value: Copy the content below"
echo ""
echo "📋 Private key content for GitHub Secret:"
echo "=================================================="
cat ~/.ssh/$KEY_NAME
echo "=================================================="
echo ""
echo "4. Optional: Add OPENAI_API_KEY secret if you haven't already:"
echo "   - Name: OPENAI_API_KEY" 
echo "   - Value: your-openai-api-key"
echo ""
echo "✅ After completing these steps, GitHub Actions will be able to deploy to your server!"
echo ""

# Save instructions to file
cat > setup-instructions.txt << EOF
REE AI - GitHub Actions Deployment Setup Instructions
====================================================

1. SSH Public Key (add to production server):
$(cat ~/.ssh/$KEY_NAME.pub)

Commands to run on production server (192.168.1.11):
mkdir -p ~/.ssh
echo '$(cat ~/.ssh/$KEY_NAME.pub)' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

2. SSH Private Key (add to GitHub Secrets as PRODUCTION_SSH_KEY):
$(cat ~/.ssh/$KEY_NAME)

3. Test SSH connection:
ssh -i ~/.ssh/$KEY_NAME tmone@192.168.1.11 'echo "SSH connection successful!"'

4. GitHub Repository URL:
https://github.com/tmone/ree-ai/settings/secrets/actions

Required GitHub Secrets:
- PRODUCTION_SSH_KEY (the private key above)
- OPENAI_API_KEY (your OpenAI API key)

After setup, push to main branch to trigger automatic deployment!
EOF

echo "💾 Instructions saved to: setup-instructions.txt"
echo ""
echo "🎯 Quick Test:"
echo "   After setting up the public key on the server, test with:"
echo "   ssh -i ~/.ssh/$KEY_NAME tmone@192.168.1.11 'echo \"Connection test successful\"'"