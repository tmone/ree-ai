# Figma Components Reference - Apps in ChatGPT

**Source:** Figma File `4JSHQqDBBms4mAvprmbN2b`
**File Name:** Apps in ChatGPT • Components & Templates
**Last Updated:** 2025-11-22
**Extraction Date:** 2025-11-22

---

## 📋 Overview

This document contains the complete component specifications extracted from the official OpenAI Apps SDK Figma file. Use this as the source of truth for all UI component implementations.

---

## 🎨 Component Library

### 1. 🌁 Inline Card (Primary Card Component)

**Figma Node:** `4JSHQqDBBms4mAvprmbN2b`
**Component Type:** Card
**Usage:** Display entity information inline in chat

**Dimensions:**
```
Width:  361px
Height: 336px
Corner Radius: 24px
Item Spacing: 10px
Padding: 16px (all sides)
```

**Structure:**
```
┌─────────────────────────────────┐
│  [Image - 329x200px]            │
│                                 │
│  Title (20px, Bold)             │
│  Subtitle (14px, Regular)       │
│                                 │
│  ┌─────────────────────────┐   │
│  │  Primary Action Button  │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

**Typography:**
- **Title:** 20px, Weight 700 (Bold), Color: #0d0d0d (light) / #ffffff (dark)
- **Subtitle:** 14px, Weight 400 (Regular), Color: #6b7280 (light) / #cdcdcd (dark)
- **Button Text:** 14px, Weight 600 (Semibold)

**Colors:**
- **Background (Light):** #ffffff
- **Background (Dark):** #212121
- **Border (Light):** #e5e7eb
- **Border (Dark):** #404040
- **Primary Action:** #3b82f6

**Spacing:**
- **Image to Title:** 12px
- **Title to Subtitle:** 8px
- **Subtitle to Button:** 16px

**States:**
- **Default:** Border #e5e7eb, Background #ffffff
- **Hover:** Border #d1d5db
- **Focus:** 2px outline #3b82f6, offset 2px
- **Active:** Background unchanged, button #1d4ed8

---

### 2. 📦 Entity Card (Square Card)

**Component Type:** Card
**Usage:** Display entities in grid layout

**Dimensions:**
```
Width:  345px
Height: 345px
Corner Radius: 24px
Item Spacing: 10px
Padding: 16px
```

**Structure:**
```
┌─────────────────┐
│  [Image]        │
│   313x313px     │
│                 │
│  Entity Name    │
│  Description    │
└─────────────────┘
```

**Best Used For:**
- Product listings
- Property thumbnails
- Gallery items
- 1:1 aspect ratio content

---

### 3. 🎠 Inline Carousel (Component Collection)

**Component Type:** Container
**Usage:** Scrollable list of cards

**Dimensions:**
```
Container Width: 100% (max 800px)
Item Width: 361px (same as Inline Card)
Gap Between Items: 16px
Scroll Behavior: Horizontal scroll with snap
Navigation: Arrow buttons (optional)
```

**Navigation Buttons:**
```
Size: 32px × 32px
Background: rgba(0,0,0,0.05) light / rgba(255,255,255,0.1) dark
Icon: Chevron (16px)
Position: Absolute, centered vertically
```

**Carousel Structure:**
```
┌─[◀]──────────────────────────────────[▶]─┐
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │
│  │Card1│  │Card2│  │Card3│  │Card4│ ... │
│  └─────┘  └─────┘  └─────┘  └─────┘     │
└───────────────────────────────────────────┘
```

**Behavior:**
- **Snap to card:** Each scroll snaps to card start
- **Overflow:** Scroll indicator appears if >2 cards
- **Touch:** Swipe gesture enabled on mobile

---

### 4. 🔎 Inspector (Detail View)

**Component Type:** Modal/Sidebar
**Usage:** Show detailed entity information

**Dimensions:**
```
Width: 480px (desktop) / 100% (mobile)
Max Height: 80vh
Padding: 24px
Corner Radius: 12px (desktop) / 0 (mobile fullscreen)
```

**Structure:**
```
┌────────────────────────────────┐
│  [Close Button ✕]             │
│                                │
│  ┌──────────────────────────┐ │
│  │  Hero Image              │ │
│  │  480x320px               │ │
│  └──────────────────────────┘ │
│                                │
│  Title (24px Bold)             │
│  Subtitle (16px Regular)       │
│                                │
│  Description text...           │
│                                │
│  ┌─ Section 1 ──────────────┐ │
│  │  Attribute: Value        │ │
│  │  Attribute: Value        │ │
│  └──────────────────────────┘ │
│                                │
│  ┌─ Section 2 ──────────────┐ │
│  │  ...                     │ │
│  └──────────────────────────┘ │
│                                │
│  [Primary Action]              │
└────────────────────────────────┘
```

**Typography:**
- **Title:** 24px, Weight 700, Color: #0d0d0d / #ffffff
- **Subtitle:** 16px, Weight 400, Color: #6b7280 / #cdcdcd
- **Section Header:** 18px, Weight 600, Color: #0d0d0d / #ffffff
- **Body Text:** 16px, Weight 400, Line Height 1.5
- **Labels:** 14px, Weight 600, Color: #6b7280 / #cdcdcd
- **Values:** 14px, Weight 400, Color: #0d0d0d / #ffffff

**Colors:**
- **Background:** #ffffff (light) / #212121 (dark)
- **Section Background:** #f3f4f6 (light) / #2d2d2d (dark)
- **Divider:** #e5e7eb (light) / #404040 (dark)

**Spacing:**
- **Image to Title:** 16px
- **Title to Subtitle:** 8px
- **Subtitle to Description:** 12px
- **Section Spacing:** 20px
- **Attribute Spacing:** 8px

**Close Button:**
```
Position: Absolute, top-right (16px, 16px)
Size: 32px × 32px
Background: rgba(0,0,0,0.05) / rgba(255,255,255,0.1)
Icon: X (20px)
Corner Radius: 6px
```

---

### 5. 📱 Compact Card (REE AI Custom)

**Component Type:** Card
**Usage:** Inline display in chat messages (minimal footprint)

**Dimensions:**
```
Max Width: 400px
Height: Auto (min 84px)
Padding: 12px
Gap: 12px
Corner Radius: 8px
```

**Structure:**
```
┌────────────────────────────────────────┐
│  [Img] Title                   [CTA]   │
│  60x60  Location • 2PN 75m²            │
│         Price: 5 tỷ VNĐ                │
└────────────────────────────────────────┘
```

**Layout:**
- **Flexbox:** Row (desktop), Column (mobile <480px)
- **Thumbnail:** 60px × 60px, border-radius 6px
- **Content:** Flex 1, min-width 0 (allows truncation)
- **CTA Button:** Fixed width, no shrink

**Typography:**
- **Title:** 14px, Weight 600, truncate with ellipsis
- **Metadata:** 12px, Weight 400, gray color
- **Price:** 14px, Weight 700

**Colors:**
- **Background:** #ffffff / #212121
- **Border:** #e5e7eb / #404040
- **CTA:** #3b82f6 (ONLY place for brand color)

**Data Points (Max 4):**
1. Title
2. Location + Key Feature (combined)
3. Price
4. CTA Button

**Mobile Behavior (<480px):**
- Stack vertically
- Thumbnail: 100% width × 150px height
- CTA: Full width

---

## 🎨 Color System

### Light Mode Colors

**Primary Colors:**
```css
--bg-primary: #ffffff      /* Main background */
--bg-secondary: #e8e8e8    /* Cards, secondary areas */
--bg-tertiary: #f3f4f6     /* Hover states, sections */
```

**Text Colors:**
```css
--text-primary: #0d0d0d    /* Headings, important text */
--text-secondary: #6b7280  /* Body text, labels */
--text-tertiary: #9ca3af   /* Disabled, placeholders */
```

**Border Colors:**
```css
--border-color: #e5e7eb    /* Default borders */
--border-hover: #d1d5db    /* Hover state borders */
```

**Brand Colors (PRIMARY CTA ONLY):**
```css
--brand-primary: #3b82f6        /* Primary action */
--brand-primary-hover: #2563eb  /* Hover state */
--brand-primary-active: #1d4ed8 /* Active/pressed state */
```

**Semantic Colors:**
```css
--color-success: #10b981
--color-warning: #f59e0b
--color-error: #ef4444
--color-info: #3b82f6
```

### Dark Mode Colors

**Primary Colors:**
```css
--bg-primary: #212121      /* Main background */
--bg-secondary: #2d2d2d    /* Cards, secondary areas */
--bg-tertiary: #3a3a3a     /* Hover states, sections */
```

**Text Colors:**
```css
--text-primary: #ffffff    /* Headings, important text */
--text-secondary: #cdcdcd  /* Body text, labels */
--text-tertiary: #9ca3af   /* Disabled, placeholders */
```

**Border Colors:**
```css
--border-color: #404040    /* Default borders */
--border-hover: #525252    /* Hover state borders */
```

---

## 📏 Spacing System (Grid-Based, 4px Base Unit)

```css
--space-1: 4px     /* 0.25rem - Fine adjustments */
--space-2: 8px     /* 0.5rem  - Small gaps */
--space-3: 12px    /* 0.75rem - Default gaps */
--space-4: 16px    /* 1rem    - Standard spacing */
--space-5: 20px    /* 1.25rem - Medium spacing */
--space-6: 24px    /* 1.5rem  - Section spacing */
--space-8: 32px    /* 2rem    - Large spacing */
--space-10: 40px   /* 2.5rem  - Extra large */
--space-12: 48px   /* 3rem    - Section breaks */
--space-16: 64px   /* 4rem    - Major sections */
```

**Usage Guidelines:**
- **Card padding:** 16px (--space-4) or 24px (--space-6)
- **Element gaps:** 8px (--space-2) or 12px (--space-3)
- **Section spacing:** 24px (--space-6) or 32px (--space-8)
- **Component margins:** 16px (--space-4)

---

## 🔤 Typography System

### Font Families

**Sans-serif (Primary):**
```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif
```

**Monospace (Code):**
```css
--font-mono: "SF Mono", Monaco, Consolas, "Liberation Mono",
             "Courier New", monospace
