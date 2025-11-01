# REE AI - OpenAI Design Standards Implementation Guide

## Overview

This document outlines recommendations to upgrade REE AI's Open WebUI to meet OpenAI's official design guidelines and create a professional, publication-ready real estate AI assistant.

**Goal**: Transform REE AI into a best-in-class real estate AI application that:
- Meets OpenAI's design and quality standards for publication
- Provides professional, context-aware property search experiences
- Implements conversational UI patterns that feel natural and intelligent

---

## 📋 OpenAI Design Principles Analysis

Based on [OpenAI Apps SDK Design Guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines/), applications must embody **5 core principles**:

### 1. **Conversational** ✅
> "Experiences should feel like a natural extension of ChatGPT, fitting seamlessly into the conversational flow"

**Current State**: REE AI has basic chat integration but property search feels separate from conversation.

**Gap**: Property cards appear in isolation; no fluid transition between chat and property discovery.

### 2. **Intelligent** ⚠️
> "Tools remain aware of discussion context and anticipate user needs"

**Current State**: Orchestrator provides intent detection but lacks context persistence across sessions.

**Gap**: System doesn't remember user preferences (budget, location, property type) across conversations.

### 3. **Simple** ⚠️
> "Each interaction targets one clear action with minimal information density"

**Current State**: PropertyCard shows 6-8 data points per card (type, location, area, bedrooms, bathrooms, price, score).

**Gap**: Violates "one card, a few key details, a clear CTA" principle - too much information density.

### 4. **Responsive** ✅
> "Applications should feel fast and lightweight rather than intrusive"

**Current State**: PropertySearch component has good loading states and async handling.

**Gap**: Could improve perceived performance with skeleton loaders and progressive enhancement.

### 5. **Accessible** ❌
> "Designs must support users relying on assistive technologies"

**Current State**: No ARIA labels, semantic HTML issues, missing alt text on placeholder images.

**Gap**: PropertyCard uses `<button>` correctly but lacks screen reader support for price/stats.

---

## 🎯 OpenAI Use Case Validation

Applications must answer **affirmatively** to these questions:

| Question | REE AI Status | Notes |
|----------|---------------|-------|
| Does the task fit naturally into dialogue? | ✅ YES | Property search via natural language fits perfectly |
| Is it time-bound with clear endpoints? | ✅ YES | Search → Browse → Contact/Save |
| Can users act on information immediately? | ⚠️ PARTIAL | Missing clear CTAs (view details, contact agent, save) |
| Can it be represented simply ("one card, a few key details, a clear CTA")? | ❌ NO | Cards are overloaded with info |
| Does it extend ChatGPT distinctively? | ✅ YES | Real estate domain with RAG + OpenSearch is unique |

**Prohibited approaches to avoid**:
- ❌ Long-form static content (avoid property listing pages that feel like websites)
- ❌ Complicated multi-step workflows (current PropertySearch filters are borderline)
- ❌ Advertisements or upsells (ensure no promotional language in responses)

---

## 🎨 OpenAI Visual Design Standards

### Color Usage
**OpenAI Standard**: "Employ system-defined palettes for text and UI elements. Brand accents appear on primary buttons and badges only—never backgrounds."

**Current REE AI**:
```css
/* ❌ VIOLATION - Custom brand colors everywhere */
.property-type-badge {
  background: rgba(59, 130, 246, 0.9); /* Blue background */
}
.search-button {
  background: #3b82f6; /* Custom blue */
}
.property-price {
  color: #dc2626; /* Custom red */
}
```

**✅ Recommended Fix**:
```css
/* Use system colors with brand accent only on CTAs */
.property-type-badge {
  background: var(--gray-100); /* System gray */
  color: var(--gray-700);
}
.search-button {
  background: var(--brand-primary); /* Only on primary CTA */
}
.property-price {
  color: var(--text-primary); /* System text color */
  font-weight: 700; /* Emphasis through weight, not color */
}
```

### Typography
**OpenAI Standard**: "Inherit system fonts (SF Pro/Roboto); avoid custom typefaces entirely."

**Current REE AI**: ✅ Already using system fonts (no violations)

