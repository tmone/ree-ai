# OpenAI Apps SDK Component Mapping

**Reference:** Apps in ChatGPT • Components & Templates (Community)
**Figma FileKey:** `4JSHQqDBBms4mAvprmbN2b`
**URL:** https://www.figma.com/design/4JSHQqDBBms4mAvprmbN2b/UI

---

## 📦 Component Type Mapping

Mapping between OpenAI Apps SDK components (from Figma) and REE AI implementation:

| OpenAI SDK Component | REE AI Component Type | Backend Model | Frontend Component | Use Case |
|---------------------|----------------------|---------------|-------------------|----------|
| 🎠 **Inline Carousel** | `property-carousel` | `PropertyCarouselComponent` | `PropertySearchResults.svelte` | Search results list |
| 🔎 **Inspector** | `property-inspector` | `PropertyInspectorComponent` | `PropertyInspector.svelte` | Property detail view |
| ↕ **Full screen** | `property-fullscreen` | _(Future)_ | `FullscreenPropertyBrowser.svelte` | Browse many properties |
| 🔲 **PiP** | `property-pip` | _(Future)_ | `PiPFrame.svelte` | Picture-in-Picture |
| 🌁 **Inline Card** | _(Base components)_ | - | `Card.svelte`, `EntityCard.svelte` | Generic cards |

---

## 🎯 Implementation Details

### 1. Property Carousel (`property-carousel`)

**OpenAI Design:** 🎠 Inline Carousel
**CTO Requirement:** "kết quả tìm sẽ show dạng list, mỗi item chỉ chứa các thông tin cơ bản"

**Backend:**
```python
from shared.models.ui_components import PropertyCarouselComponent

component = PropertyCarouselComponent.create(
    properties=[
        {
            "id": "prop_123",
            "title": "Căn hộ 2PN quận 7",
            "address": "District 7, Ho Chi Minh City",
            "price": "2.5 tỷ",
            "area": "75",
            "imageUrl": "https://...",
            "bedrooms": 2,
            "bathrooms": 2,
            "propertyType": "apartment",
            "transactionType": "sale"
        },
        ...
    ],
    total=5
)
```

**Frontend Rendering:**
- Component: `PropertySearchResults.svelte`
- Uses: `Carousel.svelte` (OpenAI Apps SDK base)
- Displays: Horizontal scrollable carousel with 2-3 cards visible
- Navigation: Prev/Next buttons

---

### 2. Property Inspector (`property-inspector`)

**OpenAI Design:** 🔎 Inspector
**CTO Requirement:** "detail của bất động sản nên show dạng popup"

**Backend:**
```python
from shared.models.ui_components import PropertyInspectorComponent

component = PropertyInspectorComponent.create(
    property_data={
        "id": "prop_123",
        "title": "Căn hộ 2PN quận 7 Phú Mỹ Hưng",
        "address": "...",
        "price": "2,500,000,000",
        "area": 75,
        "bedrooms": 2,
        "bathrooms": 2,
        "images": ["url1", "url2", ...],
        "description": "...",
        "amenities": ["parking", "pool", "gym"],
        "contact": {
            "name": "Agent Name",
            "phone": "0901234567"
        }
    }
)
```

**Frontend Rendering:**
- Component: `PropertyInspector.svelte`
- Display: Modal/popup with full property details
- Features:
  - Image carousel (MediaCarousel)
  - Specs (bedrooms, bathrooms, area, etc.)
  - Amenities list
  - Contact info
  - Action buttons (Save, Share, Contact)

---

## 🔄 User Interaction Flow

### Search → Detail Flow (CTO Requirement)

```
User searches
    ↓
Backend: SearchHandler returns PropertyCarouselComponent
    ↓
Frontend: Renders PropertySearchResults (Carousel)
    ↓
User clicks property card
    ↓
Frontend: Sends request to backend for property detail
    ↓
Backend: PropertyDetailHandler returns PropertyInspectorComponent
    ↓
Frontend: Opens PropertyInspector in modal
    ↓
User can close modal and return to carousel
```

### 3 Ways to View Detail (CTO Requirement)

1. **By ID:** "cho tôi xem chi tiết thông tin căn nhà 456"
2. **By keyword:** "cho tôi xem thông tin căn nhà: Vinhomes Central Park"
3. **By click:** User clicks card in carousel

All 3 methods trigger `PROPERTY_DETAIL` intent → `PropertyInspectorComponent`

---

## 📐 Design Compliance

### OpenAI Apps SDK Design Guidelines

✅ **Followed:**
- Use Carousel for inline scrollable lists
- Use Inspector for detailed views
- Maintain visual consistency with OpenAI design system
- Support both light/dark modes
- Accessible (ARIA labels, keyboard navigation)

✅ **Typography:** Follow OpenAI font system
- Font family: `var(--font-sans)`
- Sizes: `--text-xs`, `--text-sm`, `--text-base`, `--text-xl`

✅ **Colors:** Follow OpenAI color system
- Brand primary: `var(--brand-primary)`
- Text: `var(--text-primary)`, `var(--text-secondary)`, `var(--text-tertiary)`
- Background: `var(--bg-primary)`, `var(--bg-secondary)`, `var(--bg-tertiary)`

✅ **Spacing:** Follow OpenAI spacing system
- `var(--space-1)` to `var(--space-16)`

---

## 🚀 Future Enhancements

Based on OpenAI Apps SDK components not yet implemented:

1. **Property Fullscreen (`property-fullscreen`)**
   - Full screen browser for >10 properties
   - Grid layout with filters
   - Already exists: `FullscreenPropertyBrowser.svelte`

2. **Property Map (`property-map`)**
   - Map view with property markers
   - Click marker → Inspector popup

3. **Property PiP (`property-pip`)**
   - Picture-in-Picture for property video tours

4. **Property Comparison (`property-comparison`)**
   - Side-by-side comparison of 2-3 properties

---

## 📚 References

- **Figma Design:** Apps in ChatGPT • Components & Templates
- **File:** `docs/design/Figma_page.md`
- **OpenAI Design Standards:** `docs/OPENAI_DESIGN_STANDARDS.md`
- **Frontend Components:** `frontend/open-webui/src/lib/components/apps-sdk/`
- **Backend Models:** `shared/models/ui_components.py`
