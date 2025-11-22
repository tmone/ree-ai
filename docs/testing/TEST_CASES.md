# Test Cases - Structured Response Components

**Last Updated:** 2025-11-22
**Status:** Unit Tests Complete, E2E Tests Pending

---

## 📋 Overview

This document catalogs all test cases for the Structured Response implementation. Tests cover backend handlers, frontend components, and end-to-end flows.

---

## 🎯 Test Coverage Summary

| Component | Unit Tests | Integration Tests | E2E Tests | Status |
|-----------|------------|-------------------|-----------|--------|
| **SearchHandler** | 10 | 2 | - | ✅ Complete |
| **PropertyDetailHandler** | 11 | 1 | - | ✅ Complete |
| **CompactPropertyCard** | 13 | 2 | - | ✅ Complete |
| **PropertyDetailModal** | 14 | 1 | Pending | ✅ Complete |
| **StructuredResponseRenderer** | 12 | 2 | Pending | ✅ Complete |
| **End-to-End Flows** | - | - | 4 | ⏳ Pending |

**Total Test Cases:** 64 defined, 60 implemented

---

## 🔧 Backend Tests

### SearchHandler Tests (`tests/backend/test_search_handler.py`)

**Location:** `tests/backend/test_search_handler.py`
**Framework:** pytest
**Dependencies:** pytest-asyncio, httpx

#### Test Cases

**TC-SH-001: Structured Response Format**
```python
async def test_search_handler_returns_structured_response()
```
- **Given:** Valid search query "tìm căn hộ 2PN quận 1"
- **When:** SearchHandler.handle() is called
- **Then:** Returns Dict with `message` and `components` keys
- **Assertions:**
  - Response is dict
  - Has "message" string field
  - Has "components" array field
  - Component type is "property-carousel"
  - Component has properties array and total count

**TC-SH-002: Property Formatting**
```python
async def test_search_handler_formats_properties_correctly()
```
- **Given:** RAG service returns properties
- **When:** SearchHandler formats for frontend
- **Then:** Each property has required fields
- **Assertions:**
  - id, title, address, price, imageUrl present
  - bedrooms or area present
  - All required types correct

**TC-SH-003: Empty Results**
```python
async def test_search_handler_empty_results()
```
- **Given:** Query with no matching properties
- **When:** SearchHandler processes empty results
- **Then:** Returns appropriate message
- **Assertions:**
  - Message indicates no results
  - Components empty or total = 0

**TC-SH-004: Price Formatting**
```python
async def test_search_handler_formats_price()
```
- **Given:** Numeric prices (e.g., 5000000000)
- **When:** Properties formatted
- **Then:** Prices readable (e.g., "5 tỷ")
- **Assertions:**
  - Price field present
  - Price not null

**TC-SH-005: Multilingual Support**
```python
async def test_search_handler_multilingual_support()
```
- **Given:** Different language parameters (vi, en, th, ja)
- **When:** Handler processes query
- **Then:** Response message in correct language
- **Assertions:**
  - Message string not empty
  - Language-appropriate response

**TC-SH-006: Error Handling**
```python
async def test_search_handler_handles_rag_service_error()
```
- **Given:** RAG service throws exception
- **When:** Handler attempts query
- **Then:** Exception raised or error handled
- **Assertions:**
  - Doesn't crash silently
  - Error properly propagated or handled

**TC-SH-007: Conversation History**
```python
async def test_search_handler_uses_conversation_history()
```
- **Given:** Previous conversation history provided
- **When:** Handler processes query
- **Then:** History used for context
- **Assertions:**
  - HTTP client called with proper parameters

**TC-SH-008: Component Data Validation**
```python
async def test_search_handler_component_data_validation()
```
- **Given:** SearchHandler returns component
- **When:** Component structure validated
- **Then:** All required fields present
- **Assertions:**
  - type and data fields present
  - properties array present
  - total is integer >= 0

**TC-SH-009: Various Query Types**
```python
@pytest.mark.parametrize("test_case", MOCK_SEARCH_QUERIES)
async def test_search_handler_various_queries()
```
- **Given:** Different search queries (căn hộ, cho thuê, mua đất)
- **When:** Handler processes each
- **Then:** Appropriate structured response
- **Assertions:**
  - Component count matches expected
  - Response format correct for all queries

