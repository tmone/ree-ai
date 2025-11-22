# Structured Response Implementation - OpenAI Apps SDK Pattern

**Date:** 2025-11-22
**Branch:** `claude/add-card-components-01Fc9vYQTsScqqEPN2aRZ2r6`
**Status:** ✅ Implementation Complete, Pending Testing

---

## Overview

Implemented end-to-end structured response system following OpenAI Apps SDK design guidelines. Backend returns structured data with UI components, frontend renders them using specialized components.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER QUERY                                  │
│              "tìm căn hộ 2PN quận 1"                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│               ORCHESTRATOR                                       │
│  Intent: SEARCH → SearchHandler.handle()                       │
│  Returns: {                                                      │
│    message: "Tìm thấy 5 bất động sản...",                      │
│    components: [{                                                │
│      type: "property-carousel",                                 │
│      data: {properties: [...], total: 5}                        │
│    }]                                                            │
│  }                                                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            OPEN WEBUI ROUTER                                     │
│  /api/orchestrator/query → forwards response                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          FRONTEND (ResponseMessage.svelte)                       │
│  Detects: message.components exists                             │
│  Renders: <StructuredResponseRenderer />                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│      StructuredResponseRenderer.svelte                          │
│  - property-carousel → CompactPropertyCard list                 │
│  - property-inspector → PropertyDetailModal                     │
└─────────────────────────────────────────────────────────────────┘
```

## CTO Requirements Mapping

### ✅ Requirement 1: Search Results Display
**CTO:** "Hiển thị danh sách bất động sản với thông tin cơ bản (ID, hình, tiêu đề, địa chỉ, giá, diện tích)"

**Implementation:**
- `SearchHandler` returns `PropertyCarouselComponent` with property list
- `CompactPropertyCard.svelte` displays 4 data points + 1 CTA:
  - Title, Location, Key Feature (bedrooms + area), Price
  - CTA: "Xem chi tiết →"
- Follows OpenAI "Simple" principle

**Files:**
- `services/orchestrator/handlers/search_handler.py`
- `frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte`

### ✅ Requirement 2: Property Detail View (3 Methods)
**CTO:** "3 cách xem chi tiết: chat by ID, chat by keyword, click on card"

**Implementation:**
- `PropertyDetailHandler` supports:
  1. By ID: "cho tôi xem chi tiết thông tin căn nhà 456"
  2. By keyword: "cho tôi xem thông tin căn nhà Vinhomes"
  3. By position: "xem căn số 2 trong danh sách"
- Click event triggers query to orchestrator

**Files:**
- `services/orchestrator/handlers/property_detail_handler.py`
- `frontend/open-webui/src/lib/components/chat/StructuredResponseRenderer.svelte`

### ✅ Requirement 3: Detail Popup/Modal
**CTO:** "Hiển thị chi tiết trong popup để user có thể đóng và xem các item khác"

**Implementation:**
- `PropertyDetailModal.svelte` wraps `PropertyInspector`
- Supports ESC key, backdrop click, close button
- Returns to property list on close

**Files:**
- `frontend/open-webui/src/lib/components/property/PropertyDetailModal.svelte`

### ✅ Requirement 4: OpenAI Design Compliance
**CTO:** "Follow OpenAI Apps SDK Design Guidelines from Figma"

**Implementation:**
- Extracted design tokens from Figma (file: 4JSHQqDBBms4mAvprmbN2b)
- System colors, grid-based spacing, WCAG AA compliance
- Component types: Carousel (🎠), Inspector (🔎)

**Files:**
- `frontend/open-webui/src/lib/styles/design-tokens.css`
- `docs/design/DESIGN_TOKENS.md`

---

## Files Created/Modified

### Backend (Python)

#### 1. `shared/models/ui_components.py` (NEW)
**Purpose:** Define UI component types and models

```python
class ComponentType(str, Enum):
    PROPERTY_CAROUSEL = "property-carousel"  # 🎠 Inline Carousel
    PROPERTY_INSPECTOR = "property-inspector"  # 🔎 Inspector

