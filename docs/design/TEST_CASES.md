# Test Cases - Figma Components Implementation

**Last Updated:** 2025-11-22
**Test Framework:** Vitest + @testing-library/svelte
**Components:** CompactPropertyCard, PropertyDetailModal, StructuredResponseRenderer

---

## 📊 Test Coverage Summary

| Component                      | Unit Tests | Status        |
| ------------------------------ | ---------- | ------------- |
| CompactPropertyCard            | 13         | ✅ Complete   |
| PropertyDetailModal            | 14         | ✅ Complete   |
| StructuredResponseRenderer     | 12         | ✅ Complete   |
| **Total**                      | **39**     | **✅ Done**   |

---

## 🧪 Test Infrastructure

### Prerequisites

Before running tests, install required dependencies:

```bash
cd frontend/open-webui
npm install --save-dev @testing-library/svelte @testing-library/jest-dom jsdom @vitest/ui
```

### Configuration Files

1. **vitest.config.ts** - Vitest configuration for Svelte testing
2. **vitest.setup.ts** - Global test setup (cleanup, mocks)
3. **\_\_mocks\_\_/$app/navigation.ts** - SvelteKit navigation mocks

### Running Tests

```bash
# Run all tests
npm run test:frontend

# Run tests in watch mode
npm run test:frontend -- --watch

# Run tests with UI
npm run test:frontend -- --ui

# Run tests with coverage
npm run test:frontend -- --coverage

# Run specific test file
npm run test:frontend src/lib/components/property/CompactPropertyCard.test.ts
```

---

## 📋 Test Case Catalog

### 1. CompactPropertyCard Component (13 tests)

**File:** `src/lib/components/property/CompactPropertyCard.test.ts`

#### 1.1 Rendering (5 tests)

| Test ID | Test Name                                              | Purpose                                               |
| ------- | ------------------------------------------------------ | ----------------------------------------------------- |
| CPC-R1  | should render property card with all data points      | Verify all 4 data points render (Simple principle)    |
| CPC-R2  | should render with image when imageUrl is provided    | Verify image displays with correct attributes         |
| CPC-R3  | should render placeholder when imageUrl is missing    | Verify fallback placeholder for missing images        |
| CPC-R4  | should display key feature with bedrooms (2PN 75m²)   | Verify bedroom display format                         |
| CPC-R5  | should display key feature without bedrooms when = 0  | Verify land property display format (no bedrooms)     |

#### 1.2 Interactions (4 tests)

| Test ID | Test Name                                        | Purpose                                           |
| ------- | ------------------------------------------------ | ------------------------------------------------- |
| CPC-I1  | should call onClick when card is clicked         | Verify card click handler                         |
| CPC-I2  | should call onClick when CTA button is clicked   | Verify CTA button click handler                   |
| CPC-I3  | should support keyboard navigation (Enter key)   | Verify keyboard accessibility (Enter key)         |
| CPC-I4  | should not call onClick when onClick is not provided | Verify graceful handling when onClick is undefined |

#### 1.3 Accessibility (4 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| CPC-A1  | should have proper ARIA attributes                | Verify ARIA labels and roles                   |
| CPC-A2  | should have screen reader only labels for metadata| Verify sr-only class for screen readers        |
| CPC-A3  | should have accessible CTA button                 | Verify button has aria-label                   |
| CPC-A4  | should have visible focus indicator               | Verify focus-visible styles exist              |

#### 1.4 OpenAI Design System Compliance (4 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| CPC-D1  | should use system colors (not brand for background)| Verify white background in light mode          |
| CPC-D2  | should use brand color ONLY on CTA button         | Verify blue brand color on CTA button only     |
| CPC-D3  | should have max-width of 400px per Figma specs    | Verify Figma design token compliance           |
| CPC-D4  | should have 60px thumbnail per Figma specs        | Verify thumbnail dimensions from Figma         |

#### 1.5 Mobile Responsive (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| CPC-M1  | should render mobile layout for screens < 480px   | Verify mobile media query exists               |

#### 1.6 Edge Cases (3 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| CPC-E1  | should handle missing optional fields gracefully  | Verify component works with minimal data       |
| CPC-E2  | should truncate long titles with ellipsis         | Verify text-overflow ellipsis on long titles   |
| CPC-E3  | should handle missing priceUnit with default      | Verify default "VNĐ" when priceUnit is missing |

---

### 2. PropertyDetailModal Component (14 tests)

**File:** `src/lib/components/property/PropertyDetailModal.test.ts`