**TC-SH-010: Performance**
```python
async def test_search_handler_performance()
```
- **Given:** Normal search query
- **When:** Handler executes
- **Then:** Completes within 2 seconds
- **Assertions:**
  - Execution time < 2.0 seconds
  - Result not null

---

### PropertyDetailHandler Tests (`tests/backend/test_property_detail_handler.py`)

**Location:** `tests/backend/test_property_detail_handler.py`
**Framework:** pytest
**Dependencies:** pytest-asyncio, httpx

#### Test Cases

**TC-PDH-001: Detail by Property ID**
```python
async def test_property_detail_by_id()
```
- **Given:** Query "cho tôi xem chi tiết thông tin căn nhà prop_123"
- **When:** PropertyDetailHandler extracts ID
- **Then:** Returns PropertyInspectorComponent with full data
- **Assertions:**
  - Component type is "property-inspector"
  - property_data contains all fields
  - ID matches requested property

**TC-PDH-002: ID Extraction Variants**
```python
async def test_property_detail_by_id_variants()
```
- **Given:** Various ID query formats
- **When:** Handler extracts property reference
- **Then:** Correctly identifies ID
- **Assertions:**
  - All query formats work
  - ID extracted correctly

**TC-PDH-003: Detail by Keyword**
```python
async def test_property_detail_by_keyword()
```
- **Given:** Query "xem thông tin về Vinhomes Central Park"
- **When:** Handler searches by keyword
- **Then:** Returns matching property detail
- **Assertions:**
  - Search performed
  - Correct property returned
  - Component type correct

**TC-PDH-004: Detail by Position**
```python
async def test_property_detail_by_position()
```
- **Given:** History with search results, query "xem căn số 2"
- **When:** Handler extracts position
- **Then:** Returns 2nd property from history
- **Assertions:**
  - Position extracted correctly
  - Correct property fetched

**TC-PDH-005: Property Not Found**
```python
async def test_property_detail_not_found()
```
- **Given:** Invalid property ID
- **When:** DB Gateway returns 404
- **Then:** Error handled gracefully
- **Assertions:**
  - No crash
  - Error message or empty result

**TC-PDH-006: Component Structure**
```python
async def test_property_detail_component_structure()
```
- **Given:** Successful property fetch
- **When:** Component created
- **Then:** Has all required fields
- **Assertions:**
  - Required: id, title, address, price
  - Detail: description, amenities, images

**TC-PDH-007: Multilingual Support**
```python
async def test_property_detail_multilingual()
```
- **Given:** Different language parameters
- **When:** Handler processes detail request
- **Then:** Message in correct language
- **Assertions:**
  - Message not empty
  - Language-appropriate

**TC-PDH-008: Images Handling**
```python
async def test_property_detail_images_handling()
```
- **Given:** Property with multiple images
- **When:** Data formatted
- **Then:** All images included
- **Assertions:**
  - images array present
  - All URLs valid strings

**TC-PDH-009: Amenities Handling**
```python
async def test_property_detail_amenities_handling()
```
- **Given:** Property with amenities
- **When:** Data formatted
- **Then:** Amenities array included
- **Assertions:**
  - amenities array present
  - All items are strings

**TC-PDH-010: Price Formatting**
```python
async def test_property_detail_price_formatting()
```
- **Given:** Numeric price
- **When:** Data formatted
- **Then:** Price readable
- **Assertions:**
  - price present
  - priceUnit present
  - Price not null

**TC-PDH-011: Extraction Methods**
```python
@pytest.mark.parametrize("test_case", MOCK_DETAIL_QUERIES)
async def test_property_detail_extraction_methods()
```
- **Given:** Queries using ID, keyword, position
- **When:** Handler extracts reference
- **Then:** Uses correct method
- **Assertions:**
  - ID extraction works
  - Keyword search works
  - Position extraction works

---

## 🎨 Frontend Tests

### CompactPropertyCard Tests (`tests/frontend/CompactPropertyCard.test.ts`)

**Location:** `tests/frontend/CompactPropertyCard.test.ts`
**Framework:** Vitest + @testing-library/svelte
**Dependencies:** vitest, @testing-library/svelte, @testing-library/jest-dom

#### Test Cases

**TC-CPC-001: Rendering Complete Data**
```typescript
it('should render property card with all data points')
```
- **Given:** Property with all fields
- **When:** Component rendered
- **Then:** All data points displayed
- **Assertions:**
  - Title visible
  - Price visible
  - CTA button visible

