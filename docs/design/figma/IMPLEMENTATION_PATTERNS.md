# Implementation Patterns - OpenAI Apps SDK

**Source:** Figma File `4JSHQqDBBms4mAvprmbN2b`
**Last Updated:** 2025-11-22

---

## 📋 Overview

This document provides code patterns and implementation examples for OpenAI Apps SDK components. Use these as templates when building new components.

---

## 🎯 Component Implementation Patterns

### Pattern 1: Inline Card (Svelte)

```svelte
<script lang="ts">
  /**
   * Inline Card - OpenAI Apps SDK Pattern
   *
   * Displays entity information with image, title, subtitle, and CTA
   */

  export let entity: {
    id: string;
    title: string;
    subtitle: string;
    imageUrl: string;
    ctaText?: string;
  };

  export let onAction: ((entity: any) => void) | undefined = undefined;

  function handleAction() {
    if (onAction) onAction(entity);
  }
</script>

<article class="inline-card">
  <!-- Hero Image -->
  <div class="card-image">
    {#if entity.imageUrl}
      <img src={entity.imageUrl} alt={entity.title} loading="lazy" />
    {:else}
      <div class="image-placeholder" role="img" aria-label="No image">
        <svg><!-- Placeholder icon --></svg>
      </div>
    {/if}
  </div>

  <!-- Content -->
  <div class="card-content">
    <h3 class="card-title">{entity.title}</h3>
    <p class="card-subtitle">{entity.subtitle}</p>
  </div>

  <!-- CTA Button -->
  <button class="btn-primary card-cta" on:click={handleAction}>
    {entity.ctaText || 'View Details'}
  </button>
</article>

<style>
  .inline-card {
    width: 361px;
    height: 336px;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    padding: var(--space-4);
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 24px;
    transition: border-color var(--transition-fast);
  }

  .inline-card:hover {
    border-color: var(--border-hover);
  }

  .card-image {
    width: 329px;
    height: 200px;
    border-radius: 16px;
    overflow: hidden;
  }

  .card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-secondary);
    color: var(--text-tertiary);
  }

  .card-title {
    font-size: var(--text-xl);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    margin: 0;
  }

  .card-subtitle {
    font-size: var(--text-sm);
    font-weight: var(--font-normal);
    color: var(--text-secondary);
    margin: 0;
  }

  .card-cta {
    margin-top: auto;
  }

  /* Dark mode handled by CSS variables */
</style>
```

---

### Pattern 2: Compact Card (Svelte)

```svelte
<script lang="ts">
  /**
   * Compact Card - REE AI Custom Pattern
   *
   * Minimal footprint card for inline chat display
   * Max 4 data points + 1 CTA (OpenAI "Simple" principle)
   */

  export let data: {
    id: string;
    title: string;
    location: string;
    keyFeature: string;
    price: string;
    imageUrl?: string;
  };

  export let onClick: ((data: any) => void) | undefined = undefined;
</script>

<article
  class="compact-card"
  role="button"
  tabindex="0"
  on:click={() => onClick?.(data)}
  on:keypress={(e) => e.key === 'Enter' && onClick?.(data)}
>
  <!-- Thumbnail (60x60px) -->
  {#if data.imageUrl}
    <img src={data.imageUrl} alt={data.title} class="thumbnail" />
  {:else}
    <div class="thumbnail placeholder">
      <svg><!-- Icon --></svg>
    </div>
  {/if}

  <!-- Content (3 data points) -->
  <div class="content">
    <h4 class="title">{data.title}</h4>
    <p class="metadata">📍 {data.location} • {data.keyFeature}</p>
    <p class="price"><strong>{data.price}</strong></p>
  </div>

  <!-- CTA (1 button) -->
  <button class="btn-primary cta">
    View →
  </button>
</article>

<style>
  .compact-card {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-3);
    max-width: 400px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    align-items: center;
    cursor: pointer;
    transition: border-color var(--transition-fast);
  }

  .compact-card:hover {
    border-color: var(--border-hover);
  }

  .thumbnail {
    width: 60px;
    height: 60px;
    min-width: 60px;
    border-radius: 6px;
    object-fit: cover;
  }

  .content {
    flex: 1;
    min-width: 0; /* Allow truncation */
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .title {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .metadata {
    font-size: var(--text-xs);
    color: var(--text-secondary);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .price {
    font-size: var(--text-sm);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    margin: 0;
  }

  .cta {
    padding: var(--space-2) var(--space-4);
    white-space: nowrap;
  }

  /* Mobile responsive */
  @media (max-width: 480px) {
    .compact-card {
      flex-direction: column;
      align-items: stretch;
    }

    .thumbnail {
      width: 100%;
      height: 150px;
    }

    .cta {
      width: 100%;
    }
  }
</style>
```

