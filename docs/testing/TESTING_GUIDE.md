# Testing Guide - Structured Response Implementation

**Last Updated:** 2025-11-22
**Branch:** `claude/add-card-components-01Fc9vYQTsScqqEPN2aRZ2r6`

---

## Quick Start

### 1. Build and Deploy Services

```bash
# Build all services
docker-compose build orchestrator

# Start services
docker-compose up -d orchestrator db-gateway rag-service classification

# Check health
curl http://localhost:8080/health
```

### 2. Test Backend - Search Handler

**Request:**
```bash
curl -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query": "tìm căn hộ 2 phòng ngủ quận 1",
    "language": "vi"
  }'
```

**Expected Response:**
```json
{
  "intent": "search",
  "confidence": 0.9,
  "response": "Tìm thấy 5 căn hộ 2 phòng ngủ tại Quận 1",
  "components": [
    {
      "type": "property-carousel",
      "data": {
        "properties": [
          {
            "id": "prop_123",
            "title": "Căn hộ Vinhomes Central Park",
            "address": "Quận 1, TP.HCM",
            "price": "5 tỷ",
            "priceUnit": "VNĐ",
            "bedrooms": 2,
            "area": 75,
            "imageUrl": "https://..."
          }
        ],
        "total": 5
      }
    }
  ],
  "service_used": "classification_routing_with_memory_multimodal",
  "execution_time_ms": 1234.56
}
```

**Verification Checklist:**
- [ ] `intent` is "search"
- [ ] `response` contains Vietnamese text
- [ ] `components` is an array with 1 element
- [ ] `components[0].type` is "property-carousel"
- [ ] `components[0].data.properties` is an array
- [ ] Each property has: id, title, address, price, imageUrl

### 3. Test Backend - Property Detail Handler

**Request (By ID):**
```bash
curl -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query": "cho tôi xem chi tiết thông tin căn nhà prop_123",
    "language": "vi"
  }'
```

**Expected Response:**
```json
{
  "intent": "property_detail",
  "confidence": 0.9,
  "response": "Đang hiển thị chi tiết bất động sản",
  "components": [
    {
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
    }
  ],
  "service_used": "classification_routing_with_memory_multimodal",
  "execution_time_ms": 567.89
}
```

**Verification Checklist:**
- [ ] `intent` is "property_detail"
- [ ] `components[0].type` is "property-inspector"
- [ ] `components[0].data.property_data` contains full property info
- [ ] property_data includes: description, amenities, images

**Request (By Keyword):**
```bash
curl -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query": "xem thông tin về Vinhomes Central Park",
    "language": "vi"
  }'
```

**Request (By Position - requires conversation history):**
```bash
# First search
curl -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "conversation_id": "test-conv-1",
    "query": "tìm căn hộ quận 1",
    "language": "vi"
  }'

# Then request by position
curl -X POST http://localhost:8080/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "conversation_id": "test-conv-1",
    "query": "xem căn số 2",
    "language": "vi",
    "metadata": {
      "from_open_webui": true,
      "conversation_history": [
        {"role": "user", "content": "tìm căn hộ quận 1"},
        {"role": "assistant", "content": "..."}
      ]
    }
  }'
```

### 4. Test Frontend Components

**Open WebUI Development Server:**
```bash
cd frontend/open-webui
npm install
npm run dev
```

**Access:** http://localhost:5173

**Manual Testing Steps:**

#### 4.1 CompactPropertyCard Component

**Test File:** Create test page at `src/routes/test/property-card.svelte`

