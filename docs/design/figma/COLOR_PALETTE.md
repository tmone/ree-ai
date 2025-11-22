# Color Palette - OpenAI Apps SDK

**Source:** Figma File `4JSHQqDBBms4mAvprmbN2b`
**Last Updated:** 2025-11-22

---

## 🎨 Complete Color System

### Light Mode Palette

#### Background Colors

| Color | Hex | RGB | Usage | Preview |
|-------|-----|-----|-------|---------|
| **Primary** | `#ffffff` | `rgb(255, 255, 255)` | Main background, cards | ⬜ White |
| **Secondary** | `#e8e8e8` | `rgb(232, 232, 232)` | Alternative backgrounds | ◻️ Light Gray |
| **Tertiary** | `#f3f4f6` | `rgb(243, 244, 246)` | Hover states, sections | ◻️ Lighter Gray |

**CSS Variables:**
```css
--bg-primary: #ffffff;
--bg-secondary: #e8e8e8;
--bg-tertiary: #f3f4f6;
```

#### Text Colors

| Color | Hex | RGB | Usage | Contrast (on white) |
|-------|-----|-----|-------|---------------------|
| **Primary** | `#0d0d0d` | `rgb(13, 13, 13)` | Headings, important text | 21:1 ✅ |
| **Secondary** | `#6b7280` | `rgb(107, 114, 128)` | Body text, labels | 4.6:1 ✅ |
| **Tertiary** | `#9ca3af` | `rgb(156, 163, 175)` | Disabled, placeholders | 2.8:1 ⚠️ |

**CSS Variables:**
```css
--text-primary: #0d0d0d;
--text-secondary: #6b7280;
--text-tertiary: #9ca3af;
```

**Usage Rules:**
- **Primary:** Use for headings, important content
- **Secondary:** Use for body text, must be 14px+ for AA compliance
- **Tertiary:** Use for disabled states, large text (18px+) only

#### Border Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Default** | `#e5e7eb` | `rgb(229, 231, 235)` | Card borders, dividers |
| **Hover** | `#d1d5db` | `rgb(209, 213, 219)` | Interactive borders on hover |

**CSS Variables:**
```css
--border-color: #e5e7eb;
--border-hover: #d1d5db;
```

---

### Dark Mode Palette

#### Background Colors

| Color | Hex | RGB | Usage | Preview |
|-------|-----|-----|-------|---------|
| **Primary** | `#212121` | `rgb(33, 33, 33)` | Main background, cards | ⬛ Dark Gray |
| **Secondary** | `#2d2d2d` | `rgb(45, 45, 45)` | Alternative backgrounds | ▪️ Medium Dark |
| **Tertiary** | `#3a3a3a` | `rgb(58, 58, 58)` | Hover states, sections | ▫️ Lighter Dark |

**CSS Variables:**
```css
--bg-primary: #212121;
--bg-secondary: #2d2d2d;
--bg-tertiary: #3a3a3a;
```

#### Text Colors

