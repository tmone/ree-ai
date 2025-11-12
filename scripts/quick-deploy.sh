#!/bin/bash

# ============================================================
# Quick Deploy to Production Script
# ============================================================

echo "🚀 REE AI - Quick Deploy to Production"
echo "======================================"

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "release" ]; then
    echo ""
    echo "⚠️ Warning: You are not on the release branch!"
    echo "Production deployment should be done from 'release' branch"
    echo ""
    read -p "Do you want to switch to release branch? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Switching to release branch..."
        git checkout release
        git pull origin release
    else
        echo "❌ Deploy cancelled"
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ Warning: You have uncommitted changes"
    echo ""
    git status --porcelain
    echo ""
    read -p "Do you want to commit these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_message
        git add .
        git commit -m "$commit_message"
        git push origin release
    else
        echo "❌ Please commit your changes before deploying"
        exit 1
    fi
fi

echo ""
echo "🔍 Pre-deployment checks:"
echo "  ✅ On release branch"
echo "  ✅ No uncommitted changes"
echo ""

# Show deployment options
echo "📋 Deployment Options:"
echo "  1. 🚀 Deploy to Production (Manual trigger)"
echo "  2. 📤 Push to trigger auto-deploy"
echo "  3. 📊 Monitor current deployment"
echo "  4. ❌ Cancel"
echo ""

read -p "Choose option (1-4): " -n 1 -r option
echo

case $option in
    1)
        echo "🚀 Triggering manual deployment..."
        gh workflow run deploy-production.yml --ref release --field confirm_production="PRODUCTION"
        echo "✅ Deployment triggered!"
        echo ""
        echo "📋 To monitor deployment:"
        echo "  ./scripts/monitor-deployment.sh"
        echo ""
        echo "🌐 Or view on GitHub:"
        echo "  gh run list --workflow=deploy-production.yml"
        ;;
    2)
        echo "📤 Pushing to trigger auto-deploy..."
        # Create empty commit to trigger deployment
        git commit --allow-empty -m "trigger production deployment [skip ci]"
        git push origin release
        echo "✅ Push completed! Deployment will start automatically"
        ;;
    3)
        echo "📊 Starting deployment monitor..."
        ./scripts/monitor-deployment.sh
        ;;
    4)
        echo "❌ Deploy cancelled"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "🎉 Quick deploy completed!"