# Figma Design System Documentation

**Source:** OpenAI Apps SDK - Apps in ChatGPT
**Figma File ID:** `4JSHQqDBBms4mAvprmbN2b`
**Last Extracted:** 2025-11-22

---

## 📁 Documentation Structure

This directory contains the complete design system extracted from the official OpenAI Apps SDK Figma file. All specifications are local and can be used without requiring Figma API access.

### Files in this Directory

| File | Purpose | Use When |
|------|---------|----------|
| **COMPONENTS_REFERENCE.md** | Complete component specifications | Building new UI components |
| **COLOR_PALETTE.md** | All colors with contrast ratios | Styling components, checking accessibility |
| **IMPLEMENTATION_PATTERNS.md** | Code examples and patterns | Writing Svelte/TypeScript code |
| **README.md** | This file - overview and usage | Getting started |

---

## 🎯 Quick Start

### For Designers

**View Component Specs:**
1. Open `COMPONENTS_REFERENCE.md`
2. Find the component you need (Inline Card, Inspector, etc.)
3. Review dimensions, spacing, typography
4. Check color usage and states

**Check Colors:**
1. Open `COLOR_PALETTE.md`
2. Find the color you need
3. Verify contrast ratios (WCAG compliance)
4. Use CSS variable names in code

### For Developers

**Implement New Component:**
1. Read component spec in `COMPONENTS_REFERENCE.md`
2. Copy code pattern from `IMPLEMENTATION_PATTERNS.md`
3. Use design tokens from `frontend/open-webui/src/lib/styles/design-tokens.css`
4. Follow accessibility checklist

**Quick Reference:**
```bash
# Component dimensions → COMPONENTS_REFERENCE.md
# Colors & contrast → COLOR_PALETTE.md
# Code patterns → IMPLEMENTATION_PATTERNS.md
# CSS variables → /frontend/open-webui/src/lib/styles/design-tokens.css
```

---

## 📊 Component Catalog

### Available Components

| Component | Dimensions | Use Case | Reference |
|-----------|------------|----------|-----------|
| **🌁 Inline Card** | 361×336px | Rich content display | COMPONENTS_REFERENCE.md §1 |
| **📦 Entity Card** | 345×345px | Grid layouts | COMPONENTS_REFERENCE.md §2 |
| **🎠 Inline Carousel** | 100% width | Multiple cards | COMPONENTS_REFERENCE.md §3 |
| **🔎 Inspector** | 480px width | Detail modal | COMPONENTS_REFERENCE.md §4 |
| **📱 Compact Card** | 400px max | Inline chat | COMPONENTS_REFERENCE.md §5 |

### Component Decision Tree

```
Need to display entity?
├─ In chat inline? → Compact Card (400px max)
├─ Rich content? → Inline Card (361×336px)
├─ Grid layout? → Entity Card (345×345px)
└─ Multiple items? → Carousel (100% width)

Need detail view?
└─ Use Inspector (480px modal)
```

---

## 🎨 Design System At a Glance

### Colors

**Light Mode:**
- Background: `#ffffff`, `#e8e8e8`, `#f3f4f6`
- Text: `#0d0d0d`, `#6b7280`, `#9ca3af`
- Border: `#e5e7eb`, `#d1d5db`
- Brand (CTA only): `#3b82f6`

**Dark Mode:**
- Background: `#212121`, `#2d2d2d`, `#3a3a3a`
- Text: `#ffffff`, `#cdcdcd`, `#9ca3af`
- Border: `#404040`, `#525252`

**→ Full palette:** `COLOR_PALETTE.md`

### Spacing (Grid-based, 4px)

```
4px   8px   12px  16px  20px  24px  32px  48px  64px
--space-1 → --space-2 → --space-3 → --space-4 → ...
```

**→ Complete system:** `COMPONENTS_REFERENCE.md §Spacing`

### Typography

| Element | Size | Weight |
|---------|------|--------|
| H1 | 30px | Bold (700) |
| H2 | 24px | Bold (700) |
| Body | 16px | Normal (400) |
| Small | 14px | Normal (400) |
| Button | 14px | Semibold (600) |

**→ Full typography:** `COMPONENTS_REFERENCE.md §Typography`

---

## ✅ OpenAI Compliance Checklist

When implementing components, ensure:

### Design
- [ ] Uses system colors (not custom colors)
- [ ] Brand color ONLY on primary CTAs
- [ ] Grid-based spacing (multiples of 4px)
- [ ] System fonts (no custom typefaces)
- [ ] Follows component dimensions from Figma

### Accessibility (WCAG AA)
- [ ] Text contrast ≥4.5:1 (normal text)
- [ ] Text contrast ≥3:1 (large text 18px+)
- [ ] UI contrast ≥3:1
- [ ] Focus indicators visible (2px outline)
- [ ] Keyboard navigation works
- [ ] ARIA labels on interactive elements
- [ ] Semantic HTML

### Functionality
- [ ] Works in light and dark modes
- [ ] Responsive on mobile
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Empty states handled

**→ Full checklist:** `IMPLEMENTATION_PATTERNS.md §Checklist`

---

## 🔧 Development Workflow

### Step 1: Review Specification

```bash
# Find your component
cat COMPONENTS_REFERENCE.md | grep -A 50 "Your Component"

# Check dimensions, colors, spacing
```

### Step 2: Copy Pattern

```bash
# Get code template
cat IMPLEMENTATION_PATTERNS.md | grep -A 100 "Pattern X"
```

### Step 3: Use Design Tokens

```svelte
<style>
  .my-component {
    padding: var(--space-4);
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
  }
</style>
```

### Step 4: Test