---

### Pattern 3: Inspector Modal (Svelte)

```svelte
<script lang="ts">
  /**
   * Inspector Modal - OpenAI Apps SDK Pattern
   *
   * Full-screen detail view with close functionality
   */

  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';

  export let entity: any;
  export let open: boolean = false;

  const dispatch = createEventDispatcher();

  function handleClose() {
    open = false;
    dispatch('close');
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) handleClose();
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) handleClose();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
  <div
    class="modal-overlay"
    role="dialog"
    aria-modal="true"
    on:click={handleBackdropClick}
    transition:fade={{ duration: 200 }}
  >
    <div class="modal-container" transition:scale={{ duration: 200, start: 0.95 }}>
      <!-- Close Button -->
      <button
        class="close-button"
        on:click={handleClose}
        aria-label="Close"
      >
        <svg><!-- X icon --></svg>
      </button>

      <!-- Hero Image -->
      <img src={entity.imageUrl} alt={entity.title} class="hero-image" />

      <!-- Content -->
      <div class="modal-content">
        <h2 class="modal-title">{entity.title}</h2>
        <p class="modal-subtitle">{entity.subtitle}</p>

        <div class="description">
          {entity.description}
        </div>

        <!-- Sections -->
        {#each entity.sections as section}
          <section class="info-section">
            <h3 class="section-title">{section.title}</h3>
            <dl class="attribute-list">
              {#each section.attributes as attr}
                <div class="attribute">
                  <dt>{attr.label}</dt>
                  <dd>{attr.value}</dd>
                </div>
              {/each}
            </dl>
          </section>
        {/each}

        <!-- Action -->
        <button class="btn-primary modal-action">
          {entity.actionText}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    inset: 0;
    z-index: var(--z-modal);
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-4);
    overflow-y: auto;
  }

  .modal-container {
    position: relative;
    width: 100%;
    max-width: 480px;
    max-height: 80vh;
    background: var(--bg-primary);
    border-radius: 12px;
    padding: var(--space-6);
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
  }

  .close-button {
    position: absolute;
    top: var(--space-4);
    right: var(--space-4);
    width: 32px;
    height: 32px;
    padding: 0;
    background: rgba(0, 0, 0, 0.05);
    border: none;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color var(--transition-fast);
  }

  .close-button:hover {
    background: rgba(0, 0, 0, 0.1);
  }

  .hero-image {
    width: 100%;
    height: 320px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: var(--space-4);
  }

  .modal-title {
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
    color: var(--text-primary);
    margin: 0 0 var(--space-2) 0;
  }

  .modal-subtitle {
    font-size: var(--text-base);
    color: var(--text-secondary);
    margin: 0 0 var(--space-3) 0;
  }

  .description {
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    color: var(--text-primary);
    margin-bottom: var(--space-5);
  }

  .info-section {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: var(--space-4);
    margin-bottom: var(--space-4);
  }

  .section-title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin: 0 0 var(--space-3) 0;
  }

  .attribute-list {
    display: grid;
    gap: var(--space-2);
  }

  .attribute {
    display: flex;
    justify-content: space-between;
    gap: var(--space-4);
  }

  .attribute dt {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-secondary);
  }

  .attribute dd {
    font-size: var(--text-sm);
    color: var(--text-primary);
    text-align: right;
  }

  .modal-action {
    width: 100%;
    margin-top: var(--space-4);
  }

  /* Mobile */
  @media (max-width: 768px) {
    .modal-overlay {
      padding: 0;
    }

    .modal-container {
      max-width: 100%;
      max-height: 100vh;
      border-radius: 0;
      height: 100%;
    }
  }
</style>
```

