<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let items: Array<{
		imageUrl: string;
		title: string;
		description?: string;
		primaryButtonText?: string;
		secondaryButtonText?: string;
	}> = [];
	export let imageSize: 'square' | 'portrait' | 'landscape' = 'square';

	let scrollContainer: HTMLDivElement;
	let currentIndex = 0;

	function scrollTo(index: number) {
		if (scrollContainer) {
			const itemWidth = scrollContainer.children[0]?.clientWidth || 260;
			const gap = 16;
			scrollContainer.scrollTo({
				left: index * (itemWidth + gap),
				behavior: 'smooth'
			});
			currentIndex = index;
		}
	}

	function handlePrimaryAction(index: number) {
		dispatch('primaryAction', { index, item: items[index] });
	}

	function handleSecondaryAction(index: number) {
		dispatch('secondaryAction', { index, item: items[index] });
	}

	function handleScroll() {
		if (scrollContainer) {
			const itemWidth = scrollContainer.children[0]?.clientWidth || 260;
			const gap = 16;
			currentIndex = Math.round(scrollContainer.scrollLeft / (itemWidth + gap));
		}
	}
</script>

<div class="carousel-container">
	<div class="carousel-row" bind:this={scrollContainer} on:scroll={handleScroll}>
		{#each items as item, index}
			<div class="carousel-item" class:square={imageSize === 'square'} class:portrait={imageSize === 'portrait'} class:landscape={imageSize === 'landscape'}>
				<div class="image-wrapper">
					<img src={item.imageUrl} alt={item.title} class="item-image" />
				</div>
				<div class="content">
					<div class="header-section">
						<p class="title">{item.title}</p>
					</div>
					{#if item.description}
						<p class="description">{item.description}</p>
					{/if}
					<div class="button-container">
						{#if item.primaryButtonText}
							<button class="action-button primary" on:click={() => handlePrimaryAction(index)}>
								{item.primaryButtonText}
							</button>
						{/if}
						{#if item.secondaryButtonText}
							<button class="action-button secondary" on:click={() => handleSecondaryAction(index)}>
								{item.secondaryButtonText}
							</button>
						{/if}
					</div>
				</div>
			</div>
		{/each}
	</div>

	{#if items.length > 1}
		<div class="carousel-navigation">
			<button class="nav-button prev" on:click={() => scrollTo(Math.max(0, currentIndex - 1))} disabled={currentIndex === 0}>
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
			<button class="nav-button next" on:click={() => scrollTo(Math.min(items.length - 1, currentIndex + 1))} disabled={currentIndex === items.length - 1}>
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		</div>
	{/if}
</div>

<style>
	.carousel-container {
		position: relative;
		width: 100%;
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

	.carousel-item {
		display: flex;
		flex-direction: column;
		gap: 12px;
		align-items: center;
		flex-shrink: 0;
		scroll-snap-align: start;
	}

	.carousel-item.square {
		width: 260px;
	}

	.carousel-item.portrait {
		width: 200px;
	}

	.carousel-item.landscape {
		width: 320px;
	}

	.image-wrapper {
		border: 1px solid var(--border-light, rgba(13, 13, 13, 0.05));
		border-radius: 16px;
		overflow: hidden;
		width: 100%;
	}

	.carousel-item.square .image-wrapper {
		aspect-ratio: 1;
	}

	.carousel-item.portrait .image-wrapper {
		aspect-ratio: 3/4;
	}

	.carousel-item.landscape .image-wrapper {
		aspect-ratio: 16/9;
	}

	.item-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.content {
		display: flex;
		flex-direction: column;
		gap: 16px;
		align-items: flex-start;
		width: 100%;
	}

	.header-section {
		display: flex;
		flex-direction: column;
		gap: 8px;
		width: 100%;
	}

	.title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 17px;
		line-height: 23px;
		letter-spacing: -0.43px;
		color: var(--text-primary);
	}

	.description {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 14px;
		line-height: 20px;
		letter-spacing: -0.3px;
		color: var(--text-secondary);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.button-container {
		display: flex;
		gap: 8px;
		align-items: flex-start;
		width: 100%;
	}

	.action-button {
		height: 44px;
		padding: 15px 24px;
		border-radius: 999px;
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 14px;
		line-height: 20px;
		letter-spacing: -0.3px;
		cursor: pointer;
		border: none;
		transition: background-color var(--transition-base);
	}

	.action-button.primary {
		background: var(--brand-primary);
		color: var(--text-inverse);
	}

	.action-button.primary:hover {
		background: var(--brand-primary-hover);
	}

	.action-button.secondary {
		background: var(--bg-tertiary);
		color: var(--text-primary);
	}

	.action-button.secondary:hover {
		background: var(--bg-secondary);
	}

	.carousel-navigation {
		position: absolute;
		top: 50%;
		left: 0;
		right: 0;
		display: flex;
		justify-content: space-between;
		pointer-events: none;
		transform: translateY(-100%);
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