**TC-CPC-002: Image Display**
```typescript
it('should display property image when imageUrl is provided')
```
- **Given:** Property with imageUrl
- **When:** Component rendered
- **Then:** Image displayed
- **Assertions:**
  - img element present
  - src attribute correct
  - alt text present

**TC-CPC-003: Placeholder Image**
```typescript
it('should display placeholder when imageUrl is not provided')
```
- **Given:** Property without imageUrl
- **When:** Component rendered
- **Then:** Placeholder shown
- **Assertions:**
  - Placeholder div present
  - SVG icon present

**TC-CPC-004: Key Feature (Bedrooms + Area)**
```typescript
it('should format key feature with bedrooms and area')
```
- **Given:** Property with bedrooms and area
- **When:** Component formats feature
- **Then:** Shows "2PN 75m²"
- **Assertions:**
  - Format correct
  - Units included

**TC-CPC-005: Key Feature (Land)**
```typescript
it('should format key feature without bedrooms (land)')
```
- **Given:** Property with 0 bedrooms (land)
- **When:** Component formats feature
- **Then:** Shows area only
- **Assertions:**
  - "200m²" displayed
  - "0PN" not displayed

**TC-CPC-006: Card Click Handler**
```typescript
it('should call onClick handler when card is clicked')
```
- **Given:** Component with onClick prop
- **When:** Card clicked
- **Then:** onClick called with property
- **Assertions:**
  - Handler called
  - Correct property passed

**TC-CPC-007: CTA Click Handler**
```typescript
it('should call onClick when CTA button is clicked')
```
- **Given:** Component with onClick
- **When:** CTA button clicked
- **Then:** onClick called
- **Assertions:**
  - Handler called
  - Event propagates correctly

**TC-CPC-008: No onClick Graceful**
```typescript
it('should not crash when onClick is not provided')
```
- **Given:** Component without onClick
- **When:** Card clicked
- **Then:** No error thrown
- **Assertions:**
  - No exceptions
  - Component stable

**TC-CPC-009: Keyboard Navigation**
```typescript
it('should handle Enter key press')
```
- **Given:** Component with onClick
- **When:** Enter key pressed
- **Then:** onClick called
- **Assertions:**
  - Keyboard event handled
  - Handler called

**TC-CPC-010: ARIA Attributes**
```typescript
it('should have proper ARIA attributes')
```
- **Given:** Rendered component
- **When:** DOM inspected
- **Then:** ARIA attributes present
- **Assertions:**
  - role="button"
  - tabindex="0"
  - aria-label present

**TC-CPC-011: Screen Reader Labels**
```typescript
it('should have screen reader only labels')
```
- **Given:** Rendered component
- **When:** DOM inspected
- **Then:** sr-only elements present
- **Assertions:**
  - Location label
  - Price label

**TC-CPC-012: CSS Classes**
```typescript
it('should have correct CSS classes')
```
- **Given:** Rendered component
- **When:** DOM inspected
- **Then:** All classes present
- **Assertions:**
  - .compact-property-card
  - .thumbnail
  - .content
  - .title
  - .metadata
  - .price
  - .cta-button

**TC-CPC-013: OpenAI Compliance**
```typescript
it('should have maximum 4 data points')
```
- **Given:** Component design
- **When:** Rendered
- **Then:** 4 data points + 1 CTA
- **Assertions:**
  - Title (1)
  - Location + Feature (2)
  - Price (3)
  - CTA (action)

---

### PropertyDetailModal Tests (`tests/frontend/PropertyDetailModal.test.ts`)

**Location:** `tests/frontend/PropertyDetailModal.test.ts`
**Framework:** Vitest + @testing-library/svelte
**Component:** `frontend/open-webui/src/lib/components/property/PropertyDetailModal.svelte`

#### Test Cases

**TC-PDM-001: Modal Not Rendered When Closed**
```typescript
it('should not render modal when open is false')
```
- **Given:** Component with open=false
- **When:** Component rendered
- **Then:** Modal overlay not in DOM
- **Assertions:**
  - `.modal-overlay` not present

**TC-PDM-002: Modal Rendered When Open**
```typescript
it('should render modal when open is true')
```
- **Given:** Component with open=true
- **When:** Component rendered
- **Then:** Modal visible with property details
- **Assertions:**
  - role="dialog" present
  - Property title displayed