### Spacing & Layout
**OpenAI Standard**: "Apply consistent grid-based margins and padding"

**Current REE AI**: ✅ Good use of 12px/16px/24px grid system

### Icons
**OpenAI Standard**: "Use monochromatic, outlined iconography aligned with ChatGPT's aesthetic."

**Current REE AI**: ✅ Using Heroicons (outlined style) - good choice

---

## 🏠 Real Estate Domain Customization Recommendations

### Priority 1: Conversational Property Discovery (HIGH IMPACT)

**Problem**: PropertySearch feels like a traditional search form, not conversational AI.

**Solution**: Inline Property Cards in Chat

```typescript
// frontend/open-webui/src/lib/components/chat/Messages/ResponseMessage.svelte

interface PropertyResult {
  type: 'property_card';
  data: Property[];
}

// Detect property results in chat response
if (message.metadata?.property_results) {
  const properties = message.metadata.property_results;

  // Render inline cards
  <div class="inline-property-results">
    <p class="results-intro">Tôi tìm thấy {properties.length} bất động sản phù hợp:</p>

    <div class="property-carousel">
      {#each properties.slice(0, 3) as property}
        <CompactPropertyCard {property} />
      {/each}
    </div>

    {#if properties.length > 3}
      <button class="view-all-cta">Xem tất cả {properties.length} kết quả →</button>
    {/if}
  </div>
}
```

**Benefits**:
- ✅ Conversational: Cards appear naturally in chat flow
- ✅ Simple: Show max 3 cards inline, "View All" for more
- ✅ Intelligent: AI explains why these properties match

---

### Priority 2: Simplified Property Cards (HIGH IMPACT)

**Problem**: Current PropertyCard violates "one card, a few key details, a clear CTA" principle.

**Current (8 data points)**:
- Property type badge
- Title
- Location
- Area
- Bedrooms
- Bathrooms
- Price
- Score

**✅ Recommended: Compact Inline Card (4 data points + 1 CTA)**

```svelte
<!-- frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte -->

<script lang="ts">
  export let property: Property;

  // Show ONLY the most critical info
  const primaryInfo = {
    title: property.title,
    location: property.location,
    price: formatPrice(property.price),
    keyFeature: getKeyFeature(property) // "2PN 75m²" or "Đất 200m²"
  };

  // ONE clear CTA
  const ctaLabel = "Xem chi tiết";
</script>

<article class="compact-property-card">
  <!-- Image thumbnail (small) -->
  <img src={property.images[0]} alt={property.title} class="thumbnail" />

  <div class="content">
    <!-- Title (1 line max) -->
    <h4 class="title">{primaryInfo.title}</h4>

    <!-- Location + Key Feature (1 line) -->
    <p class="metadata">
      📍 {primaryInfo.location} • {primaryInfo.keyFeature}
    </p>

    <!-- Price (emphasized) -->
    <p class="price">{primaryInfo.price}</p>
  </div>

  <!-- ONE clear CTA -->
  <button class="cta-button" on:click={handleViewDetails}>
    {ctaLabel} →
  </button>
</article>

<style>
  .compact-property-card {
    display: flex;
    gap: 12px;
    padding: 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    align-items: center;
    max-width: 400px; /* Fit in chat */
  }

  .thumbnail {
    width: 60px;
    height: 60px;
    border-radius: 6px;
    object-fit: cover;
  }

  .content {
    flex: 1;
    min-width: 0; /* Allow text truncation */
  }

  .title {
    font-size: 14px;
    font-weight: 600;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .metadata {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 4px 0;
  }

  .price {
    font-size: 14px;
    font-weight: 700;
    margin: 0;
  }

  .cta-button {
    padding: 8px 16px;
    background: var(--brand-primary); /* Only place for brand color */
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
  }
</style>
```

**Before/After Comparison**:

| Metric | Current Card | Compact Card | Improvement |
|--------|--------------|--------------|-------------|
| Data points shown | 8 | 4 | -50% info density |
| Card height | 350px | 84px | Fits 4x more in viewport |
| CTAs | 0 | 1 | Clear next action |
| OpenAI compliance | ❌ No | ✅ Yes | Publication-ready |

---