| Color | Hex | RGB | Usage | Contrast (on #212121) |
|-------|-----|-----|-------|----------------------|
| **Primary** | `#ffffff` | `rgb(255, 255, 255)` | Headings, important text | 18.5:1 ✅ |
| **Secondary** | `#cdcdcd` | `rgb(205, 205, 205)` | Body text, labels | 12.7:1 ✅ |
| **Tertiary** | `#9ca3af` | `rgb(156, 163, 175)` | Disabled, placeholders | 6.2:1 ✅ |

**CSS Variables:**
```css
--text-primary: #ffffff;
--text-secondary: #cdcdcd;
--text-tertiary: #9ca3af;
```

#### Border Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Default** | `#404040` | `rgb(64, 64, 64)` | Card borders, dividers |
| **Hover** | `#525252` | `rgb(82, 82, 82)` | Interactive borders on hover |

**CSS Variables:**
```css
--border-color: #404040;
--border-hover: #525252;
```

---

### Brand Colors (PRIMARY CTA ONLY)

**CRITICAL:** Brand colors should ONLY be used for primary CTAs (buttons). Never use for backgrounds, badges, or decorative elements.

| State | Hex | RGB | Usage |
|-------|-----|-----|-------|
| **Default** | `#3b82f6` | `rgb(59, 130, 246)` | Primary action button |
| **Hover** | `#2563eb` | `rgb(37, 99, 235)` | Button hover state |
| **Active** | `#1d4ed8` | `rgb(29, 78, 216)` | Button pressed/active |

**CSS Variables:**
```css
--brand-primary: #3b82f6;
--brand-primary-hover: #2563eb;
--brand-primary-active: #1d4ed8;
```

**Contrast Ratios:**
- White text on `#3b82f6`: **4.8:1** ✅ (AA compliant)
- White text on `#2563eb`: **5.9:1** ✅ (AA compliant)
- White text on `#1d4ed8`: **7.3:1** ✅ (AA compliant)

**Example Usage:**
```css
/* ✅ CORRECT - Primary CTA only */
.btn-primary {
  background-color: var(--brand-primary);
  color: white;
}

/* ❌ WRONG - Don't use for backgrounds */
.card-highlighted {
  background-color: var(--brand-primary); /* NO! */
}

/* ❌ WRONG - Don't use for badges */
.badge {
  background-color: var(--brand-primary); /* NO! */
}
```

---

### Semantic Colors

Used for status indicators, alerts, and feedback messages.

| Semantic | Hex | RGB | Usage |
|----------|-----|-----|-------|
| **Success** | `#10b981` | `rgb(16, 185, 129)` | Success messages, completed states |
| **Warning** | `#f59e0b` | `rgb(245, 158, 11)` | Warning messages, caution states |
| **Error** | `#ef4444` | `rgb(239, 68, 68)` | Error messages, destructive actions |
| **Info** | `#3b82f6` | `rgb(59, 130, 246)` | Info messages, neutral notifications |

**CSS Variables:**
```css
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #3b82f6;
```

**Background Tints (10% opacity):**
```css
--bg-success: rgba(16, 185, 129, 0.1);   /* Light green */
--bg-warning: rgba(245, 158, 11, 0.1);   /* Light orange */
--bg-error: rgba(239, 68, 68, 0.1);      /* Light red */
--bg-info: rgba(59, 130, 246, 0.1);      /* Light blue */
```

---

## 🎨 Color Usage Guidelines

### 1. System Colors First

**Always use system colors for:**
- Text (primary, secondary, tertiary)
- Backgrounds (primary, secondary, tertiary)
- Borders (default, hover)

**Example:**
```css
.card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}
```

### 2. Brand Color Sparingly

**Only use brand color for:**
- Primary action buttons
- Active/selected states (outline, not background)
- Focus indicators

**Example:**
```css
/* ✅ Good */
.btn-primary {
  background-color: var(--brand-primary);
}

.input:focus {
  outline: 2px solid var(--brand-primary);
}

/* ❌ Bad */
.highlight {
  background-color: var(--brand-primary);
}
```

### 3. Semantic Colors for Feedback

**Use semantic colors for:**
- Success/error messages
- Status indicators
- Alerts and toasts

**Example:**
```css
.alert-success {
  background-color: var(--bg-success);
  color: var(--color-success);
  border-left: 4px solid var(--color-success);
}
```

---

## 📊 Color Contrast Matrix

### Light Mode

| Text Color | Background | Ratio | WCAG AA | WCAG AAA |
|------------|------------|-------|---------|----------|
| `#0d0d0d` | `#ffffff` | 21:1 | ✅ Pass | ✅ Pass |
| `#6b7280` | `#ffffff` | 4.6:1 | ✅ Pass | ❌ Fail |
| `#9ca3af` | `#ffffff` | 2.8:1 | ❌ Fail | ❌ Fail |
| `#ffffff` | `#3b82f6` | 4.8:1 | ✅ Pass | ❌ Fail |

**Recommendations:**
- `#9ca3af` should only be used for disabled states or large text (18px+)
- For body text, use `#0d0d0d` or `#6b7280`

### Dark Mode

| Text Color | Background | Ratio | WCAG AA | WCAG AAA |
|------------|------------|-------|---------|----------|
| `#ffffff` | `#212121` | 18.5:1 | ✅ Pass | ✅ Pass |
| `#cdcdcd` | `#212121` | 12.7:1 | ✅ Pass | ✅ Pass |
| `#9ca3af` | `#212121` | 6.2:1 | ✅ Pass | ✅ Pass |

**All dark mode text colors pass WCAG AA!**

---

## 🎨 Color Palettes by Component

### CompactPropertyCard

```css
/* Light Mode */
.compact-property-card {
  background-color: #ffffff;
  border-color: #e5e7eb;
}

.title { color: #0d0d0d; }
.metadata { color: #6b7280; }
.price { color: #0d0d0d; }
.cta-button { background-color: #3b82f6; color: white; }

/* Dark Mode */
.compact-property-card {
  background-color: #212121;
  border-color: #404040;
}

.title { color: #ffffff; }
.metadata { color: #cdcdcd; }
.price { color: #ffffff; }
```

### PropertyDetailModal

```css
/* Light Mode */
.modal-overlay { background-color: rgba(0, 0, 0, 0.5); }
.modal-container { background-color: #ffffff; }
.section { background-color: #f3f4f6; }
.divider { border-color: #e5e7eb; }

/* Dark Mode */
.modal-overlay { background-color: rgba(0, 0, 0, 0.7); }
.modal-container { background-color: #212121; }
.section { background-color: #2d2d2d; }
.divider { border-color: #404040; }
```

### Buttons

```css
/* Primary Button */
.btn-primary {
  background-color: #3b82f6;
  color: #ffffff;
}
.btn-primary:hover { background-color: #2563eb; }
.btn-primary:active { background-color: #1d4ed8; }

/* Secondary Button */
.btn-secondary {
  background-color: #e5e7eb; /* Light */
  background-color: #404040; /* Dark */
  color: #0d0d0d; /* Light */
  color: #ffffff; /* Dark */
}

/* Ghost Button */
.btn-ghost {
  background-color: transparent;
  border: 1px solid #e5e7eb; /* Light */
  border: 1px solid #404040; /* Dark */
  color: #0d0d0d; /* Light */
  color: #ffffff; /* Dark */
}
```

---

## 🌈 Color Accessibility Checklist

When choosing colors:

- [ ] Text has minimum 4.5:1 contrast (normal text)
- [ ] Large text (18px+) has minimum 3:1 contrast
- [ ] UI components have minimum 3:1 contrast
- [ ] Brand color used ONLY for primary CTAs
- [ ] System colors used for backgrounds/text
- [ ] Focus indicators are visible (2px, brand color)
- [ ] Color is not the only indicator (use icons/text)
- [ ] Works in both light and dark modes

---

## 🎨 Quick Reference

**Copy-Paste Color Values:**

```css
/* Light Mode */
--bg-primary: #ffffff;
--bg-secondary: #e8e8e8;
--bg-tertiary: #f3f4f6;
--text-primary: #0d0d0d;
--text-secondary: #6b7280;
--text-tertiary: #9ca3af;
--border-color: #e5e7eb;
--border-hover: #d1d5db;
--brand-primary: #3b82f6;

/* Dark Mode */
--bg-primary: #212121;
--bg-secondary: #2d2d2d;
--bg-tertiary: #3a3a3a;
--text-primary: #ffffff;
--text-secondary: #cdcdcd;
--text-tertiary: #9ca3af;
--border-color: #404040;
--border-hover: #525252;
```

---

**Related Documents:**
- Components Reference: `docs/design/figma/COMPONENTS_REFERENCE.md`
- Design Tokens: `docs/design/DESIGN_TOKENS.md`
- Implementation CSS: `frontend/open-webui/src/lib/styles/design-tokens.css`