**TC-PDM-003: Close Button Click**
```typescript
it('should close modal when close button is clicked')
```
- **Given:** Open modal
- **When:** Close button clicked
- **Then:** 'close' event dispatched
- **Assertions:**
  - Event handler called once

**TC-PDM-004: ESC Key Close**
```typescript
it('should close modal when ESC key is pressed')
```
- **Given:** Open modal
- **When:** ESC key pressed
- **Then:** 'close' event dispatched
- **Assertions:**
  - Keyboard handler called
  - Event dispatched

**TC-PDM-005: Backdrop Click Close**
```typescript
it('should close modal when clicking backdrop')
```
- **Given:** Open modal
- **When:** Overlay clicked
- **Then:** Modal closes
- **Assertions:**
  - 'close' event dispatched

**TC-PDM-006: Content Click Prevention**
```typescript
it('should not close modal when clicking modal content')
```
- **Given:** Open modal
- **When:** Modal content clicked
- **Then:** Modal stays open (stopPropagation)
- **Assertions:**
  - 'close' event NOT dispatched

**TC-PDM-007: ARIA Attributes**
```typescript
it('should have proper ARIA attributes for accessibility')
```
- **Given:** Open modal
- **When:** DOM inspected
- **Then:** Accessibility attributes present
- **Assertions:**
  - aria-modal="true"
  - aria-labelledby present
  - Close button aria-label="Close modal"

**TC-PDM-008: Focus Trap**
```typescript
it('should trap focus within modal when open')
```
- **Given:** Open modal
- **When:** Tab key pressed
- **Then:** Focus stays within modal
- **Assertions:**
  - Focus cycles within modal container

**TC-PDM-009: Mobile Fullscreen**
```typescript
it('should apply fullscreen styles on mobile')
```
- **Given:** Mobile viewport (max-width: 480px)
- **When:** Modal rendered
- **Then:** Fullscreen styles applied
- **Assertions:**
  - width: 100%
  - height: 100%

**TC-PDM-010: Body Scroll Prevention**
```typescript
it('should prevent body scroll when modal is open')
```
- **Given:** Modal opens
- **When:** Modal state changes
- **Then:** Body scroll disabled
- **Assertions:**
  - document.body.style.overflow = "hidden" when open
  - Restored when closed

**TC-PDM-011: PropertyInspector Integration**
```typescript
it('should render PropertyInspector with correct property data')
```
- **Given:** Property data passed to modal
- **When:** Modal rendered
- **Then:** PropertyInspector displays all data
- **Assertions:**
  - Title, address, price, description displayed

**TC-PDM-012: Missing Data Handling**
```typescript
it('should handle missing optional property data gracefully')
```
- **Given:** Minimal property data (no features, contact, etc.)
- **When:** Modal rendered
- **Then:** No errors, basic data displayed
- **Assertions:**
  - No crashes
  - Required fields displayed

**TC-PDM-013: Z-Index**
```typescript
it('should have proper z-index for overlay')
```
- **Given:** Modal rendered
- **When:** Styles inspected
- **Then:** High z-index ensures visibility
- **Assertions:**
  - z-index ≥ 1000

**TC-PDM-014: System Colors (OpenAI Compliance)**
```typescript
it('should use system colors from design tokens')
```
- **Given:** Modal rendered
- **When:** Styles inspected
- **Then:** Uses --bg-primary, NOT brand color
- **Assertions:**
  - background: var(--bg-primary)
  - NOT #3b82f6 (brand color)

---

### StructuredResponseRenderer Tests (`tests/frontend/StructuredResponseRenderer.test.ts`)

**Location:** `tests/frontend/StructuredResponseRenderer.test.ts`
**Framework:** Vitest + @testing-library/svelte
**Component:** `frontend/open-webui/src/lib/components/chat/StructuredResponseRenderer.svelte`

#### Test Cases

**TC-SRR-001: Property Carousel Rendering**
```typescript
it('should render property carousel with multiple properties')
```
- **Given:** Components array with property-carousel type
- **When:** Component rendered
- **Then:** All properties displayed
- **Assertions:**
  - All property titles visible
  - All prices visible

**TC-SRR-002: Property Inspector Modal**
```typescript
it('should render property inspector in modal')
```
- **Given:** Components array with property-inspector type
- **When:** Component rendered
- **Then:** Modal opens with property details
- **Assertions:**
  - role="dialog" present
  - Property data displayed

