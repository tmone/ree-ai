<script lang="ts">
	/**
	 * Structured Response Renderer - OpenAI Apps SDK Pattern
	 *
	 * Renders UI components from orchestration service structured responses
	 * Supports: property-carousel, property-inspector
	 *
	 * Props:
	 * - components: Array of UIComponent objects from backend
	 */

	import CompactPropertyCard from '$lib/components/property/CompactPropertyCard.svelte';
	import PropertyDetailModal from '$lib/components/property/PropertyDetailModal.svelte';
	import { createEventDispatcher } from 'svelte';

	export let components: any[] = [];

	const dispatch = createEventDispatcher();

	// Modal state
	let modalOpen = false;
	let selectedProperty: any = null;

	// Handle property card click - open modal directly with available data
	async function handlePropertyClick(property: any) {
		console.log('[StructuredResponseRenderer] Property clicked:', property);

		// Open modal directly with property data from card
		// Property from carousel already has: id, title, address, price, bedrooms, area, imageUrl, etc.
		selectedProperty = property;
		modalOpen = true;

		// Also dispatch event for parent to handle if needed (e.g., analytics, fetch more data)
		dispatch('propertySelected', {
			propertyId: property.id,
			property: property
		});
	}

	// Handle modal close
	function handleModalClose() {
		modalOpen = false;
		selectedProperty = null;
	}

	// Render PropertyCarouselComponent
	function renderPropertyCarousel(component: any) {
		const { properties = [], total = 0 } = component.data || {};
		return { properties, total };
	}

	// Render PropertyInspectorComponent
	function renderPropertyInspector(component: any) {
		const { property_data } = component.data || {};
		selectedProperty = property_data;
		modalOpen = true;
	}

	// Process components on mount/update
	$: {
		if (components && components.length > 0) {
			components.forEach((component) => {
				if (component.type === 'property-inspector') {
					renderPropertyInspector(component);
				}
			});
		}
	}
</script>

<!-- Render Components -->
<div class="structured-response-container">
	{#each components as component}
		{#if component.type === 'property-carousel'}
			{@const carouselData = renderPropertyCarousel(component)}

			<!-- Property Carousel (🎠 Inline Carousel) -->
			<div class="property-carousel" role="region" aria-label="Property search results">
				<!-- Header -->
				{#if carouselData.total > 0}
					<div class="carousel-header">
						<p class="result-count">
							Tìm thấy <strong>{carouselData.total}</strong> bất động sản
						</p>
					</div>
				{/if}

				<!-- Property Cards -->
				<div class="property-list">
					{#each carouselData.properties as property}
						<CompactPropertyCard {property} onClick={() => handlePropertyClick(property)} />
					{/each}
				</div>

				<!-- Empty State -->
				{#if carouselData.properties.length === 0}
					<div class="empty-state">
						<p>Không tìm thấy bất động sản phù hợp</p>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Property Inspector will auto-open modal via $: reactive block above -->
	{/each}
</div>

<!-- Property Detail Modal (CTO Requirement: User can close and return to list) -->
{#if selectedProperty}
	<PropertyDetailModal property={selectedProperty} bind:open={modalOpen} on:close={handleModalClose} />
{/if}

<style>
	.structured-response-container {
		display: flex;
		flex-direction: column;
		gap: var(--space-4, 16px);
		margin: var(--space-4, 16px) 0;
	}

	/* Property Carousel */
	.property-carousel {
		display: flex;
		flex-direction: column;
		gap: var(--space-3, 12px);
	}

	.carousel-header {
		padding: var(--space-2, 8px) 0;
	}

	.result-count {
		color: var(--text-secondary, #6b7280);
		font-size: var(--text-sm, 14px);
		margin: 0;
	}

	.result-count strong {
		color: var(--text-primary, #0d0d0d);
		font-weight: var(--font-semibold, 600);
	}

	/* Property List */
	.property-list {
		display: flex;
		flex-direction: column;
		gap: var(--space-3, 12px);
	}

	/* Empty State */
	.empty-state {
		padding: var(--space-8, 32px);
		text-align: center;
		color: var(--text-secondary, #6b7280);
		font-size: var(--text-sm, 14px);
	}

	/* Dark Mode */
	@media (prefers-color-scheme: dark) {
		.result-count {
			color: var(--text-secondary, #cdcdcd);
		}

		.result-count strong {
			color: var(--text-primary, #ffffff);
		}

		.empty-state {
			color: var(--text-secondary, #cdcdcd);
		}
	}

	/* Mobile Responsive */
	@media (max-width: 768px) {
		.structured-response-container {
			margin: var(--space-2, 8px) 0;
		}

		.property-list {
			gap: var(--space-2, 8px);
		}
	}
</style>