### Priority 3: Context-Aware Smart Suggestions (MEDIUM IMPACT)

**Problem**: System doesn't learn from user behavior or proactively suggest.

**Solution**: Conversational Memory + Proactive Nudges

```typescript
// services/orchestrator/context_manager.py

class ConversationContext:
    """Track user preferences across sessions"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.preferences = {
            "budget_range": None,      # Auto-detected from queries
            "preferred_locations": [], # Track mentioned locations
            "property_types": [],      # Track interest patterns
            "key_features": []         # Must-haves (pool, garden, etc.)
        }

    def learn_from_query(self, query: str, results_clicked: list):
        """Extract preferences from user behavior"""

        # Budget detection
        if "dưới 5 tỷ" in query or "under 5 billion" in query:
            self.preferences["budget_range"] = (0, 5_000_000_000)

        # Location tracking
        locations = extract_locations(query)  # "Quận 1", "Thủ Đức"
        self.preferences["preferred_locations"].extend(locations)

        # Feature detection from clicks
        for prop in results_clicked:
            if prop.has_pool:
                self.preferences["key_features"].append("pool")

    def generate_proactive_suggestion(self) -> str:
        """OpenAI-compliant proactive nudge"""

        # ✅ ALLOWED: Contextual nudges tied to user intent
        if self.preferences["budget_range"] and len(self.preferences["preferred_locations"]) > 0:
            return f"Dựa trên lịch sử tìm kiếm của bạn ({self.preferences['preferred_locations'][0]}, dưới {format_price(self.preferences['budget_range'][1])}), tôi có thể gợi ý thêm các căn hộ mới đăng hôm nay."

        # ❌ FORBIDDEN: Unsolicited promotions
        # return "Check out our premium listings! Limited time offer!"

        return None
```

**Integration with Chat**:
```typescript
// frontend/open-webui/src/lib/components/chat/Chat.svelte

onMount(async () => {
  // Load user context
  const context = await loadUserContext(userId);

  // Show proactive suggestion ONLY if contextually relevant
  if (context.has_recent_searches && !context.shown_suggestion_today) {
    const suggestion = context.generate_suggestion();

    if (suggestion) {
      // Render as system message (not intrusive)
      addSystemMessage({
        type: 'suggestion',
        content: suggestion,
        dismissible: true
      });
    }
  }
});
```

**OpenAI Compliance**:
- ✅ **Proactivity boundaries**: Only surface contextual nudges tied to user intent
- ✅ **Transparency**: Clearly explain why suggestions appear
- ❌ **Forbidden**: Unsolicited promotions, re-engagement campaigns

---

### Priority 4: Display Mode Strategy (HIGH IMPACT)

**OpenAI Standard**: Choose appropriate display mode for each interaction.

#### **Inline Mode** (Default for property results)
Use for: Quick property cards in chat, single property lookups, comparisons

```svelte
<!-- Show 1-3 properties inline in conversation -->
<div class="inline-property-cards">
  {#each properties.slice(0, 3) as property}
    <CompactPropertyCard {property} />
  {/each}
</div>
```

#### **Fullscreen Mode** (For detailed browsing)
Use for: "View All Results", property comparison, map view

```svelte
<!-- Triggered by "Xem tất cả" CTA -->
<FullscreenPropertyBrowser
  properties={allResults}
  onClose={() => returnToChat()}
  maintainComposer={true} <!-- Keep chat composer visible -->
/>
```

**Key Requirement**: Maintain ChatGPT's composer overlay for continued dialogue (user can chat while browsing)

#### **Picture-in-Picture Mode** (Advanced feature)
Use for: Virtual property tours, live agent chat, mortgage calculator

```svelte
<!-- Floating calculator while chatting about properties -->
<PiPMortgageCalculator
  property={selectedProperty}
  position="bottom-right"
  collapsible={true}
/>
```

**Implementation Priority**:
1. ✅ Inline (implement now) - Core conversational UX
2. ⚠️ Fullscreen (implement soon) - Needed for browsing >3 results
3. 🔮 PiP (future) - Nice-to-have for advanced interactions

---

### Priority 5: Accessibility Compliance (HIGH IMPACT)

