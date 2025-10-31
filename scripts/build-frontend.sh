#!/bin/bash

# REE AI Frontend Build Script
# Builds the custom Open WebUI frontend for production

set -e  # Exit on error

echo "🚀 REE AI Frontend Build Script"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Step 1: Check if node is available for local development
echo -e "\n${BLUE}📦 Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js found: $NODE_VERSION${NC}"

    # Check if in frontend directory
    if [ "$1" == "--local" ]; then
        echo -e "\n${BLUE}🔨 Building locally with Node.js...${NC}"
        cd frontend/open-webui

        # Install dependencies
        echo -e "${BLUE}📥 Installing dependencies...${NC}"
        npm ci --force

        # Build
        echo -e "${BLUE}🏗️  Building frontend...${NC}"
        npm run build

        echo -e "\n${GREEN}✅ Local build completed!${NC}"
        echo -e "Build output is in: ${BLUE}frontend/open-webui/build/${NC}"
        exit 0
    fi
else
    echo -e "${RED}⚠️  Node.js not found (only needed for local builds)${NC}"
fi

# Step 2: Build Docker image
echo -e "\n${BLUE}🐳 Building Docker image...${NC}"
echo "This may take 10-15 minutes on first build..."

docker compose build open-webui

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Docker image built successfully!${NC}"
else
    echo -e "\n${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 3: Show next steps
echo -e "\n${GREEN}🎉 Build completed successfully!${NC}"
echo -e "\nNext steps:"
echo -e "1. Start the frontend:"
echo -e "   ${BLUE}docker compose --profile real up -d open-webui${NC}"
echo -e "\n2. Access the frontend:"
echo -e "   ${BLUE}http://localhost:3000${NC}"
echo -e "\n3. View logs:"
echo -e "   ${BLUE}docker compose logs -f open-webui${NC}"
echo -e "\n4. Stop the frontend:"
echo -e "   ${BLUE}docker compose stop open-webui${NC}"

echo -e "\n${BLUE}ℹ️  For local development without Docker:${NC}"
echo -e "   ${BLUE}./scripts/build-frontend.sh --local${NC}"
echo -e "   ${BLUE}cd frontend/open-webui && npm run dev${NC}"