**TC-SRR-003: Request Detail Event**
```typescript
it('should dispatch requestDetail event when property card is clicked')
```
- **Given:** Carousel with clickable properties
- **When:** Property card clicked
- **Then:** 'requestDetail' event dispatched
- **Assertions:**
  - Event contains propertyId
  - Event contains query string

**TC-SRR-004: Empty Components**
```typescript
it('should handle empty components array gracefully')
```
- **Given:** Empty components array
- **When:** Component rendered
- **Then:** No errors, nothing rendered
- **Assertions:**
  - No property list
  - No modal

**TC-SRR-005: Multiple Component Types**
```typescript
it('should render multiple component types in same response')
```
- **Given:** Carousel + Inspector in same components array
- **When:** Component rendered
- **Then:** Both render correctly
- **Assertions:**
  - Carousel properties visible
  - Modal opens with inspector

**TC-SRR-006: Unknown Component Types**
```typescript
it('should ignore unknown component types')
```
- **Given:** Components with unknown type
- **When:** Component rendered
- **Then:** Ignores unknown, renders valid ones
- **Assertions:**
  - No crashes
  - Valid components displayed

**TC-SRR-007: Modal Close Event**
```typescript
it('should close modal when PropertyDetailModal dispatches close event')
```
- **Given:** Open modal with inspector
- **When:** Close button clicked
- **Then:** Modal closes
- **Assertions:**
  - Modal removed from DOM

**TC-SRR-008: Total Count Display**
```typescript
it('should display total count for property carousel')
```
- **Given:** Carousel with total count
- **When:** Component rendered
- **Then:** Total count displayed (if implemented)
- **Assertions:**
  - Total count visible (optional)

**TC-SRR-009: Malformed Data Handling**
```typescript
it('should handle malformed component data without crashing')
```
- **Given:** Component with missing required fields
- **When:** Component rendered
- **Then:** No errors thrown
- **Assertions:**
  - Component stable
  - No crashes

**TC-SRR-010: Component Prop Updates**
```typescript
it('should update when components prop changes')
```
- **Given:** Initial components rendered
- **When:** Components prop updated
- **Then:** UI updates to show new components
- **Assertions:**
  - Old properties removed
  - New properties displayed

**TC-SRR-011: CompactPropertyCard Integration**
```typescript
it('should render CompactPropertyCard components in carousel')
```
- **Given:** Carousel with properties
- **When:** Component rendered
- **Then:** Uses CompactPropertyCard component
- **Assertions:**
  - .compact-property-card class present
  - Thumbnail image present
  - CTA button present

**TC-SRR-012: Keyboard Navigation**
```typescript
it('should support keyboard navigation in property carousel')
```
- **Given:** Carousel with multiple properties
- **When:** Enter key pressed on card
- **Then:** 'requestDetail' event dispatched
- **Assertions:**
  - Event contains correct propertyId
  - Keyboard events handled

---

## 🧪 Test Execution

### Running Tests

**Backend Tests:**
```bash
# All backend tests
pytest tests/backend/ -v

# Specific handler
pytest tests/backend/test_search_handler.py -v

# With coverage
pytest tests/backend/ --cov=services/orchestrator/handlers --cov-report=html
```

**Frontend Tests:**
```bash
# All frontend tests
npm run test

# Specific component
npm run test CompactPropertyCard

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

**End-to-End Tests:**
```bash
# All E2E tests
npm run test:e2e

# Specific flow
npm run test:e2e -- --grep "search to detail"

