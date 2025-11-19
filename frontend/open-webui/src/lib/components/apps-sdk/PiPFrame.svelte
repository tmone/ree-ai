<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let showCloseButton: boolean = true;
	export let actionButtonText: string = '';
	export let width: string = '768px';
	export let height: string = '420px';

	function handleClose() {
		dispatch('close');
	}

	function handleAction() {
		dispatch('action');
	}
</script>

<div class="pip-frame" style="width: {width}; height: {height};">
	{#if showCloseButton}
		<button class="close-button" on:click={handleClose}>
			<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</button>
	{/if}

	<div class="pip-content">
		<slot />
	</div>

	{#if actionButtonText}
		<div class="action-container">
			<button class="action-button" on:click={handleAction}>
				{actionButtonText}
			</button>
		</div>
	{/if}
</div>

<style>
	.pip-frame {
		position: relative;
		border: 1px solid var(--border-light, rgba(13, 13, 13, 0.05));
		border-radius: 18px;
		overflow: hidden;
		background: var(--bg-primary);
	}

	.close-button {
		position: absolute;
		top: -7px;
		left: -10px;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		padding: 10px;
		background: var(--interactive-bg-primary, #0d0d0d);
		border: none;
		border-radius: 30px;
		cursor: pointer;
		color: white;
		box-shadow: 0px 4px 8px 0px rgba(0, 0, 0, 0.16);
		z-index: 10;
		transition: background-color var(--transition-base);
	}

	.close-button:hover {
		background: var(--interactive-bg-primary-hover, #333);
	}

	.close-button svg {
		width: 12px;
		height: 12px;
	}

	.pip-content {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 100%;
		height: 100%;
		padding: 20px;
		box-sizing: border-box;
	}

	.action-container {
		position: absolute;
		bottom: 24px;
		left: 50%;
		transform: translateX(-50%);
	}

	.action-button {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 6px 16px;
		background: white;
		border: 1px solid rgba(0, 0, 0, 0.08);
		border-radius: 21px;
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 17px;
		line-height: 22px;
		letter-spacing: -0.43px;
		color: var(--brand-primary, #2979c4);
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.action-button:hover {
		background: var(--bg-tertiary);
	}

	.dark .pip-frame {
		border-color: var(--border-default-dark);
	}

	.dark .action-button {
		background: var(--bg-secondary);
		border-color: var(--border-default-dark);
	}
</style>
