#!/bin/bash

# ============================================================
# GitHub Actions Deployment Monitoring Script  
# ============================================================

echo "🔍 Monitoring GitHub Actions Deployment..."

# Check latest workflow run
RUN_ID=$(gh run list --workflow=deploy-production.yml --limit 1 --json id --jq '.[0].id')

if [ -z "$RUN_ID" ]; then
    echo "❌ No workflow runs found"
    exit 1
fi

echo "📋 Monitoring Run ID: $RUN_ID"
echo ""

# Watch workflow in real-time
while true; do
    clear
    echo "🚀 GitHub Actions Deployment Monitor"
    echo "==================================="
    echo "Run ID: $RUN_ID"
    echo "Timestamp: $(date)"
    echo ""
    
    # Get run status
    gh run view $RUN_ID
    
    # Check if completed
    STATUS=$(gh run view $RUN_ID --json status --jq '.status')
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        echo "🏁 Deployment completed!"
        
        # Show final status
        CONCLUSION=$(gh run view $RUN_ID --json conclusion --jq '.conclusion')
        if [ "$CONCLUSION" = "success" ]; then
            echo "✅ Status: SUCCESS"
            echo ""
            echo "🌐 Production URLs:"
            echo "  - Open WebUI: http://192.168.1.11:3000"
            echo "  - Core Gateway: http://192.168.1.11:8080"
            echo "  - Orchestrator: http://192.168.1.11:8090"
            echo "  - RAG Service: http://192.168.1.11:8091"
        else
            echo "❌ Status: $CONCLUSION"
            echo ""
            echo "📋 Getting error logs..."
            gh run view $RUN_ID --log-failed
        fi
        break
    fi
    
    echo ""
    echo "⏳ Deployment in progress... (refreshing in 10s)"
    sleep 10
done