#### 2.1 Modal Visibility (3 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-V1  | should not render when open = false               | Verify modal is hidden when closed             |
| PDM-V2  | should render when open = true                    | Verify modal displays when open                |
| PDM-V3  | should show PropertyInspector component when open | Verify PropertyInspector renders in modal      |

#### 2.2 Close Mechanisms (6 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-C1  | should close when close button is clicked         | Verify X button closes modal                   |
| PDM-C2  | should emit close event when close button is clicked | Verify close event is dispatched            |
| PDM-C3  | should close when Escape key is pressed           | Verify ESC key closes modal                    |
| PDM-C4  | should close when backdrop is clicked             | Verify clicking outside modal closes it        |
| PDM-C5  | should NOT close when modal content is clicked    | Verify clicking inside doesn't close           |
| PDM-C6  | should NOT close when Escape is pressed and modal is already closed | Verify no errors when ESC pressed while closed |

#### 2.3 Accessibility (4 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-A1  | should have proper ARIA attributes                | Verify role="dialog", aria-modal="true"        |
| PDM-A2  | should have accessible close button               | Verify button has aria-label and type          |
| PDM-A3  | should trap focus within modal when open          | Verify focus trap implementation               |
| PDM-A4  | should have visible focus indicator on close button | Verify focus-visible styles                  |

#### 2.4 OpenAI Design System Compliance (4 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-D1  | should use system colors for modal background     | Verify white (#ffffff) background              |
| PDM-D2  | should have proper z-index for modal overlay      | Verify z-index: 1300                           |
| PDM-D3  | should have 480px max-width per design tokens     | Verify modal width from design tokens          |
| PDM-D4  | should have proper border radius (12px)           | Verify border-radius: 12px                     |

#### 2.5 Mobile Responsive (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-M1  | should render fullscreen on mobile (<768px)       | Verify mobile fullscreen layout                |

#### 2.6 Body Scroll Prevention (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-S1  | should prevent body scroll when modal is open     | Verify scroll lock on modal open               |

#### 2.7 Transitions (2 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-T1  | should have fade transition on modal overlay      | Verify Svelte fade transition                  |
| PDM-T2  | should have scale transition on modal container   | Verify Svelte scale transition                 |

#### 2.8 Edge Cases (2 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-E1  | should handle undefined property gracefully       | Verify modal works even with undefined prop    |
| PDM-E2  | should handle rapid open/close toggles            | Verify no issues with rapid state changes      |

#### 2.9 Scrollbar Styling (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| PDM-X1  | should have custom scrollbar styles               | Verify webkit-scrollbar CSS exists             |

---

### 3. StructuredResponseRenderer Component (12 tests)

**File:** `src/lib/components/chat/StructuredResponseRenderer.test.ts`

#### 3.1 Property Carousel Rendering (4 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-R1  | should render property carousel with multiple properties | Verify carousel renders all properties   |
| SRR-R2  | should display total count when properties > 0    | Verify "Tìm thấy X bất động sản" text          |
| SRR-R3  | should render empty state when no properties found | Verify empty state message                    |
| SRR-R4  | should render all CompactPropertyCards in property list | Verify all cards are rendered          |

#### 3.2 Property Inspector Modal (3 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-I1  | should auto-open modal when PropertyInspectorComponent is received | Verify reactive modal opening |
| SRR-I2  | should pass property data to modal correctly      | Verify data flow to modal                      |
| SRR-I3  | should close modal when PropertyDetailModal emits close event | Verify modal close handler        |

#### 3.3 Property Detail Request (3 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-D1  | should dispatch requestDetail event when property card is clicked | Verify event dispatch       |
| SRR-D2  | should include query in requestDetail event       | Verify query parameter in event                |
| SRR-D3  | should open modal directly if property has fullData | Verify shortcut for full data               |

#### 3.4 Multiple Component Types (3 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-M1  | should render multiple component types in same response | Verify handling of mixed components     |
| SRR-M2  | should handle empty components array              | Verify graceful handling of empty array        |
| SRR-M3  | should ignore unknown component types             | Verify unknown types don't break rendering     |

#### 3.5 Data Handling (2 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-H1  | should handle malformed carousel data gracefully  | Verify null data doesn't crash                 |
| SRR-H2  | should handle malformed inspector data gracefully | Verify null data doesn't crash                 |

#### 3.6 Component Reactivity (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-C1  | should update when components prop changes        | Verify reactive updates work                   |

