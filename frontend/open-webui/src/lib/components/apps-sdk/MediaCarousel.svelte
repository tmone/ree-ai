<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let images: string[] = [];
	export let currentIndex: number = 0;
	export let aspectRatio: string = '1';

	function goToSlide(index: number) {
		currentIndex = index;
		dispatch('change', { index });
	}

	function nextSlide() {
		if (currentIndex < images.length - 1) {
			goToSlide(currentIndex + 1);
		}
	}

	function prevSlide() {
		if (currentIndex > 0) {
			goToSlide(currentIndex - 1);
		}
	}
</script>

<div class="media-carousel">
	<div class="media-container" style="aspect-ratio: {aspectRatio}">
		{#each images as image, index}
			<div class="media-slide" class:active={index === currentIndex}>
				<img src={image} alt="Slide {index + 1}" />
			</div>
		{/each}
	</div>

	{#if images.length > 1}
		<div class="pagination">
			{#each images as _, index}
				<button
					class="pagination-dot"
					class:active={index === currentIndex}
					on:click={() => goToSlide(index)}
				/>
			{/each}
		</div>

		<button class="nav-button prev" on:click={prevSlide} disabled={currentIndex === 0}>
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</button>

		<button class="nav-button next" on:click={nextSlide} disabled={currentIndex === images.length - 1}>
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</button>
	{/if}
</div>

<style>
	.media-carousel {
		position: relative;
		width: 100%;
		border-radius: 20px;
		overflow: hidden;
		border: 1px solid var(--border-light, rgba(13, 13, 13, 0.05));
	}

	.media-container {
		position: relative;
		width: 100%;
		overflow: hidden;
	}

	.media-slide {
		position: absolute;
		inset: 0;
		opacity: 0;
		transition: opacity 0.3s ease;
	}

	.media-slide.active {
		opacity: 1;
	}

	.media-slide img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.pagination {
		position: absolute;
		bottom: 12px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		gap: 5px;
	}

	.pagination-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.5);
		border: none;
		padding: 0;
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.pagination-dot.active {
		background: white;
	}

	.nav-button {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		background: white;
		border: 1px solid var(--border-default);
		border-radius: 50%;
		cursor: pointer;
		color: var(--text-primary);
		box-shadow: var(--shadow-md);
		transition: all var(--transition-base);
		opacity: 0;
	}

	.media-carousel:hover .nav-button {
		opacity: 1;
	}

	.nav-button:disabled {
		opacity: 0 !important;
		cursor: not-allowed;
	}

	.nav-button:hover:not(:disabled) {
		background: var(--bg-tertiary);
	}

	.nav-button.prev {
		left: 12px;
	}

	.nav-button.next {
		right: 12px;
	}

	.dark .nav-button {
		background: var(--bg-secondary);
	}
</style>