```svelte
<script>
  import CompactPropertyCard from '$lib/components/property/CompactPropertyCard.svelte';

  const testProperty = {
    id: 'prop_123',
    title: 'Căn hộ Vinhomes Central Park',
    address: 'Quận 1, TP.HCM',
    price: '5 tỷ',
    priceUnit: 'VNĐ',
    bedrooms: 2,
    area: 75,
    imageUrl: 'https://via.placeholder.com/60'
  };

  function handleClick(property) {
    console.log('Property clicked:', property);
    alert(`Clicked: ${property.title}`);
  }
</script>

<div style="padding: 20px; max-width: 600px;">
  <h1>CompactPropertyCard Test</h1>

  <h2>With Image</h2>
  <CompactPropertyCard property={testProperty} onClick={handleClick} />

  <h2 style="margin-top: 40px;">Without Image</h2>
  <CompactPropertyCard
    property={{...testProperty, imageUrl: null}}
    onClick={handleClick}
  />

  <h2 style="margin-top: 40px;">No Bedrooms (Land)</h2>
  <CompactPropertyCard
    property={{...testProperty, bedrooms: 0, area: 200}}
    onClick={handleClick}
  />
</div>
```

**Verification Checklist:**
- [ ] Card renders with 60x60px thumbnail
- [ ] Title displays and truncates if too long
- [ ] Location shows with pin emoji (📍)
- [ ] Key feature shows "2PN 75m²" format
- [ ] Price displays in bold
- [ ] CTA button is blue (#3b82f6)
- [ ] Hover changes border color
- [ ] Click triggers onClick handler
- [ ] Placeholder icon shows when no image
- [ ] Dark mode styles apply correctly

#### 4.2 PropertyDetailModal Component

**Test File:** Create `src/routes/test/property-modal.svelte`

```svelte
<script>
  import PropertyDetailModal from '$lib/components/property/PropertyDetailModal.svelte';

  let modalOpen = false;

  const testProperty = {
    id: 'prop_123',
    title: 'Căn hộ Vinhomes Central Park',
    address: '208 Nguyễn Hữu Cảnh, Quận 1, TP.HCM',
    price: '5 tỷ',
    priceUnit: 'VNĐ',
    bedrooms: 2,
    bathrooms: 2,
    area: 75,
    description: 'Căn hộ cao cấp tại Vinhomes Central Park...',
    amenities: ['Hồ bơi', 'Gym', 'Công viên'],
    images: [
      'https://via.placeholder.com/400x300',
      'https://via.placeholder.com/400x300'
    ]
  };
</script>

<div style="padding: 20px;">
  <h1>PropertyDetailModal Test</h1>
  <button on:click={() => modalOpen = true}>
    Open Property Detail Modal
  </button>

  <PropertyDetailModal
    property={testProperty}
    bind:open={modalOpen}
    on:close={() => console.log('Modal closed')}
  />
</div>
```

**Verification Checklist:**
- [ ] Modal opens when button clicked
- [ ] Backdrop is semi-transparent black
- [ ] Modal centered on screen
- [ ] Max-width 480px
- [ ] Max-height 80vh
- [ ] PropertyInspector component renders inside
- [ ] Close button (X) works
- [ ] ESC key closes modal
- [ ] Backdrop click closes modal
- [ ] Fade transition on open/close
- [ ] Scrollbar shows if content overflows
- [ ] Mobile: Full-screen on small screens

#### 4.3 StructuredResponseRenderer Component

**Test File:** Create `src/routes/test/structured-response.svelte`

```svelte
<script>
  import StructuredResponseRenderer from '$lib/components/chat/StructuredResponseRenderer.svelte';

  const carouselComponents = [
    {
      type: 'property-carousel',
      data: {
        properties: [
          {
            id: 'prop_1',
            title: 'Căn hộ Vinhomes Central Park',
            address: 'Quận 1, TP.HCM',
            price: '5 tỷ',
            priceUnit: 'VNĐ',
            bedrooms: 2,
            area: 75,
            imageUrl: 'https://via.placeholder.com/60'
          },
          {
            id: 'prop_2',
            title: 'Căn hộ Masteri Thảo Điền',
            address: 'Quận 2, TP.HCM',
            price: '4.5 tỷ',
            priceUnit: 'VNĐ',
            bedrooms: 2,
            area: 70,
            imageUrl: 'https://via.placeholder.com/60'
          }
        ],
        total: 2
      }
    }
  ];

  const inspectorComponents = [
    {
      type: 'property-inspector',
      data: {
        property_data: {
          id: 'prop_1',
          title: 'Căn hộ Vinhomes Central Park',
          address: '208 Nguyễn Hữu Cảnh, Quận 1, TP.HCM',
          price: '5 tỷ',
          bedrooms: 2,
          bathrooms: 2,
          area: 75,
          description: 'Căn hộ cao cấp...'
        }
      }
    }
  ];

  function handleRequestDetail(event) {
    console.log('Detail requested:', event.detail);
    alert(`Requesting detail for property: ${event.detail.propertyId}`);
  }
</script>

<div style="padding: 20px;">
  <h1>StructuredResponseRenderer Test</h1>

  <h2>Property Carousel</h2>
  <StructuredResponseRenderer
    components={carouselComponents}
    on:requestDetail={handleRequestDetail}
  />

  <h2 style="margin-top: 60px;">Property Inspector (Opens Modal)</h2>
  <button on:click={() => {
    // Trigger inspector rendering
    inspectorComponents = [...inspectorComponents];
  }}>
    Render Property Inspector
  </button>
  <StructuredResponseRenderer components={inspectorComponents} />
</div>
```

**Verification Checklist:**
- [ ] Property carousel renders card list
- [ ] Result count displays: "Tìm thấy X bất động sản"
- [ ] Each card is clickable
- [ ] Click dispatches requestDetail event
- [ ] Inspector component auto-opens modal
- [ ] Empty state shows when no properties

### 5. End-to-End Testing

**Prerequisites:**
- All services running (orchestrator, db-gateway, rag-service)
- Open WebUI running
- Database seeded with test properties

**Test Scenario 1: Search → Click → Detail**

1. **Open Chat:** Navigate to Open WebUI chat interface
2. **Send Search Query:** "tìm căn hộ 2 phòng ngủ quận 1"
3. **Verify Search Results:**
   - Text response appears
   - Property cards render below text
   - Cards show: title, location, price, bedrooms, area
   - Blue "Xem chi tiết →" button visible
4. **Click Property Card:**
   - Click "Xem chi tiết →" on first card
5. **Verify Detail Request:**
   - New message sent automatically
   - Loading indicator shows
6. **Verify Detail Modal:**
   - PropertyDetailModal opens
   - Shows full property information
   - Images, amenities, description visible
7. **Close Modal:**
   - Click close button (or ESC or backdrop)
   - Modal closes
   - Property list still visible

**Test Scenario 2: Chat Detail Request (By ID)**

1. **Send Query:** "cho tôi xem chi tiết thông tin căn nhà prop_123"
2. **Verify:**
   - PropertyDetailModal opens automatically
   - Shows property with ID prop_123
   - No card list displayed

**Test Scenario 3: Chat Detail Request (By Keyword)**

1. **Send Query:** "xem thông tin về Vinhomes Central Park"
2. **Verify:**
   - System finds property by keyword
   - PropertyDetailModal opens
   - Shows correct property

**Test Scenario 4: Position-based Detail (Conversation Context)**

1. **Send Query 1:** "tìm căn hộ quận 1"
2. **Verify:** Property cards display
3. **Send Query 2:** "xem căn số 2"
4. **Verify:**
   - System extracts "2nd property" from conversation
   - PropertyDetailModal opens for 2nd property

### 6. Dark Mode Testing

**Steps:**
1. Enable dark mode in OS settings (or browser)
2. Refresh Open WebUI
3. Send search query
4. Verify dark mode styles:
   - Cards: `#212121` background, `#404040` border
   - Text: `#ffffff` primary, `#cdcdcd` secondary
   - Modal: `#212121` background
   - Buttons: Same blue brand color

### 7. Mobile Responsive Testing

**Device Sizes:**
- iPhone SE: 375x667
- iPhone 12: 390x844
- iPad: 768x1024

**Verification:**
- [ ] Cards stack vertically on mobile
- [ ] Thumbnail becomes full-width (150px height)
- [ ] CTA button becomes full-width
- [ ] Modal becomes full-screen (<768px)
- [ ] Text remains readable
- [ ] Touch targets ≥44px

### 8. Performance Testing

**Metrics to Monitor:**
- Backend response time: <2000ms
- Frontend render time: <100ms
- Image loading: Lazy load, <500ms
- Modal animation: Smooth 60fps

**Tools:**
- Chrome DevTools Performance tab
- Lighthouse audit
- Network tab for API calls

### 9. Error Handling

**Test Cases:**

1. **No Search Results:**
   - Query: "tìm căn hộ 100 tỷ quận 1000"
   - Expected: "Không tìm thấy bất động sản phù hợp"

2. **Invalid Property ID:**
   - Query: "xem chi tiết prop_invalid"
   - Expected: Error message, no modal

3. **Network Error:**
   - Disconnect network
   - Send query
   - Expected: Error toast, graceful degradation

4. **Malformed Component Data:**
   - Mock response with invalid component type
   - Expected: Console error, no crash

### 10. Accessibility (WCAG AA)

**Checklist:**
- [ ] Keyboard navigation works (Tab, Enter, ESC)
- [ ] Screen reader announces card content
- [ ] Focus visible outline (2px blue)
- [ ] Color contrast ≥4.5:1 (text)
- [ ] Color contrast ≥3:1 (UI components)
- [ ] ARIA labels on interactive elements
- [ ] Modal traps focus when open

**Tools:**
- axe DevTools
- WAVE browser extension
- Lighthouse accessibility audit

---

## Debugging Tips

### Backend Issues

**Check Logs:**
```bash
docker logs ree-ai-orchestrator -f --tail 100
```

**Common Issues:**
1. **Handler not found:** Check `services/orchestrator/handlers/__init__.py`
2. **Import error:** Verify all dependencies installed
3. **No components in response:** Check handler returns Dict with "components" key

### Frontend Issues

**Check Browser Console:**
- Open DevTools → Console
- Look for React/Svelte errors
- Check Network tab for API responses

**Common Issues:**
1. **Components not rendering:** Verify `message.components` exists
2. **Modal not opening:** Check `modalOpen` state binding
3. **Click not working:** Verify `onClick` prop passed correctly

### Integration Issues

**Verify Data Flow:**
```bash
# 1. Check orchestrator response
curl -X POST http://localhost:8080/orchestrate -H "Content-Type: application/json" -d '{"user_id":"test","query":"tìm nhà"}'

# 2. Check Open WebUI receives components
# Open Network tab in DevTools
# Send chat message
# Check /api/orchestrator/query response body
```

---

## Test Results Template

```markdown
## Test Results - [Date]

**Branch:** claude/add-card-components-01Fc9vYQTsScqqEPN2aRZ2r6
**Tester:** [Name]
**Environment:** [Development/Staging/Production]

### Backend Tests
- [ ] SearchHandler returns structured response: ✅/❌
- [ ] PropertyDetailHandler (by ID): ✅/❌
- [ ] PropertyDetailHandler (by keyword): ✅/❌
- [ ] PropertyDetailHandler (by position): ✅/❌

### Frontend Tests
- [ ] CompactPropertyCard renders: ✅/❌
- [ ] PropertyDetailModal opens/closes: ✅/❌
- [ ] StructuredResponseRenderer detects components: ✅/❌
- [ ] Dark mode works: ✅/❌
- [ ] Mobile responsive: ✅/❌

### End-to-End Tests
- [ ] Search → Click → Detail flow: ✅/❌
- [ ] Chat detail request (ID): ✅/❌
- [ ] Chat detail request (keyword): ✅/❌
- [ ] Position-based detail: ✅/❌

### Issues Found
1. [Description]
   - Severity: Critical/High/Medium/Low
   - Steps to reproduce:
   - Expected behavior:
   - Actual behavior:

### Screenshots
[Attach screenshots here]
```

---

**Next Steps After Testing:**
1. Fix any issues found
2. Update documentation with test results
3. Deploy to staging environment
4. User acceptance testing
5. Deploy to production