```

### Font Sizes

```css
--text-xs: 12px     /* 0.75rem  - Small labels, captions */
--text-sm: 14px     /* 0.875rem - Body small, buttons */
--text-base: 16px   /* 1rem     - Body default */
--text-lg: 18px     /* 1.125rem - Emphasized text */
--text-xl: 20px     /* 1.25rem  - Sub-headings */
--text-2xl: 24px    /* 1.5rem   - Headings */
--text-3xl: 30px    /* 1.875rem - Large headings */
```

### Font Weights

```css
--font-normal: 400     /* Body text */
--font-medium: 500     /* Emphasized text */
--font-semibold: 600   /* Sub-headings, buttons */
--font-bold: 700       /* Headings */
```

### Line Heights

```css
--leading-tight: 1.25    /* Headings */
--leading-normal: 1.5    /* Body text */
--leading-relaxed: 1.75  /* Long-form content */
```

### Typography Scale

| Element | Size | Weight | Line Height | Color |
|---------|------|--------|-------------|-------|
| **H1** | 30px | 700 | 1.25 | --text-primary |
| **H2** | 24px | 700 | 1.25 | --text-primary |
| **H3** | 20px | 600 | 1.25 | --text-primary |
| **H4** | 18px | 600 | 1.5 | --text-primary |
| **Body** | 16px | 400 | 1.5 | --text-primary |
| **Body Small** | 14px | 400 | 1.5 | --text-secondary |
| **Caption** | 12px | 400 | 1.5 | --text-tertiary |
| **Button** | 14px | 600 | 1 | white |
| **Label** | 14px | 600 | 1.5 | --text-secondary |

---

## 🎭 Shadow System

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1),
               0 1px 2px 0 rgba(0, 0, 0, 0.06)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -1px rgba(0, 0, 0, 0.06)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -2px rgba(0, 0, 0, 0.05)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 10px 10px -5px rgba(0, 0, 0, 0.04)
```

