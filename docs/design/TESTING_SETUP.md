# Testing Setup Guide - Figma Components

**Last Updated:** 2025-11-22
**Framework:** Vitest + @testing-library/svelte
**Environment:** JSDOM

---

## 📦 Installation

### Prerequisites

- Node.js >= 18.13.0
- npm >= 6.0.0
- Existing Open WebUI frontend project

### Step 1: Install Testing Dependencies

```bash
cd frontend/open-webui

# Install testing libraries
npm install --save-dev @testing-library/svelte @testing-library/jest-dom jsdom @vitest/ui
```

**Dependencies Breakdown:**
- `@testing-library/svelte` - Svelte component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers for DOM assertions
- `jsdom` - JavaScript implementation of web standards (DOM environment)
- `@vitest/ui` - Interactive UI for Vitest (optional but recommended)

### Step 2: Verify Installation

```bash
npm list @testing-library/svelte @testing-library/jest-dom jsdom @vitest/ui
```

Expected output:
```
open-webui@0.6.34 D:\Crastonic\ree-ai\frontend\open-webui
├── @testing-library/jest-dom@6.x.x
├── @testing-library/svelte@5.x.x
├── @vitest/ui@1.x.x
└── jsdom@24.x.x
```

---

## ⚙️ Configuration Files

All configuration files have been created. Here's what each file does:

### 1. `vitest.config.ts` (Root Config)

**Location:** `frontend/open-webui/vitest.config.ts`

**Purpose:** Main Vitest configuration for Svelte testing

**Key Settings:**
- Uses `jsdom` environment for browser-like DOM
- Includes all `*.test.ts` and `*.spec.ts` files
- Sets up path aliases for `$lib` and `$app`
- Configures coverage reporter

### 2. `vitest.setup.ts` (Global Setup)

**Location:** `frontend/open-webui/vitest.setup.ts`

**Purpose:** Global test setup and mocks

**What it does:**
- Auto-cleanup after each test
- Mocks `window.matchMedia` (for responsive tests)
- Mocks `IntersectionObserver` (for lazy loading)
- Imports Jest DOM matchers

### 3. `__mocks__/$app/navigation.ts` (SvelteKit Mocks)

**Location:** `frontend/open-webui/__mocks__/$app/navigation.ts`

**Purpose:** Mock SvelteKit navigation functions

**Mocked Functions:**
- `goto` - Navigation function
- `invalidate`, `invalidateAll` - Cache invalidation
- `beforeNavigate`, `afterNavigate` - Navigation hooks

---

## 🧪 Test Files

### Test File Structure

```
frontend/open-webui/src/lib/components/
├── property/
│   ├── CompactPropertyCard.svelte
│   ├── CompactPropertyCard.test.ts ✅ (13 tests)
│   ├── PropertyDetailModal.svelte
│   └── PropertyDetailModal.test.ts ✅ (14 tests)
└── chat/
    ├── StructuredResponseRenderer.svelte
    └── StructuredResponseRenderer.test.ts ✅ (12 tests)
```

**Total:** 39 unit tests across 3 components

---

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests once
npm run test:frontend

# Run tests in watch mode (auto-rerun on file changes)
npm run test:frontend -- --watch

# Run tests with interactive UI
npm run test:frontend -- --ui

# Run tests with coverage report
npm run test:frontend -- --coverage
```

### Advanced Commands

```bash
# Run specific test file
npm run test:frontend src/lib/components/property/CompactPropertyCard.test.ts

# Run tests matching a pattern
npm run test:frontend -- --grep "CompactPropertyCard"

# Run tests in a specific directory
npm run test:frontend src/lib/components/property/

# Run with verbose output
npm run test:frontend -- --reporter=verbose

# Run and generate HTML coverage report
npm run test:frontend -- --coverage --coverage.reporter=html
```

---

## 🔧 Troubleshooting

### Issue 1: npm install fails

**Error:**
```
npm error Cannot read properties of null (reading 'explain')
```

**Solutions:**

1. **Clear npm cache:**
   ```bash
   npm cache clean --force
   cd frontend/open-webui
   npm install
   ```

2. **Delete node_modules and reinstall:**
   ```bash
   cd frontend/open-webui
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Install dependencies individually:**
   ```bash
   npm install --save-dev @testing-library/svelte
   npm install --save-dev @testing-library/jest-dom
   npm install --save-dev jsdom
   npm install --save-dev @vitest/ui
   ```

4. **Use a different npm registry:**
   ```bash
   npm config set registry https://registry.npmjs.org/
   npm install --save-dev @testing-library/svelte @testing-library/jest-dom jsdom @vitest/ui
   ```

### Issue 2: Tests fail with "Cannot find module '$lib'"

**Solution:** Ensure `vitest.config.ts` has correct path aliases:

```typescript
resolve: {
  alias: {
    $lib: path.resolve(__dirname, './src/lib'),
    '$app': path.resolve(__dirname, './__mocks__/$app')
  }
}
```