**OpenAI Standard**: "Maintain WCAG AA contrast ratios; include alt text for all images."

**Current Violations**:

```svelte
<!-- ❌ BEFORE: No alt text, no ARIA labels -->
<div class="placeholder-image">
  <svg>...</svg>  <!-- No aria-label -->
</div>

<div class="property-stats">
  <div class="stat">
    <span class="stat-label">Diện tích</span>
    <span class="stat-value">{formatArea(property.area)}</span>
  </div>
</div>
```

**✅ AFTER: WCAG AA Compliant**:

```svelte
<!-- ✅ Proper semantic HTML + ARIA -->
<div class="placeholder-image" role="img" aria-label="Hình ảnh bất động sản chưa có sẵn">
  <svg aria-hidden="true">...</svg>
</div>

<dl class="property-stats" aria-label="Thông số bất động sản">
  <div class="stat">
    <dt class="stat-label">Diện tích</dt>
    <dd class="stat-value">{formatArea(property.area)}</dd>
  </div>
</dl>

<!-- Price with semantic emphasis -->
<p class="property-price">
  <span class="sr-only">Giá:</span>
  <strong aria-label="{property.price.toLocaleString()} đồng Việt Nam">
    {formatPrice(property.price)} VNĐ
  </strong>
</p>
```

**Checklist**:
- [ ] Add ARIA labels to all interactive elements
- [ ] Use semantic HTML (`<dl>`, `<dt>`, `<dd>` for stats)
- [ ] Ensure 4.5:1 contrast ratio for text (use contrast checker)
- [ ] Add screen reader only text (`.sr-only` class) for context
- [ ] Test with VoiceOver (Mac) or NVDA (Windows)

---

### Priority 6: Communication Standards (CRITICAL)

**OpenAI Standard**: "Information must be concise, context-driven, and jargon-free. Marketing language is prohibited."

**❌ Bad Examples** (Avoid):
```typescript
// Marketing language - FORBIDDEN
"🔥 Căn hộ HOT nhất khu vực! SIÊU ƯU ĐÃI chỉ hôm nay!"
"Cơ hội VÀNG sở hữu BĐS đẳng cấp! Liên hệ NGAY!"
```

**✅ Good Examples** (Use):
```typescript
// Concise, context-driven, jargon-free
"Căn hộ này phù hợp với ngân sách dưới 5 tỷ của bạn và nằm gần trường quốc tế như bạn đã đề cập."

"Dựa trên yêu cầu 2 phòng ngủ tại Quận 7, tôi tìm thấy 12 lựa chọn. Sắp xếp theo giá tăng dần."
```

**Implementation in RAG Service**:

```python
# services/rag_service/prompt_templates.py

RESPONSE_SYSTEM_PROMPT = """
You are a professional real estate assistant for REE AI.

Communication Guidelines (OpenAI Compliance):
1. CONCISE: Keep responses under 3 sentences for property listings
2. CONTEXT-DRIVEN: Always reference user's stated preferences
3. JARGON-FREE: Use simple Vietnamese, avoid marketing buzzwords
4. NO MARKETING: Never use promotional language (🔥, HOT, SIÊU ƯU ĐÃI, etc.)
5. TRANSPARENT: Explain why you're suggesting these properties

Example:
User: "Tìm căn hộ 2 phòng ngủ Quận 1 dưới 5 tỷ"
Good: "Tôi tìm thấy 8 căn hộ 2 phòng ngủ tại Quận 1 trong khoảng giá của bạn. Căn hộ đầu tiên (3.2 tỷ, 75m²) gần trường quốc tế."
Bad: "🔥 SIÊU HOT! 8 căn hộ ĐẲNG CẤP chỉ từ 3.2 tỷ! CƠ HỘI VÀNG!"
"""
```

---

## 🚀 Implementation Roadmap

### Phase 1: OpenAI Standards Compliance (Week 1-2)
**Goal**: Fix violations preventing publication

- [ ] **Visual Design Overhaul**
  - [ ] Replace custom colors with system palette
  - [ ] Keep brand color ONLY on primary CTAs
  - [ ] Ensure WCAG AA contrast ratios