**Usage:**
- **Cards:** `--shadow-base`
- **Modals:** `--shadow-xl`
- **Dropdowns:** `--shadow-lg`
- **Buttons (hover):** `--shadow-md`

---

## ⚡ Transitions & Animations

### Transition Speeds

```css
--transition-fast: 150ms ease-in-out    /* Hovers, simple state changes */
--transition-base: 200ms ease-in-out    /* Default animations */
--transition-slow: 300ms ease-in-out    /* Modals, complex animations */
```

### Common Transitions

**Hover Effects:**
```css
transition: border-color var(--transition-fast);
transition: background-color var(--transition-fast);
transition: transform var(--transition-fast);
```

**Modal Animations:**
```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Scale in */
@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
```

---

## 🎯 Z-Index Layers

```css
--z-base: 0           /* Normal document flow */
--z-dropdown: 1000    /* Dropdown menus */
--z-sticky: 1100      /* Sticky headers */
--z-modal: 1300       /* Modal overlays */
--z-popover: 1400     /* Popovers, tooltips */
--z-tooltip: 1500     /* Tooltips (highest) */
```

---

## ♿ Accessibility Standards (WCAG AA)

### Color Contrast Requirements

**Text Contrast:**
- **Normal text (16px+):** Minimum 4.5:1
- **Large text (18px+ or 14px+ bold):** Minimum 3:1
- **UI Components:** Minimum 3:1

