# REE AI Frontend Usage Examples

Complete examples for using REE AI custom components and API clients.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Property Search Page](#property-search-page)
3. [Chat Integration](#chat-integration)
4. [API Client Examples](#api-client-examples)
5. [Advanced Patterns](#advanced-patterns)

---

## Basic Usage

### Using Property Components

```svelte
<script lang="ts">
  import { PropertyCard, PropertySearch, PropertyDetails } from '$lib/components/property';
  import type { Property } from '$lib/apis/ree-ai';

  let token = localStorage.getItem('token') || '';
  let selectedProperty: Property | null = null;
  let showDetails = false;

  function handlePropertySelect(property: Property) {
    selectedProperty = property;
    showDetails = true;
  }
</script>

<!-- Property Search Component -->
<PropertySearch {token} onPropertySelect={handlePropertySelect} />

<!-- Property Details Modal -->
{#if showDetails && selectedProperty}
  <PropertyDetails
    property={selectedProperty}
    onClose={() => {
      showDetails = false;
      selectedProperty = null;
    }}
  />
{/if}
```

### Displaying a Single Property Card

```svelte
<script lang="ts">
  import { PropertyCard } from '$lib/components/property';

  const property = {
    id: 'prop-123',
    title: 'Căn hộ cao cấp 2 phòng ngủ',
    description: 'Căn hộ đẹp tại trung tâm Quận 1',
    property_type: 'apartment',
    location: 'Quận 1, TP.HCM',
    price: 3500000000,
    area: 75,
    bedrooms: 2,
    bathrooms: 2,
    images: ['https://example.com/image1.jpg'],
    created_at: '2025-10-31T00:00:00Z'
  };

  function handleClick(property) {
    console.log('Property clicked:', property);
  }
</script>

<PropertyCard {property} onClick={handleClick} />
```

---

## Property Search Page

Complete example of a property search page with filters.

### Full Page Implementation

```svelte
<!-- src/routes/(app)/properties/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { PropertySearch, PropertyDetails } from '$lib/components/property';
  import { toast } from 'svelte-sonner';
  import type { Property } from '$lib/apis/ree-ai';

  let token = '';
  let selectedProperty: Property | null = null;
  let showDetails = false;

  onMount(() => {
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      toast.error('Vui lòng đăng nhập');
      goto('/auth');
      return;
    }
    token = storedToken;
  });

  function handlePropertySelect(property: Property) {
    selectedProperty = property;
    showDetails = true;
  }

  function closeDetails() {
    showDetails = false;
    selectedProperty = null;
  }
</script>

<svelte:head>
  <title>Tìm kiếm Bất động sản - REE AI</title>
</svelte:head>

<div class="properties-page">
  <div class="page-header">
    <h1>Tìm kiếm Bất động sản</h1>
    <p>Sử dụng AI để tìm kiếm bất động sản phù hợp</p>
  </div>

  <div class="page-content">
    {#if token}
      <PropertySearch {token} onPropertySelect={handlePropertySelect} />
    {:else}
      <p>Đang tải...</p>
    {/if}
  </div>

  {#if showDetails && selectedProperty}
    <PropertyDetails property={selectedProperty} onClose={closeDetails} />
  {/if}
</div>

<style>
  .properties-page {
    min-height: 100vh;
    background: #f9fafb;
  }

  .page-header {
    background: white;
    padding: 32px;
    border-bottom: 1px solid #e5e7eb;
  }

  .page-header h1 {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 8px 0;
  }

  .page-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
  }
</style>
```

---

## Chat Integration

### Displaying Properties in Chat Messages

```svelte
<!-- In your chat message component -->
<script lang="ts">
  import { PropertyMessage } from '$lib/components/chat';
  import type { Property } from '$lib/apis/ree-ai';

  export let message: any;
  export let onPropertyClick: (property: Property) => void;

  // Parse properties from message metadata
  $: properties = message.metadata?.properties || [];
</script>

<div class="chat-message">
  <!-- Regular message content -->
  <div class="message-text">
    {message.content}
  </div>

  <!-- Property cards if available -->
  {#if properties.length > 0}
    <PropertyMessage {properties} {onPropertyClick} />
  {/if}
</div>
```

### Triggering Property Search from Chat

```svelte
<script lang="ts">
  import { sendOrchestratorQuery } from '$lib/apis/ree-ai';
  import { PropertyMessage } from '$lib/components/chat';

  let token = localStorage.getItem('token') || '';
  let query = '';
  let properties = [];
  let loading = false;

  async function handleSearch() {
    if (!query.trim()) return;

    loading = true;
    try {
      // Send to orchestrator for intent detection
      const response = await sendOrchestratorQuery(token, {
        query,
        user_id: 'user123'
      });

      // If orchestrator detected property search intent
      if (response.intent === 'property_search' && response.metadata?.properties) {
        properties = response.metadata.properties;
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      loading = false;
    }
  }

  function handlePropertyClick(property) {
    console.log('Property clicked:', property);
  }
</script>

<div class="chat-interface">
  <input bind:value={query} on:keypress={(e) => e.key === 'Enter' && handleSearch()} />

  {#if loading}
    <div class="spinner"></div>
  {/if}

  {#if properties.length > 0}
    <PropertyMessage {properties} onPropertyClick={handlePropertyClick} />
  {/if}
</div>
```

---

## API Client Examples

### 1. Orchestrator API

```typescript
import { sendOrchestratorQuery } from '$lib/apis/ree-ai';

// Basic query
const response = await sendOrchestratorQuery(token, {
  query: 'Tìm căn hộ 2 phòng ngủ ở Quận 1',
  user_id: 'user123'
});

console.log(response.intent); // e.g., 'property_search'
console.log(response.response); // AI response
console.log(response.service_used); // e.g., 'db-gateway'
console.log(response.confidence); // 0.95

// With context
const contextualResponse = await sendOrchestratorQuery(token, {
  query: 'Cho tôi xem thêm kết quả',
  user_id: 'user123',
  context: {
    previous_query: 'căn hộ quận 1',
    filters: { property_type: 'apartment' }
  }
});
```

### 2. Storage/Search API

```typescript
import { searchProperties, getPropertyById } from '$lib/apis/ree-ai';

// Basic search
const results = await searchProperties(token, {
  query: 'căn hộ cao cấp',
  limit: 20
});

console.log(results.total); // Total matches
console.log(results.results); // Array of properties

// Advanced search with filters
const filteredResults = await searchProperties(token, {
  query: 'nhà phố',
  filters: {
    property_type: ['house', 'townhouse'],
    location: ['Quận 1', 'Quận 3'],
    min_price: 5000000000, // 5 tỷ
    max_price: 10000000000, // 10 tỷ
    min_area: 100,
    max_area: 200,
  },
  limit: 50,
  offset: 0
});

// Get specific property
const property = await getPropertyById(token, 'prop-123');
console.log(property.title);
console.log(property.price);
```

### 3. Classification API

```typescript
import { classifyProperty, extractAttributes } from '$lib/apis/ree-ai';

// Classify property text
const classification = await classifyProperty(token, {
  text: 'Bán nhà 3 tầng 100m2 tại Quận 1 giá 5 tỷ, 3 phòng ngủ 2 phòng tắm',
  options: {
    extract_attributes: true,
    confidence_threshold: 0.7
  }
});

console.log(classification.property_type); // 'house'
console.log(classification.confidence); // 0.92
console.log(classification.attributes.price); // 5000000000
console.log(classification.attributes.area); // 100
console.log(classification.attributes.bedrooms); // 3

// Extract only attributes
const attributes = await extractAttributes(token,
  'Căn hộ 2PN 75m2 giá 3.5 tỷ'
);

console.log(attributes);
// {
//   bedrooms: 2,
//   area: 75,
//   price: 3500000000
// }
```

### 4. RAG API

```typescript
import { queryRAG, indexProperty } from '$lib/apis/ree-ai';

// Query with RAG
const answer = await queryRAG(token, {
  query: 'Tư vấn về thị trường BDS tại Quận 1',
  user_id: 'user123',
  top_k: 5
});

console.log(answer.answer); // Generated answer
console.log(answer.sources); // Source properties used
console.log(answer.context_used); // Context snippets

// Index new property
const indexed = await indexProperty(token, {
  id: 'prop-456',
  title: 'Căn hộ cao cấp...',
  description: 'Mô tả chi tiết...',
  property_type: 'apartment',
  location: 'Quận 1, TP.HCM',
  price: 3500000000,
  area: 75
});

console.log(indexed.success); // true
console.log(indexed.property_id); // 'prop-456'
```

---

## Advanced Patterns

### 1. Infinite Scroll Search Results

```svelte
<script lang="ts">
  import { searchProperties } from '$lib/apis/ree-ai';
  import { PropertyCard } from '$lib/components/property';
  import { onMount } from 'svelte';

  let token = '';
  let query = '';
  let results = [];
  let offset = 0;
  let limit = 20;
  let loading = false;
  let hasMore = true;

  async function loadMore() {
    if (loading || !hasMore) return;

    loading = true;
    try {
      const response = await searchProperties(token, {
        query,
        limit,
        offset
      });

      results = [...results, ...response.results];
      offset += limit;
      hasMore = response.results.length === limit;
    } catch (error) {
      console.error('Load more error:', error);
    } finally {
      loading = false;
    }
  }

  function handleScroll(e) {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollHeight - scrollTop <= clientHeight * 1.5) {
      loadMore();
    }
  }

  onMount(() => {
    token = localStorage.getItem('token') || '';
  });
</script>

<div class="scroll-container" on:scroll={handleScroll}>
  <div class="results-grid">
    {#each results as property}
      <PropertyCard {property} />
    {/each}
  </div>

  {#if loading}
    <div class="loading">Đang tải...</div>
  {/if}

  {#if !hasMore}
    <div class="end">Hết kết quả</div>
  {/if}
</div>
```

### 2. Real-time Search with Debounce

```svelte
<script lang="ts">
  import { searchProperties } from '$lib/apis/ree-ai';
  import { writable } from 'svelte/store';
  import { debounce } from 'lodash-es';

  let token = '';
  let query = '';
  let results = writable([]);
  let loading = writable(false);

  const debouncedSearch = debounce(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      results.set([]);
      return;
    }

    loading.set(true);
    try {
      const response = await searchProperties(token, {
        query: searchQuery,
        limit: 10
      });
      results.set(response.results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      loading.set(false);
    }
  }, 500);

  $: debouncedSearch(query);
</script>

<input
  type="text"
  bind:value={query}
  placeholder="Tìm kiếm..."
/>

{#if $loading}
  <div>Đang tìm...</div>
{/if}

{#each $results as property}
  <PropertyCard {property} />
{/each}
```

### 3. Property Comparison

```svelte
<script lang="ts">
  import { PropertyCard } from '$lib/components/property';
  import type { Property } from '$lib/apis/ree-ai';

  let selectedProperties: Property[] = [];
  const maxCompare = 3;

  function toggleCompare(property: Property) {
    const index = selectedProperties.findIndex(p => p.id === property.id);
    if (index >= 0) {
      selectedProperties = selectedProperties.filter(p => p.id !== property.id);
    } else if (selectedProperties.length < maxCompare) {
      selectedProperties = [...selectedProperties, property];
    } else {
      alert(`Chỉ có thể so sánh tối đa ${maxCompare} bất động sản`);
    }
  }

  function getComparisonData() {
    return {
      prices: selectedProperties.map(p => p.price),
      areas: selectedProperties.map(p => p.area),
      pricePerSqm: selectedProperties.map(p => p.price / p.area)
    };
  }
</script>

<div class="comparison-tool">
  <h2>So sánh bất động sản ({selectedProperties.length}/{maxCompare})</h2>

  {#if selectedProperties.length > 0}
    <div class="comparison-grid">
      {#each selectedProperties as property}
        <div class="comparison-item">
          <PropertyCard {property} />
          <button on:click={() => toggleCompare(property)}>
            Xóa khỏi so sánh
          </button>
        </div>
      {/each}
    </div>

    {#if selectedProperties.length >= 2}
      <div class="comparison-stats">
        <h3>Thống kê so sánh</h3>
        {@const data = getComparisonData()}
        <p>Giá trung bình: {(data.prices.reduce((a, b) => a + b, 0) / data.prices.length).toFixed(0)} VNĐ</p>
        <p>Diện tích trung bình: {(data.areas.reduce((a, b) => a + b, 0) / data.areas.length).toFixed(1)} m²</p>
        <p>Giá/m² trung bình: {(data.pricePerSqm.reduce((a, b) => a + b, 0) / data.pricePerSqm.length).toFixed(0)} VNĐ/m²</p>
      </div>
    {/if}
  {:else}
    <p>Chọn bất động sản để bắt đầu so sánh</p>
  {/if}
</div>
```

### 4. Save Favorite Properties

```svelte
<script lang="ts">
  import { PropertyCard } from '$lib/components/property';
  import type { Property } from '$lib/apis/ree-ai';
  import { writable } from 'svelte/store';

  // Store favorites in localStorage
  const favorites = writable<Property[]>([]);

  function loadFavorites() {
    const stored = localStorage.getItem('favorite_properties');
    if (stored) {
      favorites.set(JSON.parse(stored));
    }
  }

  function saveFavorites(favs: Property[]) {
    localStorage.setItem('favorite_properties', JSON.stringify(favs));
    favorites.set(favs);
  }

  function toggleFavorite(property: Property) {
    favorites.update(favs => {
      const index = favs.findIndex(p => p.id === property.id);
      if (index >= 0) {
        return favs.filter(p => p.id !== property.id);
      } else {
        return [...favs, property];
      }
    });

    favorites.subscribe(favs => saveFavorites(favs));
  }

  function isFavorite(propertyId: string): boolean {
    return $favorites.some(p => p.id === propertyId);
  }

  loadFavorites();
</script>

<div class="favorites-list">
  <h2>Bất động sản yêu thích ({$favorites.length})</h2>

  {#if $favorites.length === 0}
    <p>Chưa có bất động sản yêu thích</p>
  {:else}
    <div class="favorites-grid">
      {#each $favorites as property}
        <div class="favorite-item">
          <PropertyCard {property} />
          <button on:click={() => toggleFavorite(property)}>
            ❤️ Bỏ yêu thích
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>
```

---

## Error Handling

### Comprehensive Error Handling

```typescript
import { searchProperties } from '$lib/apis/ree-ai';
import { toast } from 'svelte-sonner';

async function safeSearch(token: string, query: string) {
  try {
    const response = await searchProperties(token, {
      query,
      limit: 20
    });

    return response;
  } catch (error: any) {
    // Handle specific error types
    if (error.status === 401) {
      toast.error('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
      goto('/auth');
    } else if (error.status === 403) {
      toast.error('Bạn không có quyền truy cập');
    } else if (error.status === 404) {
      toast.error('Không tìm thấy kết quả');
    } else if (error.status === 500) {
      toast.error('Lỗi hệ thống. Vui lòng thử lại sau.');
    } else if (error.status === 504) {
      toast.error('Hết thời gian chờ. Vui lòng thử lại.');
    } else {
      toast.error(`Lỗi: ${error.message || 'Đã xảy ra lỗi'}`);
    }

    console.error('Search error:', error);
    return null;
  }
}
```

---

## Testing

### Component Testing Example

```typescript
import { render, fireEvent } from '@testing-library/svelte';
import PropertyCard from '$lib/components/property/PropertyCard.svelte';

describe('PropertyCard', () => {
  const mockProperty = {
    id: 'test-1',
    title: 'Test Property',
    location: 'Test Location',
    price: 1000000000,
    area: 50,
    property_type: 'apartment',
    created_at: '2025-10-31T00:00:00Z'
  };

  test('renders property information', () => {
    const { getByText } = render(PropertyCard, { props: { property: mockProperty } });

    expect(getByText('Test Property')).toBeInTheDocument();
    expect(getByText('Test Location')).toBeInTheDocument();
  });

  test('calls onClick when clicked', async () => {
    let clicked = false;
    const onClick = () => { clicked = true; };

    const { container } = render(PropertyCard, {
      props: { property: mockProperty, onClick }
    });

    const button = container.querySelector('button');
    await fireEvent.click(button);

    expect(clicked).toBe(true);
  });
});
```

---

## Resources

- **Complete Build Guide**: [FRONTEND_BUILD_GUIDE.md](./FRONTEND_BUILD_GUIDE.md)
- **Frontend README**: [frontend/open-webui/README.REE-AI.md](../frontend/open-webui/README.REE-AI.md)
- **API Type Definitions**: `frontend/open-webui/src/lib/apis/ree-ai/`
- **Component Source**: `frontend/open-webui/src/lib/components/property/`

---

**Last Updated:** 2025-10-31
**Version:** 1.0.0
