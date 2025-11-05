#!/bin/bash

# Script to verify GitHub Secrets are configured correctly
# Run this manually to test before deployment

echo "======================================"
echo "GitHub Secrets Configuration Check"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if secret is set
check_secret() {
    local secret_name=$1
    local is_required=$2

    if [ -z "${!secret_name}" ]; then
        if [ "$is_required" = "required" ]; then
            echo -e "${RED}❌ $secret_name${NC} - MISSING (REQUIRED)"
            return 1
        else
            echo -e "${YELLOW}⚠️  $secret_name${NC} - Not set (optional, will use default)"
            return 0
        fi
    else
        echo -e "${GREEN}✅ $secret_name${NC} - Set"
        return 0
    fi
}

echo "Required Secrets:"
echo "===================="
check_secret "OPENAI_API_KEY" "required"
check_secret "POSTGRES_PASSWORD" "required"
check_secret "WEBUI_SECRET_KEY" "required"
echo ""

echo "Optional Secrets:"
echo "===================="
check_secret "POSTGRES_DB" "optional"
check_secret "POSTGRES_USER" "optional"
check_secret "OPENSEARCH_PASSWORD" "optional"
check_secret "TASK_MODEL" "optional"
check_secret "LANGCHAIN_TRACING_V2" "optional"
check_secret "LANGCHAIN_API_KEY" "optional"
echo ""

echo "======================================"
echo "Configuration Summary"
echo "======================================"

# Count missing required secrets
missing_count=0
[ -z "$OPENAI_API_KEY" ] && ((missing_count++))
[ -z "$POSTGRES_PASSWORD" ] && ((missing_count++))
[ -z "$WEBUI_SECRET_KEY" ] && ((missing_count++))

if [ $missing_count -eq 0 ]; then
    echo -e "${GREEN}✅ All required secrets are configured!${NC}"
    echo ""
    echo "You can now push to main branch to trigger deployment."
    exit 0
else
    echo -e "${RED}❌ $missing_count required secret(s) missing!${NC}"
    echo ""
    echo "Please add missing secrets to GitHub:"
    echo "1. Go to: https://github.com/YOUR_USERNAME/ree-ai/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Add the missing secrets listed above"
    echo ""
    echo "Required secrets:"
    [ -z "$OPENAI_API_KEY" ] && echo "  - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)"
    [ -z "$POSTGRES_PASSWORD" ] && echo "  - POSTGRES_PASSWORD (create a strong password)"
    [ -z "$WEBUI_SECRET_KEY" ] && echo "  - WEBUI_SECRET_KEY (generate random string)"
    exit 1
fi