**Our Color Pairs (Light Mode):**
- `#0d0d0d` on `#ffffff`: **21:1** ✅ (Excellent)
- `#6b7280` on `#ffffff`: **4.6:1** ✅ (AA compliant)
- `#3b82f6` on `#ffffff`: **3.1:1** ⚠️ (Use for large text or UI only)

**Our Color Pairs (Dark Mode):**
- `#ffffff` on `#212121`: **18.5:1** ✅ (Excellent)
- `#cdcdcd` on `#212121`: **12.7:1** ✅ (Excellent)

### Focus Indicators

**Visible Focus (Required):**
```css
*:focus-visible {
  outline: 2px solid var(--brand-primary);
  outline-offset: 2px;
}
```

### Interactive Elements

**Minimum Touch Target:**
- Desktop: 24px × 24px
- Mobile: 44px × 44px

**Keyboard Navigation:**
- All interactive elements must be keyboard accessible
- Tab order follows logical reading order
- ESC closes modals/dropdowns

---

## 📐 Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 480px) {
  /* Compact cards stack vertically */
  /* Modals go fullscreen */
}

/* Tablet */
@media (max-width: 768px) {
  /* Carousels adapt scroll behavior */
  /* Inspector becomes fullscreen */
}

/* Desktop */
@media (min-width: 769px) {
  /* Default desktop layout */
  /* Inspector as sidebar or modal */
}
```

---

## 🎨 Component Usage Matrix

| Component | Desktop | Mobile | Use Case |
|-----------|---------|--------|----------|
| **Inline Card** | 361×336px | Stack | Rich content display |
| **Entity Card** | 345×345px | Full width | Grid layouts |
| **Compact Card** | 400px max | Stack | Inline chat results |
| **Inspector** | 480px width | Fullscreen | Detail views |
| **Carousel** | Scroll | Swipe | Multiple items |

---

## 📝 Implementation Checklist

When implementing any component, ensure:

- [ ] Uses design tokens from this file
- [ ] Follows spacing system (4px grid)
- [ ] Meets WCAG AA contrast ratios
- [ ] Has focus-visible styles
- [ ] Supports dark mode
- [ ] Responsive on mobile
- [ ] Semantic HTML
- [ ] ARIA labels where needed
- [ ] Keyboard accessible
- [ ] Touch targets ≥44px (mobile)

---

## 🔗 References

- **Figma File:** https://www.figma.com/file/4JSHQqDBBms4mAvprmbN2b/
- **OpenAI Design Standards:** `docs/design/OPENAI_DESIGN_STANDARDS.md`
- **Design Tokens CSS:** `frontend/open-webui/src/lib/styles/design-tokens.css`
- **Component Mapping:** `docs/design/OPENAI_APPS_SDK_MAPPING.md`

---

**Last Verified:** 2025-11-22
**Maintained By:** Development Team
**Questions?** See implementation examples in `docs/implementation/`