- [ ] **Accessibility Fixes**
  - [ ] Add ARIA labels to all components
  - [ ] Implement semantic HTML for property cards
  - [ ] Add alt text to all images
  - [ ] Test with screen readers

- [ ] **Communication Standards**
  - [ ] Update RAG prompts to ban marketing language
  - [ ] Enforce concise, context-driven responses
  - [ ] Add response quality validation

**Deliverable**: PropertyCard component that passes OpenAI design review

---

### Phase 2: Conversational UX Enhancement (Week 3-4)
**Goal**: Make property search feel like natural ChatGPT extension

- [ ] **Inline Property Cards**
  - [ ] Create CompactPropertyCard component
  - [ ] Integrate cards into chat message flow
  - [ ] Implement "View All" → Fullscreen transition

- [ ] **Context Management**
  - [ ] Build ConversationContext service
  - [ ] Track user preferences (budget, location, type)
  - [ ] Generate smart suggestions (OpenAI-compliant)

- [ ] **Display Mode Implementation**
  - [ ] Inline mode (default)
  - [ ] Fullscreen mode (for browsing)
  - [ ] Maintain chat composer in fullscreen

**Deliverable**: Property search feels like ChatGPT conversation, not web form

---

### Phase 3: Real Estate Intelligence (Week 5-6)
**Goal**: Domain-specific features that extend ChatGPT distinctively

- [ ] **Smart Property Insights**
  - [ ] Neighborhood analysis (schools, transit, amenities)
  - [ ] Price trend predictions
  - [ ] Investment ROI calculator

- [ ] **Advanced RAG Features**
  - [ ] Multi-property comparison (side-by-side cards)
  - [ ] Similar property recommendations
  - [ ] Saved searches with alerts

- [ ] **Picture-in-Picture Tools** (Optional)
  - [ ] Mortgage calculator PiP widget
  - [ ] Virtual tour viewer (if data available)

**Deliverable**: Unique real estate features unavailable in base ChatGPT

---

### Phase 4: Production Polish & Testing (Week 7-8)
**Goal**: Publication-ready quality

- [ ] **Performance Optimization**
  - [ ] Implement skeleton loaders
  - [ ] Progressive image loading
  - [ ] Response caching for common queries

- [ ] **Error Handling**
  - [ ] Graceful degradation (show cached results if API fails)
  - [ ] User-friendly error messages
  - [ ] Retry logic with exponential backoff

- [ ] **Quality Assurance**
  - [ ] Cross-browser testing (Chrome, Safari, Firefox)
  - [ ] Mobile responsiveness
  - [ ] Screen reader testing (VoiceOver, NVDA)
  - [ ] Load testing (100+ concurrent users)

**Deliverable**: Application ready for OpenAI platform submission

---

## 📊 Success Metrics

### OpenAI Compliance Scorecard

| Principle | Current Score | Target Score | Key Metrics |
|-----------|---------------|--------------|-------------|
| **Conversational** | 3/10 | 9/10 | Properties appear inline in chat |
| **Intelligent** | 5/10 | 9/10 | Context retention >80% accuracy |
| **Simple** | 4/10 | 9/10 | Max 4 data points per card |
| **Responsive** | 7/10 | 9/10 | Time to First Property <500ms |
| **Accessible** | 2/10 | 9/10 | WCAG AA compliance 100% |

### User Experience Metrics

- **Time to First Result**: <500ms (current: ~2s)
- **Click-through Rate**: >30% on property cards
- **Conversation Completion**: >80% reach "View Details" or "Contact"
- **User Satisfaction**: >4.5/5 stars

### Technical Quality Metrics

- **Lighthouse Score**: >90 (Performance, Accessibility, Best Practices)
- **Core Web Vitals**: LCP <2.5s, FID <100ms, CLS <0.1
- **API Reliability**: 99.9% uptime, <1% error rate

---

## 🔧 Quick Wins (Implement First)

### 1. Compact Property Card (2 hours)
Replace current PropertyCard with CompactPropertyCard component following OpenAI "one card, a few key details, a clear CTA" principle.

**File**: `frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte`

### 2. System Color Palette (1 hour)
Create CSS variables for system colors and remove custom brand colors from non-CTA elements.

