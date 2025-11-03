#!/bin/bash
# Reset Open WebUI - Remove old data and restart with clean state

echo "🔄 Stopping Open WebUI..."
docker-compose stop open-webui

echo "🗑️  Removing old Open WebUI data..."
docker volume rm ree-ai_open_webui_data 2>/dev/null || echo "Volume already removed or doesn't exist"

echo "🚀 Starting Open WebUI with clean state..."
docker-compose up -d open-webui

echo "✅ Done! Open WebUI reset complete."
echo "📌 Access at: http://localhost:3000"
echo ""
echo "⚠️  Important: You'll need to create a new admin account"
