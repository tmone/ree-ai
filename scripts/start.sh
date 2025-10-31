#!/bin/bash
# REE AI Project Startup Script
# Auto-provisions PostgreSQL before starting services

set -e

echo "======================================================================="
echo "🚀 REE AI PROJECT STARTUP"
echo "======================================================================="

# Change to project root
cd "$(dirname "$0")/.."

# Step 1: Auto-provision PostgreSQL
echo ""
echo "Step 1: PostgreSQL Auto-Provisioning"
echo "-----------------------------------------------------------------------"
python3 scripts/init_postgres.py
if [ $? -ne 0 ]; then
    echo "❌ PostgreSQL provisioning failed"
    exit 1
fi

# Load PostgreSQL connection info
if [ -f .env.postgres ]; then
    export $(cat .env.postgres | grep -v '^#' | xargs)
    echo "✅ Loaded PostgreSQL connection from .env.postgres"
fi

# Step 2: Start other services (optional)
echo ""
echo "Step 2: Starting Services (optional)"
echo "-----------------------------------------------------------------------"
echo "Available profiles:"
echo "  - mock: Mock services for development"
echo "  - real: Real services for production"
echo "  - all: All services"
echo ""
read -p "Start services? (mock/real/all/skip) [skip]: " PROFILE
PROFILE=${PROFILE:-skip}

if [ "$PROFILE" != "skip" ]; then
    echo "🐳 Starting services with profile: $PROFILE"
    docker-compose --profile "$PROFILE" up -d
else
    echo "⏭️  Skipped starting services"
fi

echo ""
echo "======================================================================="
echo "✅ STARTUP COMPLETE"
echo "======================================================================="
echo ""
echo "PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo "Quick commands:"
echo "  - Test crawler:  python3 tests/crawl_and_store.py 100"
echo "  - Run evaluation: python3 tests/prompt_evaluation/quick_eval.py"
echo "  - View logs:     docker-compose logs -f"
echo ""