---

### Pattern 4: Carousel Container (Svelte)

```svelte
<script lang="ts">
  /**
   * Carousel - OpenAI Apps SDK Pattern
   *
   * Horizontal scrolling container with optional navigation
   */

  export let items: any[];
  export let showNavigation: boolean = true;

  let scrollContainer: HTMLElement;
  let canScrollLeft = false;
  let canScrollRight = true;

  function scroll(direction: 'left' | 'right') {
    const scrollAmount = 377; // card width (361) + gap (16)
    scrollContainer.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    });
  }

  function checkScroll() {
    if (!scrollContainer) return;

    canScrollLeft = scrollContainer.scrollLeft > 0;
    canScrollRight =
      scrollContainer.scrollLeft <
      scrollContainer.scrollWidth - scrollContainer.clientWidth - 10;
  }
</script>

<div class="carousel-wrapper">
  {#if showNavigation && canScrollLeft}
    <button
      class="nav-button nav-left"
      on:click={() => scroll('left')}
      aria-label="Scroll left"
    >
      ←
    </button>
  {/if}

  <div
    class="carousel-container"
    bind:this={scrollContainer}
    on:scroll={checkScroll}
  >
    <div class="carousel-track">
      {#each items as item (item.id)}
        <slot {item} />
      {/each}
    </div>
  </div>

  {#if showNavigation && canScrollRight}
    <button
      class="nav-button nav-right"
      on:click={() => scroll('right')}
      aria-label="Scroll right"
    >
      →
    </button>
  {/if}
</div>

<style>
  .carousel-wrapper {
    position: relative;
    width: 100%;
    max-width: 800px;
  }

  .carousel-container {
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .carousel-container::-webkit-scrollbar {
    display: none;
  }

  .carousel-track {
    display: flex;
    gap: var(--space-4);
    padding: var(--space-2) 0;
  }

  .nav-button {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
    background: rgba(0, 0, 0, 0.05);
    border: none;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    transition: background-color var(--transition-fast);
  }

  .nav-button:hover {
    background: rgba(0, 0, 0, 0.1);
  }

  .nav-left {
    left: -16px;
  }

  .nav-right {
    right: -16px;
  }

  @media (prefers-color-scheme: dark) {
    .nav-button {
      background: rgba(255, 255, 255, 0.1);
    }

    .nav-button:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
</style>
```

---

## 🎨 Common CSS Patterns

### Button Styles

```css
/* Primary Button (Brand Color) */
.btn-primary {
  padding: var(--space-2) var(--space-4);
  background-color: var(--brand-primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.btn-primary:hover {
  background-color: var(--brand-primary-hover);
}

.btn-primary:active {
  background-color: var(--brand-primary-active);
}

.btn-primary:focus-visible {
  outline: 2px solid var(--brand-primary);
  outline-offset: 2px;
}

/* Secondary Button */
.btn-secondary {
  padding: var(--space-2) var(--space-4);
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: background-color var(--transition-fast),
              border-color var(--transition-fast);
}

.btn-secondary:hover {
  background-color: var(--bg-tertiary);
  border-color: var(--border-hover);
}

/* Ghost Button */
.btn-ghost {
  padding: var(--space-2) var(--space-4);
  background-color: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.btn-ghost:hover {
  border-color: var(--border-hover);
}
```

### Card Hover Effects

