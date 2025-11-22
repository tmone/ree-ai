#!/bin/bash
# Verification Script for Structured Response Implementation
# Checks that all required files exist and are properly structured

set -e

echo "🔍 Verifying Structured Response Implementation..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS=0
FAILURE=0

check_file() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $description - FILE MISSING: $file"
        ((FAILURE++))
    fi
}

check_content() {
    local file=$1
    local pattern=$2
    local description=$3

    if [ -f "$file" ] && grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✓${NC} $description"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $description - NOT FOUND in $file"
        ((FAILURE++))
    fi
}

echo "📦 Backend Files"
echo "────────────────"
check_file "shared/models/ui_components.py" "UI Components model"
check_content "shared/models/ui_components.py" "class PropertyCarouselComponent" "PropertyCarouselComponent class"
check_content "shared/models/ui_components.py" "class PropertyInspectorComponent" "PropertyInspectorComponent class"

check_file "shared/models/orchestrator.py" "Orchestrator models"
check_content "shared/models/orchestrator.py" "components: Optional\[List\[UIComponent\]\]" "OrchestrationResponse.components field"

check_file "services/orchestrator/handlers/base_handler.py" "BaseHandler"
check_file "services/orchestrator/handlers/search_handler.py" "SearchHandler"
check_content "services/orchestrator/handlers/search_handler.py" "async def handle" "SearchHandler.handle method"

check_file "services/orchestrator/handlers/property_detail_handler.py" "PropertyDetailHandler"
check_content "services/orchestrator/handlers/property_detail_handler.py" "_extract_property_reference" "Property reference extraction"

check_file "services/orchestrator/handlers/__init__.py" "Handlers __init__"
check_content "services/orchestrator/handlers/__init__.py" "SearchHandler" "SearchHandler export"
check_content "services/orchestrator/handlers/__init__.py" "PropertyDetailHandler" "PropertyDetailHandler export"

check_content "services/orchestrator/main.py" "from services.orchestrator.handlers" "Orchestrator imports handlers"
check_content "services/orchestrator/main.py" "self.search_handler" "SearchHandler initialization"
check_content "services/orchestrator/main.py" "self.property_detail_handler" "PropertyDetailHandler initialization"

echo ""
echo "🎨 Frontend Files"
echo "─────────────────"
check_file "frontend/open-webui/src/lib/styles/design-tokens.css" "Design tokens CSS"
check_content "frontend/open-webui/src/lib/styles/design-tokens.css" "--brand-primary: #3b82f6" "Brand color token"
check_content "frontend/open-webui/src/lib/styles/design-tokens.css" "--compact-card-max-width" "Compact card dimensions"

check_file "frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte" "CompactPropertyCard component"
check_content "frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte" "export let property" "Property prop"
check_content "frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte" "Xem chi tiết" "CTA button text"

check_file "frontend/open-webui/src/lib/components/property/PropertyDetailModal.svelte" "PropertyDetailModal component"
check_content "frontend/open-webui/src/lib/components/property/PropertyDetailModal.svelte" "PropertyInspector" "PropertyInspector import"
check_content "frontend/open-webui/src/lib/components/property/PropertyDetailModal.svelte" "handleClose" "Close handler"

check_file "frontend/open-webui/src/lib/components/chat/StructuredResponseRenderer.svelte" "StructuredResponseRenderer component"
check_content "frontend/open-webui/src/lib/components/chat/StructuredResponseRenderer.svelte" "property-carousel" "Carousel rendering"
check_content "frontend/open-webui/src/lib/components/chat/StructuredResponseRenderer.svelte" "property-inspector" "Inspector rendering"

check_file "frontend/open-webui/src/lib/components/chat/Messages/ResponseMessage.svelte" "ResponseMessage component"
check_content "frontend/open-webui/src/lib/components/chat/Messages/ResponseMessage.svelte" "StructuredResponseRenderer" "StructuredResponseRenderer import"
check_content "frontend/open-webui/src/lib/components/chat/Messages/ResponseMessage.svelte" "components?: Array" "MessageType.components field"

check_file "frontend/open-webui/src/lib/apis/ree-ai/orchestrator.ts" "Orchestrator API"
check_content "frontend/open-webui/src/lib/apis/ree-ai/orchestrator.ts" "components?: Array" "OrchestratorResponse.components field"

echo ""
echo "📚 Documentation"
echo "────────────────"
check_file "docs/design/DESIGN_TOKENS.md" "Design tokens documentation"
check_file "docs/design/OPENAI_APPS_SDK_MAPPING.md" "OpenAI Apps SDK mapping"
check_file "docs/implementation/STRUCTURED_RESPONSE_IMPLEMENTATION.md" "Implementation documentation"
check_file "docs/testing/TESTING_GUIDE.md" "Testing guide"

echo ""
echo "📊 Summary"
echo "──────────"
TOTAL=$((SUCCESS + FAILURE))
echo -e "Total checks: $TOTAL"
echo -e "${GREEN}Passed: $SUCCESS${NC}"
if [ $FAILURE -gt 0 ]; then
    echo -e "${RED}Failed: $FAILURE${NC}"
    echo ""
    echo "❌ Verification failed. Please fix the issues above."
    exit 1
else
    echo -e "${GREEN}Failed: 0${NC}"
    echo ""
    echo "✅ All verification checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Build services: docker-compose build orchestrator"
    echo "2. Start services: docker-compose up -d"
    echo "3. Run tests: See docs/testing/TESTING_GUIDE.md"
    exit 0
fi
