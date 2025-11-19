<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let title: string = '';
	export let subtitle: string = '';
	export let imageUrl: string = '';
	export let variant: 'simple' | 'media' | 'detailed' = 'simple';
	export let showAction: boolean = true;

	function handleAction() {
		dispatch('action', { title, subtitle });
	}
</script>

<div class="entity-card" class:simple={variant === 'simple'} class:media={variant === 'media'} class:detailed={variant === 'detailed'}>
	<div class="card-inner">
		{#if imageUrl}
			<div class="image-container">
				<img src={imageUrl} alt={title} class="entity-image" />
				<div class="image-overlay"></div>
			</div>
		{/if}

		<div class="footer">
			<div class="content-left">
				<p class="title">{title}</p>
				{#if subtitle}
					<p class="subtitle">{subtitle}</p>
				{/if}
			</div>
			{#if showAction}
				<div class="content-right">
					<button class="action-button" on:click={handleAction}>
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.entity-card {
		background: white;
		border: 0.5px solid var(--border-default, rgba(13, 13, 13, 0.15));
		border-radius: 24px;
		overflow: hidden;
	}

	.entity-card.simple {
		width: 345px;
		height: 345px;
	}

	.entity-card.media {
		width: 345px;
		height: 345px;
	}

	.entity-card.detailed {
		width: 356px;
		min-height: 397px;
	}

	.dark .entity-card {
		background: var(--bg-primary);
		border-color: var(--border-default-dark);
	}

	.card-inner {
		display: flex;
		flex-direction: column;
		gap: 10px;
		align-items: center;
		justify-content: flex-end;
		overflow: hidden;
		border-radius: inherit;
		height: 100%;
		position: relative;
	}

	.image-container {
		position: absolute;
		inset: 0;
		overflow: hidden;
	}

	.entity-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.image-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 50%);
	}

	.footer {
		display: flex;
		gap: 12px;
		align-items: center;
		padding: 20px;
		width: 100%;
		box-sizing: border-box;
		position: relative;
		z-index: 1;
	}

	.content-left {
		display: flex;
		flex: 1 0 0;
		flex-direction: column;
		gap: 5px;
		align-items: flex-start;
		justify-content: center;
		min-width: 0;
	}

	.title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 17px;
		line-height: 23px;
		letter-spacing: -0.43px;
		color: white;
	}

	.subtitle {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 14px;
		line-height: 20px;
		letter-spacing: -0.3px;
		color: rgba(255, 255, 255, 0.7);
	}

	.content-right {
		padding: 0 8px;
	}

	.action-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		background: rgba(239, 239, 240, 1);
		border: none;
		border-radius: 999px;
		cursor: pointer;
		color: var(--text-primary);
		transition: background-color var(--transition-base);
	}

	.action-button:hover {
		background: rgba(255, 255, 255, 1);
	}

	/* Detailed variant specific styles */
	.entity-card.detailed .footer {
		background: white;
		padding: 16px;
	}

	.dark .entity-card.detailed .footer {
		background: var(--bg-primary);
	}

	.entity-card.detailed .title {
		color: var(--text-primary);
	}

	.entity-card.detailed .subtitle {
		color: var(--text-secondary);
	}

	.entity-card.detailed .image-overlay {
		display: none;
	}

	.entity-card.detailed .image-container {
		position: relative;
		width: 100%;
		aspect-ratio: 1;
	}
</style>