class PropertyCarouselComponent(UIComponent):
    @classmethod
    def create(cls, properties: List[Dict], total: int):
        return cls(
            type=ComponentType.PROPERTY_CAROUSEL,
            data={"properties": properties, "total": total}
        )
```

**Lines:** 127
**Pattern:** OpenAI Apps SDK component types

#### 2. `shared/models/orchestrator.py` (MODIFIED)
**Purpose:** Add components field to OrchestrationResponse

```python
class OrchestrationResponse(BaseModel):
    response: str
    components: Optional[List[UIComponent]] = Field(None)  # NEW
```

**Change:** Added components field (line 67-70)

#### 3. `services/orchestrator/handlers/search_handler.py` (MODIFIED)
**Purpose:** Return structured response with PropertyCarouselComponent

```python
async def handle(...) -> Dict[str, Any]:
    # Create PropertyCarouselComponent
    component = PropertyCarouselComponent.create(
        properties=formatted_properties,
        total=total_count
    )

    return {
        "message": response_text,
        "components": [component.dict()]
    }
```

**Lines:** 210 (total)
**Pattern:** BaseHandler returning Dict with message + components

#### 4. `services/orchestrator/handlers/property_detail_handler.py` (NEW)
**Purpose:** Handle property detail requests (3 methods)

```python
class PropertyDetailHandler(BaseHandler):
    async def handle(...) -> Dict[str, Any]:
        # Extract: ID, position, or keyword
        property_id = self._extract_property_reference(query)

        # Fetch from DB Gateway
        property_data = await self.call_service(...)

        # Create PropertyInspectorComponent
        component = PropertyInspectorComponent.create(property_data)

        return {
            "message": t('property_detail.showing_details'),
            "components": [component.dict()]
        }