# With UI
npm run test:e2e:ui
```

---

## 📊 Test Data

### Mock Property Data

**Standard Property:**
```json
{
  "id": "prop_123",
  "title": "Căn hộ Vinhomes Central Park",
  "address": "Quận 1, TP.HCM",
  "price": 5000000000,
  "priceUnit": "VNĐ",
  "bedrooms": 2,
  "bathrooms": 2,
  "area": 75,
  "imageUrl": "https://example.com/image.jpg"
}
```

**Property with Full Details:**
```json
{
  "id": "prop_123",
  "title": "Căn hộ Vinhomes Central Park",
  "address": "208 Nguyễn Hữu Cảnh, Quận 1, TP.HCM",
  "price": 5000000000,
  "priceUnit": "VNĐ",
  "bedrooms": 2,
  "bathrooms": 2,
  "area": 75,
  "description": "Căn hộ cao cấp...",
  "amenities": ["Hồ bơi", "Gym", "Công viên"],
  "images": [
    "https://example.com/1.jpg",
    "https://example.com/2.jpg"
  ],
  "propertyType": "apartment",
  "listingType": "sale",
  "yearBuilt": 2020,
  "floor": 15
}
```

**Land Property (No Bedrooms):**
```json
{
  "id": "prop_land_1",
  "title": "Đất Bình Dương",
  "address": "Bình Dương",
  "price": 10000000000,
  "bedrooms": 0,
  "area": 200,
  "propertyType": "land"
}
```

---

## 🎯 Test Scenarios

### Scenario 1: Search → Click → Detail

**Steps:**
1. User searches: "tìm căn hộ 2PN quận 1"
2. SearchHandler returns PropertyCarouselComponent
3. Frontend renders CompactPropertyCard list
4. User clicks "Xem chi tiết →"
5. PropertyDetailHandler fetches detail
6. PropertyDetailModal opens with PropertyInspector

**Expected Results:**
- Search results display correctly
- Cards are clickable
- Detail request sent
- Modal opens with full data
- User can close modal

**Test Files:**
- Backend: `test_search_handler.py`, `test_property_detail_handler.py`
- Frontend: `CompactPropertyCard.test.ts`, `PropertyDetailModal.test.ts`
- E2E: `search-to-detail.spec.ts`

---

### Scenario 2: Chat Detail Request (By ID)

**Steps:**
1. User types: "cho tôi xem chi tiết prop_123"
2. PropertyDetailHandler extracts ID
3. Fetches property from DB Gateway
4. Returns PropertyInspectorComponent
5. Modal opens automatically

**Expected Results:**
- ID extracted correctly
- Property fetched
- Modal opens
- Full property details displayed

**Test Files:**
- Backend: `test_property_detail_handler.py` (TC-PDH-001, TC-PDH-002)
- E2E: `chat-detail-by-id.spec.ts`

---

### Scenario 3: Multilingual Support

**Steps:**
1. User switches language to English
2. Searches: "find apartments district 1"
3. System responds in English
4. Component labels in English

**Expected Results:**
- Response message in English
- Component text localized
- CTA button in English

**Test Files:**
- Backend: `test_search_handler.py` (TC-SH-005)
- Frontend: TBD (localization tests)

---

### Scenario 4: Error Handling

**Steps:**
1. User searches: "tìm căn hộ 100 tỷ"
2. No results found
3. System shows appropriate message
4. User searches invalid ID
5. Error handled gracefully

**Expected Results:**
- Empty state message shown
- No crash on errors
- User-friendly error messages

**Test Files:**
- Backend: `test_search_handler.py` (TC-SH-003, TC-SH-006)
- Backend: `test_property_detail_handler.py` (TC-PDH-005)

---

## ✅ Test Checklist

Before deployment, ensure:

### Backend
- [ ] All pytest tests pass
- [ ] Coverage ≥80%
- [ ] No skipped tests
- [ ] Error handling tested
- [ ] Edge cases covered

### Frontend
- [ ] All Vitest tests pass
- [ ] Coverage ≥80%
- [ ] Accessibility tests pass
- [ ] Dark mode tested
- [ ] Mobile responsive tested

### Integration
- [ ] API contracts verified
- [ ] Component integration tested
- [ ] Event handling works
- [ ] State management correct

### E2E
- [ ] Search flow works
- [ ] Detail flow works
- [ ] Error scenarios handled
- [ ] Performance acceptable

---

## 📝 Test Results Template

```markdown
## Test Run - [Date]

**Environment:** [Development/Staging/Production]
**Branch:** claude/add-card-components-01Fc9vYQTsScqqEPN2aRZ2r6

### Backend Tests
- Total: X
- Passed: Y
- Failed: Z
- Coverage: N%

### Frontend Tests
- Total: X
- Passed: Y
- Failed: Z
- Coverage: N%

### E2E Tests
- Total: X
- Passed: Y
- Failed: Z

### Issues Found
1. [Description]
   - Severity: Critical/High/Medium/Low
   - Assigned to: [Name]

### Sign-off
- [ ] QA Lead
- [ ] Tech Lead
- [ ] Product Owner
```

---

**Related Documents:**
- Testing Guide: `docs/testing/TESTING_GUIDE.md`
- Implementation: `docs/implementation/STRUCTURED_RESPONSE_IMPLEMENTATION.md`
- Components Spec: `docs/design/figma/COMPONENTS_REFERENCE.md`