### Issue 3: Tests fail with "window.matchMedia is not a function"

**Solution:** Ensure `vitest.setup.ts` includes the matchMedia mock (already configured).

### Issue 4: Svelte component fails to compile in tests

**Solution:** Ensure `svelte` plugin is configured in `vitest.config.ts`:

```typescript
plugins: [svelte({ hot: !process.env.VITEST })]
```

### Issue 5: "Cannot read properties of undefined (reading '$on')"

**Solution:** This may occur with older versions of @testing-library/svelte. Update to latest:

```bash
npm install --save-dev @testing-library/svelte@latest
```

---

## 📊 Coverage Reports

### Generate Coverage

```bash
npm run test:frontend -- --coverage
```

### View HTML Coverage Report

```bash
# Generate HTML report
npm run test:frontend -- --coverage --coverage.reporter=html

# Open in browser (Windows)
start frontend/open-webui/coverage/index.html

# Open in browser (Mac)
open frontend/open-webui/coverage/index.html

# Open in browser (Linux)
xdg-open frontend/open-webui/coverage/index.html
```

### Coverage Targets

| Metric     | Target | Description                              |
| ---------- | ------ | ---------------------------------------- |
| Lines      | >80%   | % of code lines executed during tests    |
| Branches   | >75%   | % of conditional branches tested         |
| Functions  | >80%   | % of functions called during tests       |
| Statements | >80%   | % of statements executed during tests    |

---

## 🎯 Next Steps

After successful installation and test execution:

1. **Review test results:**
   ```bash
   npm run test:frontend -- --reporter=verbose
   ```

2. **Check coverage gaps:**
   ```bash
   npm run test:frontend -- --coverage
   ```

3. **Add more tests if coverage < 80%**

4. **Set up CI/CD pipeline:**
   - Add test command to GitHub Actions workflow
   - Fail build if tests fail or coverage < 80%

5. **Add E2E tests with Playwright:**
   - Install Playwright
   - Write E2E tests for full user flows
   - Test across browsers (Chrome, Firefox, Safari)

---

## 🔗 Additional Resources

### Documentation

- **Test Cases Catalog:** `docs/design/TEST_CASES.md`
- **Design Tokens:** `docs/design/DESIGN_TOKENS.md`
- **Component Mapping:** `docs/design/OPENAI_APPS_SDK_MAPPING.md`

### External Links

- **Vitest:** https://vitest.dev
- **Testing Library (Svelte):** https://testing-library.com/docs/svelte-testing-library/intro
- **Jest DOM Matchers:** https://github.com/testing-library/jest-dom
- **Svelte Testing Guide:** https://svelte.dev/docs/testing

---

## 🐛 Debugging Tests

### Enable Debug Mode

```bash
# Run tests with debug output
DEBUG=* npm run test:frontend

# Run specific test with console output
npm run test:frontend -- --reporter=verbose src/lib/components/property/CompactPropertyCard.test.ts
```

### Using Vitest UI for Debugging

```bash
# Start Vitest UI (best for debugging)
npm run test:frontend -- --ui

# Then open browser at http://localhost:51204/__vitest__/
```

**Vitest UI Features:**
- See test results in real-time
- Click on failed tests to see stack traces
- Filter tests by name or status
- View code coverage inline

---

## ✅ Installation Checklist

Before running tests, ensure:

- [ ] Node.js >= 18.13.0 installed
- [ ] npm >= 6.0.0 installed
- [ ] Dependencies installed successfully
- [ ] `vitest.config.ts` exists
- [ ] `vitest.setup.ts` exists
- [ ] `__mocks__/$app/navigation.ts` exists
- [ ] All 3 test files exist (CompactPropertyCard, PropertyDetailModal, StructuredResponseRenderer)
- [ ] No TypeScript errors in test files
- [ ] Can run `npm run test:frontend` without errors

---

## 🎓 Writing Your Own Tests

### Test Template

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import YourComponent from './YourComponent.svelte';

describe('YourComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render correctly', () => {
    render(YourComponent, { props: { /* your props */ } });

    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle click events', async () => {
    const onClick = vi.fn();
    render(YourComponent, { props: { onClick } });

    await fireEvent.click(screen.getByRole('button'));

    expect(onClick).toHaveBeenCalled();
  });
});
```

### Best Practices

1. **Use semantic queries:** `getByRole`, `getByLabelText` over `getByTestId`
2. **Test user behavior:** Focus on what users see and do
3. **Avoid implementation details:** Don't test internal state
4. **Clean up:** Use `beforeEach` and `afterEach` hooks
5. **Mock external dependencies:** Use `vi.fn()` and `vi.mock()`
6. **Test accessibility:** Always verify ARIA attributes

---

**Need help?** Check `docs/design/TEST_CASES.md` for test examples and best practices.
