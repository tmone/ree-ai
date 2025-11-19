<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import MediaCarousel from './MediaCarousel.svelte';
	import Button from './Button.svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let title: string = '';
	export let subtitle: string = '';
	export let rating: string = '';
	export let images: string[] = [];
	export let metadata: Array<{ label: string; value: string }> = [];
	export let primaryButtonText: string = '';
	export let secondaryButtonText: string = '';
	export let description: string = '';
	export let showCloseButton: boolean = true;

	function handleClose() {
		dispatch('close');
	}

	function handlePrimaryAction() {
		dispatch('primaryAction');
	}

	function handleSecondaryAction() {
		dispatch('secondaryAction');
	}
</script>

<div class="inspector">
	{#if showCloseButton}
		<div class="inspector-header">
			<button class="close-button" on:click={handleClose}>
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		</div>
	{/if}

	{#if images.length > 0}
		<div class="media-section">
			<MediaCarousel {images} aspectRatio="420/360" />
		</div>
	{/if}

	<div class="details-section">
		<div class="single-item-header">
			<div class="header-content">
				<div class="title-section">
					<h2 class="title">{title}</h2>
					{#if subtitle}
						<p class="subtitle">{subtitle}</p>
					{/if}
				</div>
				{#if rating}
					<div class="rating-badge">
						<span>{rating}</span>
					</div>
				{/if}
			</div>
		</div>

		{#if metadata.length > 0}
			<div class="metadata-section">
				{#each metadata as item, index}
					<div class="metadata-item">
						<span class="metadata-value">{item.value}</span>
						<span class="metadata-label">{item.label}</span>
					</div>
					{#if index < metadata.length - 1}
						<div class="metadata-divider"></div>
					{/if}
				{/each}
			</div>
		{/if}

		{#if primaryButtonText || secondaryButtonText}
			<div class="button-container">
				{#if primaryButtonText}
					<Button text={primaryButtonText} variant="warning" on:click={handlePrimaryAction} />
				{/if}
				{#if secondaryButtonText}
					<Button text={secondaryButtonText} variant="secondary" on:click={handleSecondaryAction} />
				{/if}
			</div>
		{/if}

		{#if description}
			<div class="description-section">
				<p class="description">{description}</p>
			</div>
		{/if}

		<slot />
	</div>
</div>

<style>
	.inspector {
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 420px;
		background: var(--bg-primary);
		border-left: 1px solid var(--border-light, rgba(13, 13, 13, 0.05));
		height: 100%;
		overflow-y: auto;
	}

	.inspector-header {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding: 12px 16px;
		position: absolute;
		top: 0;
		right: 0;
		z-index: 10;
	}

	.close-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		background: rgba(0, 0, 0, 0.3);
		border: none;
		border-radius: 50%;
		cursor: pointer;
		color: white;
		transition: all var(--transition-base);
	}

	.close-button:hover {
		background: rgba(0, 0, 0, 0.5);
	}

	.media-section {
		width: 100%;
		position: relative;
	}

	.details-section {
		display: flex;
		flex-direction: column;
		padding: 0 24px;
	}

	.single-item-header {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding: 16px 0;
	}

	.header-content {
		display: flex;
		align-items: flex-start;
		gap: 8px;
	}

	.title-section {
		display: flex;
		flex-direction: column;
		gap: 4px;
		flex: 1;
		min-width: 0;
	}

	.title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 28px;
		line-height: 34px;
		letter-spacing: 0.38px;
		color: var(--text-primary);
	}

	.subtitle {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 14px;
		line-height: 20px;
		letter-spacing: -0.3px;
		color: var(--text-primary);
	}

	.rating-badge {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		background: var(--status-warning-bg, #fff5f0);
		border-radius: 38px;
		flex-shrink: 0;
	}

	.rating-badge span {
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 14px;
		line-height: 18px;
		color: var(--status-warning, #e25507);
	}

	.metadata-section {
		display: flex;
		align-items: flex-start;
		gap: 18px;
		padding: 16px 0;
	}

	.metadata-item {
		display: flex;
		flex-direction: column;
		gap: 0;
	}

	.metadata-value {
		font-family: var(--font-sans);
		font-size: 17px;
		line-height: 23px;
		color: var(--text-primary);
	}

	.metadata-label {
		font-family: var(--font-sans);
		font-size: 14px;
		line-height: 18px;
		color: var(--text-secondary);
	}

	.metadata-divider {
		width: 1px;
		height: 19px;
		background: var(--border-default);
		align-self: center;
	}

	.button-container {
		display: flex;
		gap: 8px;
		padding: 16px 0;
	}

	.description-section {
		padding: 16px 0;
	}

	.description {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 16px;
		line-height: 26px;
		letter-spacing: -0.4px;
		color: var(--text-primary);
	}
</style>