- [ ] Visual comparison with Figma
- [ ] Dark mode
- [ ] Mobile responsive
- [ ] Accessibility audit
- [ ] Cross-browser testing

---

## 📖 Figma File Information

### Source Details

**File:** Apps in ChatGPT • Components & Templates
**File Key:** `4JSHQqDBBms4mAvprmbN2b`
**Owner:** OpenAI
**Access:** Public (view only)

### Extraction Method

```bash
# Figma API was used to extract:
curl -H "X-Figma-Token: YOUR_TOKEN" \
  "https://api.figma.com/v1/files/4JSHQqDBBms4mAvprmbN2b"

# Data processed and saved as:
# - COMPONENTS_REFERENCE.md (component specs)
# - COLOR_PALETTE.md (color system)
# - IMPLEMENTATION_PATTERNS.md (code patterns)
```

### What Was Extracted

✅ **Component Dimensions** (exact pixel values)
✅ **Color System** (hex codes, contrast ratios)
✅ **Spacing System** (grid-based, 4px)
✅ **Typography** (sizes, weights, line heights)
✅ **Shadows** (elevation system)
✅ **Transitions** (animation speeds)
✅ **Z-Index Layers** (stacking order)

❌ **Not Extracted:**
- Auto-layout rules (interpreted as Flexbox)
- Component instances (only master components)
- Figma-specific features (constraints, etc.)

---

## 🔄 Keeping Documentation Updated

### When to Update

Update this documentation when:
1. OpenAI releases new Apps SDK components
2. Design tokens change in Figma
3. New component patterns are needed
4. Accessibility standards update

### How to Update

**Option 1: Manual Update**
1. Review Figma file for changes
2. Update relevant .md files
3. Update CSS design tokens
4. Commit changes with clear message

**Option 2: Re-extract from Figma**
1. Get fresh Figma token
2. Run extraction script (if available)
3. Compare changes with current docs
4. Merge updates

**Always:**
- Update "Last Updated" dates
- Document what changed
- Verify implementations still match
- Test existing components

---

## 📚 Related Documentation

### In This Repository

| Document | Location | Purpose |
|----------|----------|---------|
| **Design Tokens CSS** | `frontend/open-webui/src/lib/styles/design-tokens.css` | Actual CSS variables |
| **OpenAI Design Standards** | `docs/design/OPENAI_DESIGN_STANDARDS.md` | Design principles |
| **Component Mapping** | `docs/design/OPENAI_APPS_SDK_MAPPING.md` | OpenAI → REE AI mapping |
| **Implementation Guide** | `docs/implementation/STRUCTURED_RESPONSE_IMPLEMENTATION.md` | Full implementation |
| **Testing Guide** | `docs/testing/TESTING_GUIDE.md` | How to test |

### External Resources

- [OpenAI Apps Documentation](https://platform.openai.com/docs/guides/apps)
- [WCAG AA Guidelines](https://www.w3.org/WAI/WCAG2AA-Conformance)
- [Figma API Docs](https://www.figma.com/developers/api)

---

## 🎓 Learning Resources

### For New Developers

**Start here:**
1. Read `COMPONENTS_REFERENCE.md` overview
2. Review `COLOR_PALETTE.md` for color usage
3. Copy a pattern from `IMPLEMENTATION_PATTERNS.md`
4. Build a simple component
5. Test against checklist

**Example Exercise:**
```
Build a CompactPropertyCard component:
1. Read spec in COMPONENTS_REFERENCE.md §5
2. Copy pattern from IMPLEMENTATION_PATTERNS.md §Pattern 2
3. Use colors from COLOR_PALETTE.md
4. Test with docs/testing/TESTING_GUIDE.md
```

### For Designers

**Start here:**
1. Open Figma file for visual reference
2. Use this documentation for precise specs
3. Check color contrast in `COLOR_PALETTE.md`
4. Verify accessibility standards

---

## ❓ FAQ

**Q: Can I use custom colors?**
A: No. Always use system colors from `COLOR_PALETTE.md`. Brand color only for primary CTAs.

**Q: What if a component doesn't match Figma exactly?**
A: Prioritize: 1) Accessibility, 2) Functionality, 3) Visual match. Document deviations.

**Q: How do I add a new component?**
A: 1) Check if Figma has it, 2) Extract specs, 3) Add to COMPONENTS_REFERENCE.md, 4) Create pattern in IMPLEMENTATION_PATTERNS.md

**Q: Do I need Figma access?**
A: No. All specs are in these .md files. Figma access only needed for updates.

**Q: What about responsive design?**
A: Follow mobile-first. Breakpoints: 480px (mobile), 768px (tablet), 769px+ (desktop).

---

## 🤝 Contributing

When adding to this documentation:

1. **Follow the format** - Match existing structure
2. **Be specific** - Include exact values (px, hex codes)
3. **Show examples** - Code snippets help
4. **Check accessibility** - Verify contrast ratios
5. **Update README** - Add to catalog if new component
6. **Update date** - "Last Updated" in file header

**File naming:**
- Use SCREAMING_SNAKE_CASE.md
- Be descriptive: `BUTTON_PATTERNS.md`, not `buttons.md`

---

## 📧 Support

**Questions about:**
- **Design specs** → See COMPONENTS_REFERENCE.md
- **Colors** → See COLOR_PALETTE.md
- **Implementation** → See IMPLEMENTATION_PATTERNS.md
- **Testing** → See docs/testing/TESTING_GUIDE.md

**Still stuck?**
- Check existing implementations in `frontend/open-webui/src/lib/components/`
- Review test examples in `docs/testing/TESTING_GUIDE.md`
- Ask in team chat with specific question + file reference

---

**Last Updated:** 2025-11-22
**Maintained By:** Development Team
**Version:** 1.0.0
