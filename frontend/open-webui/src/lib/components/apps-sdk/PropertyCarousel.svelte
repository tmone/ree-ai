<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import PropertyCard from './PropertyCard.svelte';
	import AppAttribution from './AppAttribution.svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let properties: Array<{
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
	}> = [];
	export let showAttribution: boolean = true;
	export let appName: string = 'REE AI';
	export let appIcon: string = '';

	let scrollContainer: HTMLDivElement;
	let currentIndex = 0;

	function scrollTo(index: number) {
		if (scrollContainer) {
			const itemWidth = 276; // 260px card + 16px gap
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

<div class="property-carousel-container">
	{#if showAttribution}
		<AppAttribution {appName} {appIcon} />
	{/if}

	<div class="carousel-wrapper">
		<div class="carousel-row" bind:this={scrollContainer} on:scroll={handleScroll}>
			{#each properties as property}
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
</div>

<style>
	.property-carousel-container {
		display: flex;
		flex-direction: column;
		width: 100%;
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
		border: 1px solid var(--border-default);
		border-radius: 999px;
		cursor: pointer;
		color: var(--text-primary);
		pointer-events: auto;
		box-shadow: var(--shadow-md);
		transition: all var(--transition-base);
	}

	.nav-button:hover:not(:disabled) {
		background: var(--bg-tertiary);
	}

	.nav-button:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.dark .nav-button {
		background: var(--bg-secondary);
	}
</style>