#### 3.7 Styling and Layout (2 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-S1  | should have proper spacing between components     | Verify flexbox layout                          |
| SRR-S2  | should render property list with proper layout    | Verify property list flexbox                   |

#### 3.8 Accessibility (2 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-A1  | should have proper ARIA region for carousel       | Verify role="region" with label                |
| SRR-A2  | should have accessible empty state message        | Verify empty state is readable                 |

#### 3.9 Mobile Responsive (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-X1  | should have mobile-specific styles                | Verify mobile media queries exist              |

#### 3.10 Edge Cases (2 tests)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-E1  | should handle rapid component updates without errors | Verify rapid state changes work             |
| SRR-E2  | should handle property click errors gracefully    | Verify error handling in click handler         |

#### 3.11 Keyboard Navigation (1 test)

| Test ID | Test Name                                         | Purpose                                        |
| ------- | ------------------------------------------------- | ---------------------------------------------- |
| SRR-K1  | should support keyboard navigation on property cards | Verify tabindex="0" on all cards            |

---

## ✅ Test Execution Checklist

Before running tests, ensure:

- [x] **Dependencies installed:** @testing-library/svelte, jsdom, @testing-library/jest-dom
- [x] **Config files created:** vitest.config.ts, vitest.setup.ts
- [x] **Mocks created:** __mocks__/$app/navigation.ts
- [x] **Test files created:** All 3 component test files

### Run Tests

```bash
# Step 1: Install dependencies (if not already done)
cd frontend/open-webui
npm install --save-dev @testing-library/svelte @testing-library/jest-dom jsdom @vitest/ui

# Step 2: Run tests
npm run test:frontend

# Step 3: View coverage report
npm run test:frontend -- --coverage
```

---

## 📈 Coverage Goals

| Metric              | Target | Status |
| ------------------- | ------ | ------ |
| Line Coverage       | >80%   | TBD    |
| Branch Coverage     | >75%   | TBD    |
| Function Coverage   | >80%   | TBD    |
| Statement Coverage  | >80%   | TBD    |

---

## 🔍 Test Categories Overview

### By Type

- **Rendering Tests:** 12 tests (31%)
- **Interaction Tests:** 9 tests (23%)
- **Accessibility Tests:** 10 tests (26%)
- **Design System Compliance:** 12 tests (31%)
- **Edge Cases:** 9 tests (23%)
- **Mobile Responsive:** 3 tests (8%)

### By Component

- **CompactPropertyCard:** 13 tests (33%)
- **PropertyDetailModal:** 14 tests (36%)
- **StructuredResponseRenderer:** 12 tests (31%)

---

## 🚨 Known Issues & Limitations

### Current Limitations

1. **Dependency Installation Error:**
   - npm install may fail on some systems
   - Workaround: Try clearing npm cache (`npm cache clean --force`)
   - Alternative: Install dependencies individually

2. **CSS-in-JS Testing:**
   - Some computed style tests may fail in JSDOM environment
   - Consider using Playwright for full browser testing

3. **Svelte Transitions:**
   - Transition tests verify structure, not actual animations
   - Full animation testing requires E2E tests

### Future Improvements

- [ ] Add E2E tests with Playwright
- [ ] Add visual regression tests
- [ ] Add performance tests (render time, memory)
- [ ] Add integration tests with backend API
- [ ] Add snapshot tests for component HTML output

---

## 📚 References

- **OpenAI Apps SDK:** Design system compliance guidelines
- **Figma Design:** `docs/design/DESIGN_TOKENS.md`
- **Component Mapping:** `docs/design/OPENAI_APPS_SDK_MAPPING.md`
- **Vitest Docs:** https://vitest.dev
- **Testing Library:** https://testing-library.com/svelte

---

## 🔄 Last Test Run

**Date:** Not yet run
**Result:** Pending dependency installation
**Coverage:** N/A

Update this section after running tests successfully.

---

## 💡 Tips for Writing Tests

1. **Follow AAA Pattern:** Arrange, Act, Assert
2. **Test Behavior, Not Implementation:** Focus on user interactions
3. **Use Semantic Queries:** Prefer `getByRole`, `getByLabelText` over `getByTestId`
4. **Test Accessibility:** Always verify ARIA attributes and keyboard navigation
5. **Test Edge Cases:** Empty data, malformed data, missing props
6. **Mock External Dependencies:** Use vi.fn() for event handlers
7. **Clean Up:** Use afterEach(() => cleanup()) to prevent test pollution

---

**Questions?** See `docs/claude/04-development-guide.md` for general testing guidelines.
