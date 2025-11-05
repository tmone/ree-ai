#!/bin/bash

# Script to generate secure random secrets for GitHub Secrets configuration

echo "======================================"
echo "GitHub Secrets Generator"
echo "======================================"
echo ""
echo "Copy these values to GitHub Secrets:"
echo "https://github.com/YOUR_USERNAME/ree-ai/settings/secrets/actions"
echo ""

# Function to generate random string
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

echo "1. POSTGRES_PASSWORD"
echo "   Value: $(generate_secret)"
echo ""

echo "2. WEBUI_SECRET_KEY"
echo "   Value: $(generate_secret)"
echo ""

echo "3. OPENSEARCH_PASSWORD (Optional)"
echo "   Value: Admin123!@#  (or generate: $(generate_secret))"
echo ""

echo "4. OPENAI_API_KEY"
echo "   ⚠️  You need to get this from: https://platform.openai.com/api-keys"
echo "   Value: sk-proj-... (paste your key here)"
echo ""

echo "======================================"
echo "Steps to Add Secrets to GitHub:"
echo "======================================"
echo ""
echo "1. Go to your repository on GitHub"
echo "2. Click 'Settings' tab"
echo "3. In left sidebar: 'Secrets and variables' > 'Actions'"
echo "4. Click 'New repository secret'"
echo "5. Add each secret:"
echo "   - Name: POSTGRES_PASSWORD"
echo "   - Secret: (paste value from above)"
echo "   - Click 'Add secret'"
echo "6. Repeat for other secrets"
echo ""
echo "After adding all secrets, test with:"
echo "./scripts/check-secrets.sh"
echo ""
