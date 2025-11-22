# Design Tokens - OpenAI Apps SDK

**Source:** Figma File `4JSHQqDBBms4mAvprmbN2b` (Apps in ChatGPT • Components & Templates)
**Extracted:** 2025-11-22
**Location:** `frontend/open-webui/src/lib/styles/design-tokens.css`

---

## 📐 Component Dimensions (From Figma)

### 🌁 Inline Card
```
Width:  361px
Height: 336px
Corner Radius: 24px
Item Spacing: 10px
```

### Entity Card
```
Size: 345px × 345px
Corner Radius: 24px
Item Spacing: 10px
```

### Compact Card (REE AI Specific)
```
Max Width: 400px
Padding: 12px
Corner Radius: 8px
Gap: 12px
Thumbnail: 60px
```

**Usage:** Inline display in chat (follows OpenAI "Simple" principle)

---

## 🎨 Color System

### Light Mode
```css
Background:
  --bg-primary: #ffffff     /* Main background */
  --bg-secondary: #e8e8e8   /* Cards, secondary areas */
  --bg-tertiary: #f3f4f6    /* Hover states */

Text:
  --text-primary: #0d0d0d   /* Main text */
  --text-secondary: #6b7280 /* Secondary text */
  --text-tertiary: #9ca3af  /* Disabled, placeholders */

Border:
  --border-color: #e5e7eb
  --border-hover: #d1d5db
```

### Dark Mode
```css
Background:
  --bg-primary: #212121
  --bg-secondary: #2d2d2d
  --bg-tertiary: #3a3a3a

Text:
  --text-primary: #ffffff
  --text-secondary: #cdcdcd
  --text-tertiary: #9ca3af

Border:
  --border-color: #404040
  --border-hover: #525252
```

### Brand Colors (ONLY for Primary CTAs)
```css
--brand-primary: #3b82f6
--brand-primary-hover: #2563eb
--brand-primary-active: #1d4ed8
```

**OpenAI Compliance:**
- ✅ System colors for backgrounds and text
- ✅ Brand color ONLY on primary buttons/CTAs
- ❌ Never use brand colors for backgrounds or badges

---

## 📏 Spacing System

Grid-based spacing following OpenAI standards:

```css
--space-1: 4px    /* Fine adjustments */
--space-2: 8px    /* Small gaps */
--space-3: 12px   /* Default gaps */
--space-4: 16px   /* Standard spacing */
--space-6: 24px   /* Section spacing */
--space-8: 32px   /* Large spacing */
--space-12: 48px  /* Extra large */
--space-16: 64px  /* Sections */
```

---

## 🔤 Typography

### Font Families
```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
--font-mono: "SF Mono", Monaco, Consolas, monospace
```

### Font Sizes
```css
--text-xs: 12px    /* Labels, captions */
--text-sm: 14px    /* Body small */
--text-base: 16px  /* Body default */
--text-lg: 18px    /* Emphasized */
--text-xl: 20px    /* Sub-headings */
--text-2xl: 24px   /* Headings */
--text-3xl: 30px   /* Large headings */
```

### Font Weights
```css
--font-normal: 400    /* Body text */
--font-medium: 500    /* Emphasized */
--font-semibold: 600  /* Sub-headings */
--font-bold: 700      /* Headings */
```

---

## 🎭 Shadows

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05)
--shadow-base: 0 1px 3px rgba(0,0,0,0.1)
--shadow-md: 0 4px 6px rgba(0,0,0,0.1)
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1)
--shadow-xl: 0 20px 25px rgba(0,0,0,0.1)
```

**Usage:**
- Cards: `--shadow-base`
- Modals: `--shadow-lg`
- Dropdowns: `--shadow-md`

---

## ⚡ Transitions

```css
--transition-fast: 150ms ease-in-out   /* Hovers */
--transition-base: 200ms ease-in-out   /* Default */
--transition-slow: 300ms ease-in-out   /* Modals */
```

---

## 🎯 Usage Examples

### Compact Property Card (OpenAI Compliant)

```svelte
<article class="compact-property-card">
  <img
    src={property.image}
    alt={property.title}
    style="width: var(--thumbnail-sm); height: var(--thumbnail-sm)"
  />

  <div class="content">
    <h4 class="text-primary">{property.title}</h4>
    <p class="text-secondary text-sm">{property.location}</p>
    <p class="text-primary font-bold">{property.price}</p>
  </div>

  <button class="btn-primary">
    Xem chi tiết →
  </button>
</article>

<style>
  .compact-property-card {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-3);
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--compact-card-radius);
    max-width: var(--compact-card-max-width);
    transition: border-color var(--transition-fast);
  }

  .compact-property-card:hover {
    border-color: var(--border-hover);
  }

  .btn-primary {
    padding: var(--space-2) var(--space-4);
    border-radius: 6px;
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    white-space: nowrap;
  }
</style>
```

---

## ✅ OpenAI Compliance Checklist

When using design tokens, ensure:

- [x] System colors for text and backgrounds
- [x] Brand color ONLY on primary CTAs
- [x] Grid-based spacing (multiples of 4px)
- [x] System fonts (no custom typefaces)
- [x] WCAG AA contrast ratios (4.5:1 for text)
- [x] Semantic HTML with ARIA labels
- [x] Focus visible styles for keyboard navigation

---

## 🔄 Updating Design Tokens

To sync with latest Figma designs:

1. Get fresh Figma token
2. Run extraction script:
   ```bash
   curl -H "X-Figma-Token: YOUR_TOKEN" \
     "https://api.figma.com/v1/files/4JSHQqDBBms4mAvprmbN2b" \
     -o /tmp/figma_file.json
   ```
3. Parse and update `design-tokens.css`
4. Update this documentation

---

## 📚 References

- **Figma File:** Apps in ChatGPT • Components & Templates
- **FileKey:** `4JSHQqDBBms4mAvprmbN2b`
- **OpenAI Standards:** `docs/OPENAI_DESIGN_STANDARDS.md`
- **Component Mapping:** `docs/design/OPENAI_APPS_SDK_MAPPING.md`
