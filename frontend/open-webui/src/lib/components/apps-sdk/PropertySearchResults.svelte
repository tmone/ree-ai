<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import PropertyCard from './PropertyCard.svelte';
	import AppAttribution from './AppAttribution.svelte';

	const dispatch = createEventDispatcher();

	// Props - JSON string from HTML attribute
	export let data: string = '';

	interface Property {
		id: string;
		title: string;
		address: string;
		price: string;
		priceUnit?: string;
		area: string;
		areaUnit?: string;
		bedrooms?: number;
		bathrooms?: number;
		imageUrl: string;
		propertyType?: string;
		transactionType?: 'sale' | 'rent';
	}

	let properties: Property[] = [];
	let scrollContainer: HTMLDivElement;
	let currentIndex = 0;

	// Parse data from JSON string
	$: {
		try {
			if (data) {
				const parsed = JSON.parse(decodeURIComponent(data));
				properties = Array.isArray(parsed) ? parsed : [];
			}
		} catch (e) {
			console.error('Failed to parse property data:', e);
			properties = [];
		}
	}

	function scrollTo(index: number) {
		if (scrollContainer) {
			const itemWidth = 276;
			scrollContainer.scrollTo({
				left: index * itemWidth,
				behavior: 'smooth'
			});
			currentIndex = index;
		}
	}

	function handleScroll() {
		if (scrollContainer) {
			const itemWidth = 276;
			currentIndex = Math.round(scrollContainer.scrollLeft / itemWidth);
		}
	}

	function handlePropertyClick(event: CustomEvent) {
		dispatch('propertyClick', event.detail);
	}

	function handleViewDetails(event: CustomEvent) {
		dispatch('viewDetails', event.detail);
	}
</script>

{#if properties.length > 0}
	<div class="property-search-results">
		<AppAttribution appName="REE AI" />

		<div class="carousel-wrapper">
			<div class="carousel-row" bind:this={scrollContainer} on:scroll={handleScroll}>
				{#each properties as property (property.id)}
					<PropertyCard
						{...property}
						on:click={handlePropertyClick}
						on:viewDetails={handleViewDetails}
					/>
				{/each}
			</div>

			{#if properties.length > 2}
				<div class="carousel-navigation">
					<button
						class="nav-button prev"
						on:click={() => scrollTo(Math.max(0, currentIndex - 1))}
						disabled={currentIndex === 0}
					>
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
					<button
						class="nav-button next"
						on:click={() => scrollTo(Math.min(properties.length - 1, currentIndex + 1))}
						disabled={currentIndex >= properties.length - 2}
					>
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				</div>
			{/if}
		</div>

		<p class="results-count">Tìm thấy {properties.length} bất động sản</p>
	</div>
{/if}

<style>
	.property-search-results {
		display: flex;
		flex-direction: column;
		width: 100%;
		margin: 12px 0;
	}

	.carousel-wrapper {
		position: relative;
	}

	.carousel-row {
		display: flex;
		gap: 16px;
		overflow-x: auto;
		scroll-snap-type: x mandatory;
		scrollbar-width: none;
		-ms-overflow-style: none;
		padding: 4px;
	}

	.carousel-row::-webkit-scrollbar {
		display: none;
	}

	.carousel-row > :global(*) {
		scroll-snap-align: start;
	}

	.carousel-navigation {
		position: absolute;
		top: 50%;
		left: 0;
		right: 0;
		display: flex;
		justify-content: space-between;
		pointer-events: none;
		transform: translateY(-50%);
		padding: 0 8px;
	}

	.nav-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		background: white;
		border: 1px solid var(--border-default, rgba(13, 13, 13, 0.15));
		border-radius: 999px;
		cursor: pointer;
		color: var(--text-primary, #0d0d0d);
		pointer-events: auto;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		transition: all 0.2s ease;
	}

	.nav-button:hover:not(:disabled) {
		background: var(--bg-tertiary, #f3f3f3);
	}

	.nav-button:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	:global(.dark) .nav-button {
		background: var(--bg-secondary, #1a1a1a);
		border-color: var(--border-default-dark, rgba(255, 255, 255, 0.1));
		color: white;
	}

	.results-count {
		margin: 12px 0 0 0;
		font-family: var(--font-sans, system-ui);
		font-size: 13px;
		color: var(--text-secondary, #5d5d5d);
	}
</style>
