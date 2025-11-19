<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let text: string = '';
	export let variant: 'primary' | 'secondary' | 'warning' | 'outline' = 'primary';
	export let size: 'small' | 'medium' | 'large' = 'medium';
	export let disabled: boolean = false;
	export let fullWidth: boolean = false;

	function handleClick() {
		if (!disabled) {
			dispatch('click');
		}
	}
</script>

<button
	class="sdk-button {variant} {size}"
	class:full-width={fullWidth}
	{disabled}
	on:click={handleClick}
>
	{text}
	<slot />
</button>

<style>
	.sdk-button {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 4px;
		border: none;
		border-radius: 999px;
		font-family: var(--font-sans);
		font-weight: 600;
		cursor: pointer;
		transition: all var(--transition-base);
	}

	/* Sizes */
	.sdk-button.small {
		padding: 8px 16px;
		font-size: 12px;
		line-height: 16px;
	}

	.sdk-button.medium {
		padding: 15px 24px;
		font-size: 14px;
		line-height: 18px;
		letter-spacing: -0.3px;
	}

	.sdk-button.large {
		padding: 16px 32px;
		font-size: 16px;
		line-height: 24px;
	}

	/* Variants */
	.sdk-button.primary {
		background: var(--brand-primary);
		color: var(--text-inverse);
	}

	.sdk-button.primary:hover:not(:disabled) {
		background: var(--brand-primary-hover);
	}

	.sdk-button.secondary {
		background: var(--bg-tertiary);
		color: var(--text-primary);
	}

	.sdk-button.secondary:hover:not(:disabled) {
		background: var(--bg-secondary);
	}

	.sdk-button.warning {
		background: var(--status-warning, #e25507);
		color: white;
	}

	.sdk-button.warning:hover:not(:disabled) {
		background: var(--status-warning-hover, #c94a06);
	}

	.sdk-button.outline {
		background: transparent;
		border: 1px solid var(--border-default);
		color: var(--text-primary);
	}

	.sdk-button.outline:hover:not(:disabled) {
		background: var(--bg-tertiary);
	}

	/* States */
	.sdk-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.sdk-button.full-width {
		width: 100%;
	}
</style>