```css
.card {
  border: 1px solid var(--border-color);
  transition: border-color var(--transition-fast),
              box-shadow var(--transition-fast);
}

.card:hover {
  border-color: var(--border-hover);
  box-shadow: var(--shadow-md);
}
```

### Text Truncation

```css
/* Single line */
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Multiple lines (2 lines) */
.truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

### Responsive Grids

```css
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(345px, 1fr));
  gap: var(--space-4);
}

@media (max-width: 768px) {
  .grid-auto {
    grid-template-columns: 1fr;
  }
}
```

---

## 🔧 TypeScript Patterns

### Component Props Interface

```typescript
// Card component props
interface CardProps {
  id: string;
  title: string;
  subtitle?: string;
  imageUrl?: string;
  onClick?: (data: CardProps) => void;
}

// Inspector component props
interface InspectorProps {
  entity: {
    id: string;
    title: string;
    subtitle: string;
    description: string;
    sections: Array<{
      title: string;
      attributes: Array<{
        label: string;
        value: string;
      }>;
    }>;
  };
  open: boolean;
  onClose?: () => void;
}

// Carousel component props
interface CarouselProps<T> {
  items: T[];
  renderItem: (item: T) => ComponentType;
  showNavigation?: boolean;
}
```

### API Response Types

```typescript
// Structured response from orchestrator
interface StructuredResponse {
  message: string;
  components: UIComponent[];
}

interface UIComponent {
  type: ComponentType;
  data: any;
}

enum ComponentType {
  PROPERTY_CAROUSEL = 'property-carousel',
  PROPERTY_INSPECTOR = 'property-inspector',
  INLINE_CARD = 'inline-card',
  ENTITY_CARD = 'entity-card'
}
```

---

## ♿ Accessibility Patterns

### Keyboard Navigation

```svelte
<div
  role="button"
  tabindex="0"
  on:click={handleClick}
  on:keypress={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  <!-- Content -->
</div>
```

### ARIA Labels

```svelte
<!-- Image with alt text -->
<img src={url} alt={description} />

<!-- Decorative icon (aria-hidden) -->
<svg aria-hidden="true"><!-- Icon --></svg>

<!-- Button with label -->
<button aria-label="Close modal">
  <svg><!-- X icon --></svg>
</button>

<!-- Modal -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title">Title</h2>
  <p id="modal-description">Description</p>
</div>
```

### Focus Management

```svelte
<script>
  import { onMount } from 'svelte';

  let modalOpen = false;
  let firstFocusable: HTMLElement;
  let lastFocusable: HTMLElement;

  function trapFocus(e: KeyboardEvent) {
    if (e.key !== 'Tab') return;

    const focusables = modalContainer.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    firstFocusable = focusables[0] as HTMLElement;
    lastFocusable = focusables[focusables.length - 1] as HTMLElement;

    if (e.shiftKey && document.activeElement === firstFocusable) {
      lastFocusable.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === lastFocusable) {
      firstFocusable.focus();
      e.preventDefault();
    }
  }

  $: if (modalOpen) {
    setTimeout(() => firstFocusable?.focus(), 100);
  }
</script>

<div on:keydown={trapFocus}>
  <!-- Modal content -->
</div>
```

---

## 📝 Implementation Checklist

For each new component:

- [ ] Uses design tokens (no hardcoded values)
- [ ] Follows spacing system (4px grid)
- [ ] Has TypeScript interfaces
- [ ] WCAG AA contrast ratios
- [ ] Focus-visible styles
- [ ] Keyboard accessible
- [ ] ARIA labels
- [ ] Dark mode support
- [ ] Mobile responsive
- [ ] Loading states
- [ ] Error states
- [ ] Empty states

---

**Related Documents:**
- Components Reference: `docs/design/figma/COMPONENTS_REFERENCE.md`
- Color Palette: `docs/design/figma/COLOR_PALETTE.md`
- Design Tokens: `frontend/open-webui/src/lib/styles/design-tokens.css`