**File**: `frontend/open-webui/src/app.css`

```css
:root {
  /* System colors (inherit from ChatGPT) */
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --bg-primary: #ffffff;
  --bg-secondary: #f3f4f6;

  /* Brand accent (ONLY for primary CTAs) */
  --brand-primary: #3b82f6;
  --brand-primary-hover: #2563eb;
}
```

### 3. ARIA Labels (2 hours)
Add semantic HTML and ARIA labels to PropertyCard and PropertySearch components.

**Files**:
- `PropertyCard.svelte`
- `PropertySearch.svelte`

### 4. Remove Marketing Language (1 hour)
Update RAG service prompts to ban promotional language.

**File**: `services/rag_service/prompt_templates.py`

**Total Time**: 6 hours for immediate OpenAI compliance improvements

---

## 📝 OpenAI Submission Checklist

Before submitting to OpenAI platform, verify:

### Design Standards
- [ ] System color palette used (no custom backgrounds)
- [ ] Brand color appears ONLY on primary CTAs
- [ ] System fonts used (SF Pro/Roboto)
- [ ] Consistent grid-based spacing
- [ ] Monochromatic outlined icons

### Use Case Validation
- [ ] Fits naturally into dialogue (not a separate web app)
- [ ] Time-bound interactions (clear start/end)
- [ ] Immediate actionability (clear CTAs)
- [ ] Simple representation (one card = few details + CTA)
- [ ] Distinctive extension of ChatGPT (unique real estate features)

### Communication Standards
- [ ] Concise responses (<3 sentences for listings)
- [ ] Context-driven (references user preferences)
- [ ] Jargon-free language
- [ ] NO marketing language
- [ ] Transparent proactive suggestions

### Accessibility
- [ ] WCAG AA contrast ratios (4.5:1 for text)
- [ ] Alt text on all images
- [ ] ARIA labels on interactive elements
- [ ] Semantic HTML
- [ ] Screen reader tested

### Technical Quality
- [ ] Lighthouse score >90
- [ ] Core Web Vitals passing
- [ ] Cross-browser compatible
- [ ] Mobile responsive
- [ ] Error handling graceful

### Prohibited Content
- [ ] NO long-form static content (avoid listing pages)
- [ ] NO complicated multi-step workflows (max 3 steps)
- [ ] NO advertisements or upsells
- [ ] NO sensitive information in cards
- [ ] NO duplication of ChatGPT built-in features

---

## 🎓 Training Materials

### For Developers

**Required Reading**:
1. [OpenAI Apps SDK Design Guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines/)
2. [WCAG 2.1 AA Compliance](https://www.w3.org/WAI/WCAG21/quickref/)
3. [Conversational UI Best Practices](https://design.google/library/conversation-design-speaking-same-language/)

**Code Examples**:
- Reference implementation: `frontend/open-webui/src/lib/components/property/CompactPropertyCard.svelte`
- System color usage: `frontend/open-webui/src/app.css`
- ARIA patterns: `frontend/open-webui/src/lib/components/property/AccessiblePropertyCard.svelte`

### For Product Team

**Key Principles to Enforce**:
1. **"One card, a few details, one CTA"** - Review all property card designs
2. **"No marketing language"** - Review all AI prompts and response templates
3. **"Context-driven proactivity"** - Only suggest when relevant to user intent
4. **"Conversation, not forms"** - Design interactions as dialogue, not web forms

---

## 🔗 References

- [OpenAI Apps SDK Design Guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines/)
- [Material Design 3 - Conversational AI](https://m3.material.io/foundations/interaction/conversational-ai)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Conversation Design by Google](https://design.google/library/conversation-design-speaking-same-language/)
- [Apple Human Interface Guidelines - Siri](https://developer.apple.com/design/human-interface-guidelines/siri)

---

## 📞 Support

For questions about implementing OpenAI design standards:
- Review this guide first
- Check reference implementations in `frontend/open-webui/src/lib/components/property/`
- Consult `CLAUDE.md` for project-specific guidelines
- Open issue at project repository

---

**Document Version**: 1.0
**Last Updated**: 2025-11-01
**Author**: REE AI Development Team
**Status**: Ready for Implementation
