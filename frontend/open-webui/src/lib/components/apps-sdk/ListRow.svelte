<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let title: string = '';
	export let subtitle: string = '';
	export let imageUrl: string = '';
	export let showAction: boolean = true;
	export let actionIcon: 'plus' | 'chevron' | 'check' = 'plus';
	export let isChecked: boolean = false;
	export let hasBorder: boolean = true;
	export let isLoading: boolean = false;

	function handleActionClick() {
		dispatch('action', { title, subtitle });
	}
</script>

<div
	class="list-row"
	class:has-border={hasBorder}
	class:is-loading={isLoading}
>
	<div class="list-row-content">
		<div class="image-content">
			{#if imageUrl}
				<div class="image-wrapper">
					<img src={imageUrl} alt={title} class="item-image" />
				</div>
			{/if}
			<div class="title-subtitle">
				{#if isLoading}
					<div class="skeleton-title"></div>
					<div class="skeleton-subtitle"></div>
				{:else}
					<p class="title">{title}</p>
					{#if subtitle}
						<p class="subtitle">{subtitle}</p>
					{/if}
				{/if}
			</div>
		</div>
		{#if showAction && !isLoading}
			<button class="action-button" on:click={handleActionClick}>
				{#if actionIcon === 'plus'}
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				{:else if actionIcon === 'chevron'}
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				{:else if actionIcon === 'check'}
					<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				{/if}
			</button>
		{/if}
	</div>
</div>

<style>
	.list-row {
		display: flex;
		flex-direction: column;
		gap: 12px;
		align-items: flex-start;
		justify-content: center;
		padding: 12px 16px;
		width: 100%;
		box-sizing: border-box;
	}

	.list-row.has-border {
		border-bottom: 1px solid var(--border-light, rgba(13, 13, 13, 0.05));
	}

	.list-row-content {
		display: flex;
		gap: 8px;
		align-items: center;
		width: 100%;
	}

	.image-content {
		display: flex;
		flex: 1 0 0;
		gap: 12px;
		align-items: center;
		min-width: 0;
	}

	.image-wrapper {
		width: 44px;
		height: 44px;
		border-radius: 10px;
		overflow: hidden;
		flex-shrink: 0;
	}

	.item-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.title-subtitle {
		display: flex;
		flex-direction: column;
		flex: 1 0 0;
		justify-content: center;
		min-width: 0;
		font-family: var(--font-sans);
	}

	.title {
		margin: 0;
		font-size: 17px;
		line-height: 24px;
		letter-spacing: -0.4px;
		color: var(--text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.subtitle {
		margin: 0;
		font-size: 14px;
		font-weight: 400;
		line-height: 20px;
		letter-spacing: -0.18px;
		color: var(--text-secondary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.action-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 44px;
		height: 44px;
		padding: 8px;
		background: var(--bg-tertiary);
		border: none;
		border-radius: 999px;
		cursor: pointer;
		flex-shrink: 0;
		color: var(--text-primary);
		transition: background-color var(--transition-base);
	}

	.action-button:hover {
		background: var(--bg-secondary);
	}

	/* Loading skeleton styles */
	.is-loading .skeleton-title,
	.is-loading .skeleton-subtitle {
		background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-tertiary) 50%, var(--bg-secondary) 75%);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
		border-radius: 4px;
	}

	.skeleton-title {
		width: 120px;
		height: 20px;
		margin-bottom: 4px;
	}

	.skeleton-subtitle {
		width: 80px;
		height: 16px;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}
</style>