```

**Lines:** 255
**Methods:** By ID, by position, by keyword

#### 5. `services/orchestrator/main.py` (MODIFIED)
**Purpose:** Integrate handlers into orchestration flow

**Changes:**
- Import SearchHandler, PropertyDetailHandler (line 62-63)
- Initialize handlers in `__init__` (line 136-146)
- Route SEARCH intent to SearchHandler (line 355-360)
- Route PROPERTY_DETAIL intent to PropertyDetailHandler (line 369-375)
- Extract components from response_data (line 401)
- Pass components to OrchestrationResponse (line 407)

**Pattern:** Structured response with components array

---

### Frontend (Svelte/TypeScript)

#### 6. `frontend/open-webui/src/lib/styles/design-tokens.css` (NEW)
**Purpose:** OpenAI Apps SDK design tokens from Figma

**Includes:**
- Colors: System colors (light/dark mode)
- Spacing: Grid-based (4px base unit)
- Typography: Font families, sizes, weights
- Component dimensions: Card (361x336px), Compact (400px max)
- Shadows, transitions, z-index layers

**Lines:** 300+
**Source:** Figma file 4JSHQqDBBms4mAvprmbN2b

#### 7. `frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte` (NEW)
**Purpose:** OpenAI-compliant compact property card

**Features:**
- 4 data points: Title, Location + Key Feature, Price
- 1 CTA: "Xem chi tiết →"
- 60x60px thumbnail
- 400px max-width
- System colors only (brand color ONLY on CTA button)

**Lines:** 244
**Compliance:** OpenAI "Simple" principle

#### 8. `frontend/open-webui/src/lib/components/property/PropertyDetailModal.svelte` (NEW)
**Purpose:** Modal wrapper for PropertyInspector

**Features:**
- Full-screen backdrop with fade transition
- Centered modal container (480px max-width, 80vh max-height)
- Close methods: ESC key, backdrop click, close button
- Contains PropertyInspector component

**Lines:** 239
**Pattern:** OpenAI Inspector (🔎)

#### 9. `frontend/open-webui/src/lib/components/chat/StructuredResponseRenderer.svelte` (NEW)
**Purpose:** Parse and render structured response components

**Features:**
- Renders property-carousel as CompactPropertyCard list
- Renders property-inspector as PropertyDetailModal
- Handles click events → dispatches requestDetail event
- Auto-opens modal for inspector components

**Lines:** 170
**Pattern:** Component renderer with event handling

#### 10. `frontend/open-webui/src/lib/components/chat/Messages/ResponseMessage.svelte` (MODIFIED)
**Purpose:** Support structured response rendering

**Changes:**
- Import StructuredResponseRenderer (line 63)
- Add components field to MessageType interface (line 115-118)
- Render StructuredResponseRenderer if components exist (line 810-817)
- Add handlePropertyDetailRequest handler (line 282-292)

**Pattern:** Conditional rendering based on message.components

#### 11. `frontend/open-webui/src/lib/apis/ree-ai/orchestrator.ts` (MODIFIED)
**Purpose:** TypeScript interface for structured response

**Change:** Add components field to OrchestratorResponse interface

```typescript
export interface OrchestratorResponse {
    intent: string;
    response: string;
    components?: Array<{    // NEW
        type: string;
        data: any;
    }>;
}
```

**Lines:** 64 (total)

---

## Data Flow Example

### Search Flow

1. **User Query:** "tìm căn hộ 2 phòng ngủ quận 1"

2. **Orchestrator → SearchHandler:**
```python
response_data = await self.search_handler.handle(
    query="tìm căn hộ 2 phòng ngủ quận 1",
    history=[],
    language="vi"
)
# Returns:
{
    "message": "Tìm thấy 5 căn hộ 2 phòng ngủ tại Quận 1",
    "components": [{
        "type": "property-carousel",
        "data": {
            "properties": [
                {
                    "id": "prop_123",
                    "title": "Căn hộ Vinhomes Central Park",
                    "address": "Quận 1, TP.HCM",
                    "price": "5 tỷ",
                    "bedrooms": 2,
                    "area": 75,
                    "imageUrl": "..."
                },
                ...
            ],
            "total": 5
        }
    }]
}
```

3. **Frontend Rendering:**
```svelte
<!-- ResponseMessage.svelte detects components -->
{#if message.components && message.components.length > 0}
    <StructuredResponseRenderer
        components={message.components}
        on:requestDetail={handlePropertyDetailRequest}
    />
{/if}

<!-- StructuredResponseRenderer renders cards -->
{#each carouselData.properties as property}
    <CompactPropertyCard
        {property}
        onClick={() => handlePropertyClick(property)}
    />
{/each}
```

### Detail Flow (Click on Card)

1. **User Action:** Click "Xem chi tiết →" on CompactPropertyCard

2. **Event Flow:**
```javascript
// CompactPropertyCard dispatches click
handleClick() → onClick(property)

// StructuredResponseRenderer dispatches requestDetail
dispatch('requestDetail', {
    propertyId: property.id,
    query: `cho tôi xem chi tiết thông tin căn nhà ${property.id}`
})

// ResponseMessage submits message
handlePropertyDetailRequest(event) → submitMessage(query)
```

3. **Orchestrator → PropertyDetailHandler:**
```python
response_data = await self.property_detail_handler.handle(
    query="cho tôi xem chi tiết thông tin căn nhà prop_123",
    history=[...],
    language="vi"
)
# Returns:
{
    "message": "Đang hiển thị chi tiết bất động sản",
    "components": [{
        "type": "property-inspector",
        "data": {
            "property_data": {
                "id": "prop_123",
                "title": "Căn hộ Vinhomes Central Park",
                "address": "Quận 1, TP.HCM",
                "price": "5 tỷ",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 75,
                "description": "...",
                "amenities": [...],
                "images": [...]
            }
        }
    }]
}
```

4. **Frontend Modal Display:**
```svelte
<!-- StructuredResponseRenderer detects inspector -->
{#if component.type === 'property-inspector'}
    {renderPropertyInspector(component)}  <!-- Opens modal -->
{/if}

<!-- PropertyDetailModal shows PropertyInspector -->
<PropertyDetailModal
    property={selectedProperty}
    bind:open={modalOpen}
    on:close={handleModalClose}
/>
```

---

## Testing Checklist

### ✅ Backend Tests

- [ ] **SearchHandler returns structured response**
  - Query: "tìm căn hộ 2pn quận 1"
  - Verify: response contains `{message, components}`
  - Verify: components[0].type == "property-carousel"
  - Verify: components[0].data.properties is array

- [ ] **PropertyDetailHandler extracts property reference**
  - By ID: "chi tiết căn prop_123"
  - By keyword: "chi tiết Vinhomes Central Park"
  - By position: "xem căn số 2"
  - Verify: correct property_id extracted

- [ ] **PropertyDetailHandler returns inspector component**
  - Verify: components[0].type == "property-inspector"
  - Verify: components[0].data.property_data contains full property info

### ✅ Frontend Tests

- [ ] **CompactPropertyCard renders correctly**
  - Verify: Displays title, location, price, key feature
  - Verify: CTA button uses brand color (#3b82f6)
  - Verify: onClick handler fires when clicked
  - Verify: 60x60px thumbnail size
  - Verify: 400px max-width

- [ ] **PropertyDetailModal functionality**
  - Verify: Opens when property_inspector component received
  - Verify: ESC key closes modal
  - Verify: Backdrop click closes modal
  - Verify: Close button works
  - Verify: PropertyInspector displays inside modal
  - Verify: Dark mode styles apply correctly

- [ ] **StructuredResponseRenderer integration**
  - Verify: Detects property-carousel component
  - Verify: Renders CompactPropertyCard list
  - Verify: Click on card dispatches requestDetail event
  - Verify: property-inspector auto-opens modal

### ✅ End-to-End Tests

- [ ] **Search → Click → Detail flow**
  1. User sends search query
  2. Search results display as card list
  3. User clicks "Xem chi tiết →" on a card
  4. New query sent to orchestrator
  5. PropertyDetailModal opens with full property info
  6. User can close modal and return to list

- [ ] **Dark mode consistency**
  - Verify: All components apply dark mode styles
  - Verify: Color contrast meets WCAG AA

- [ ] **Mobile responsiveness**
  - Verify: CompactPropertyCard adapts to small screens
  - Verify: PropertyDetailModal goes full-screen on mobile

---

## Deployment Notes

### Environment Variables
No new environment variables needed. Uses existing service URLs:
- `ORCHESTRATOR_URL`: http://orchestrator:8080
- `DB_GATEWAY_URL`: http://db-gateway:8080
- `RAG_SERVICE_URL`: http://rag-service:8080

### Service Dependencies
- **Orchestrator** must be running with new handlers
- **DB Gateway** must support `/properties/{id}` endpoint
- **RAG Service** must return full property data

### Build Requirements
1. **Backend:** Python 3.11+, dependencies in `requirements.txt`
2. **Frontend:** Node.js 18+, SvelteKit
3. **Build command:** `npm run build` (frontend)

---

## Commits

1. `48eb6d8` - feat: Add PropertyDetailModal with OpenAI Inspector pattern
2. `ecf8516` - feat: Integrate structured response components into orchestrator and frontend
3. `4dfac37` - feat: Add components field to OrchestratorResponse TypeScript interface

**Total commits:** 3
**Branch:** `claude/add-card-components-01Fc9vYQTsScqqEPN2aRZ2r6`

---

## Next Steps

1. **Testing:** Run end-to-end tests with real orchestrator
2. **Deployment:** Deploy to staging environment
3. **User Acceptance:** Test with actual user queries
4. **Monitoring:** Add logging for component rendering
5. **Optimization:** Cache property data, lazy load images

---

## References

- **Design Tokens:** `docs/design/DESIGN_TOKENS.md`
- **OpenAI Mapping:** `docs/design/OPENAI_APPS_SDK_MAPPING.md`
- **Figma File:** Apps in ChatGPT • Components & Templates (4JSHQqDBBms4mAvprmbN2b)
- **CTO Requirements:** Original design specification in `docs/design/`

---

**Status:** ✅ Ready for Testing
**Last Updated:** 2025-11-22
**Implemented By:** Claude (AI Assistant)
