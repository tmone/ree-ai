#!/bin/bash

# Script to sync .env file to GitHub Secrets using gh CLI
# This automates the process of adding secrets to GitHub Actions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================"
echo "Sync .env to GitHub Secrets"
echo -e "======================================${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file first:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Edit values"
    exit 1
fi

# Check if gh CLI is authenticated
if ! gh auth status &>/dev/null; then
    echo -e "${RED}❌ GitHub CLI not authenticated!${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI authenticated${NC}"
echo ""

# Function to set secret from .env
set_secret_from_env() {
    local key=$1
    local required=$2

    # Extract value from .env (handle comments and empty lines)
    local value=$(grep "^${key}=" .env | cut -d'=' -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/#.*//')

    # Check if value is empty or placeholder
    if [ -z "$value" ] || [[ "$value" == *"your-"* ]] || [[ "$value" == *"sk-your-"* ]]; then
        if [ "$required" = "required" ]; then
            echo -e "${RED}❌ $key${NC} - Missing or placeholder value in .env"
            echo "   Please update .env file with real value for $key"
            return 1
        else
            echo -e "${YELLOW}⚠️  $key${NC} - Skipped (empty or placeholder)"
            return 0
        fi
    fi

    # Set secret using gh CLI
    echo -n "Setting $key... "
    if echo "$value" | gh secret set "$key" --repo $(gh repo view --json nameWithOwner -q .nameWithOwner) 2>/dev/null; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
}

echo "Setting Required Secrets:"
echo "=========================="

failed_count=0

# Required secrets
set_secret_from_env "OPENAI_API_KEY" "required" || ((failed_count++))
set_secret_from_env "POSTGRES_PASSWORD" "required" || ((failed_count++))
set_secret_from_env "WEBUI_SECRET_KEY" "required" || ((failed_count++))

echo ""
echo "Setting Optional Secrets:"
echo "=========================="

# Optional secrets (won't fail if missing)
set_secret_from_env "POSTGRES_DB" "optional"
set_secret_from_env "POSTGRES_USER" "optional"
set_secret_from_env "OPENSEARCH_PASSWORD" "optional"
set_secret_from_env "TASK_MODEL" "optional"
set_secret_from_env "LANGCHAIN_TRACING_V2" "optional"
set_secret_from_env "LANGCHAIN_API_KEY" "optional"

echo ""
echo -e "${BLUE}======================================"
echo "Summary"
echo -e "======================================${NC}"

if [ $failed_count -eq 0 ]; then
    echo -e "${GREEN}✅ All secrets synced successfully!${NC}"
    echo ""
    echo "View secrets at:"
    echo "  $(gh repo view --json url -q .url)/settings/secrets/actions"
    echo ""
    echo "Next steps:"
    echo "  1. Verify secrets: gh secret list"
    echo "  2. Commit and push to main to trigger deployment"
    echo "  3. Monitor deployment: gh run list"
    exit 0
else
    echo -e "${RED}❌ $failed_count required secret(s) failed!${NC}"
    echo ""
    echo "Please fix the issues above and run again:"
    echo "  ./scripts/sync-secrets-to-github.sh"
    exit 1
fi
