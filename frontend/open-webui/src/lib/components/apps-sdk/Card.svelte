<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import ListGroup from './ListGroup.svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let headerTitle: string = '';
	export let hasHeader: boolean = true;
	export let hasFooter: boolean = true;
	export let headerImage: string = '';
	export let footerButtonText: string = 'Action';
	export let footerButtonVariant: 'primary' | 'secondary' = 'primary';
	export let items: Array<{
		title: string;
		subtitle?: string;
		imageUrl?: string;
		actionIcon?: 'plus' | 'chevron' | 'check';
	}> = [];

	function handleFooterClick() {
		dispatch('footerAction');
	}

	function handleHeaderAction() {
		dispatch('headerAction');
	}

	function handleItemAction(event: CustomEvent) {
		dispatch('itemAction', event.detail);
	}
</script>

<div class="card">
	<div class="card-inner">
		{#if headerImage}
			<div class="card-header-image">
				<img src={headerImage} alt={headerTitle} />
			</div>
		{/if}

		{#if hasHeader}
			<div class="card-header">
				<div class="header-left">
					<p class="header-title">{headerTitle}</p>
				</div>
				<div class="header-right">
					<button class="header-action" on:click={handleHeaderAction}>
						<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M14.166 2.5C14.3849 2.28113 14.6447 2.10752 14.9307 1.98906C15.2167 1.87061 15.5232 1.80965 15.8327 1.80965C16.1422 1.80965 16.4487 1.87061 16.7347 1.98906C17.0206 2.10752 17.2805 2.28113 17.4993 2.5C17.7182 2.71887 17.8918 2.97871 18.0103 3.26468C18.1287 3.55064 18.1897 3.85714 18.1897 4.16667C18.1897 4.47619 18.1287 4.78269 18.0103 5.06866C17.8918 5.35462 17.7182 5.61446 17.4993 5.83333L6.24935 17.0833L1.66602 18.3333L2.91602 13.75L14.166 2.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</button>
				</div>
			</div>
		{/if}

		{#if items.length > 0}
			<ListGroup {items} on:itemAction={handleItemAction} />
		{/if}

		<slot />

		{#if hasFooter}
			<div class="card-footer">
				<button
					class="footer-button"
					class:primary={footerButtonVariant === 'primary'}
					class:secondary={footerButtonVariant === 'secondary'}
					on:click={handleFooterClick}
				>
					{footerButtonText}
				</button>
			</div>
		{/if}
	</div>
</div>

<style>
	.card {
		background: white;
		border: 0.5px solid var(--border-default, rgba(13, 13, 13, 0.15));
		border-radius: 24px;
		width: 100%;
		max-width: 361px;
	}

	.dark .card {
		background: var(--bg-primary);
		border-color: var(--border-default-dark);
	}

	.card-inner {
		display: flex;
		flex-direction: column;
		align-items: center;
		overflow: hidden;
		border-radius: inherit;
	}

	.card-header-image {
		width: 100%;
		aspect-ratio: 362/210;
		overflow: hidden;
	}

	.card-header-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.card-header {
		display: flex;
		gap: 8px;
		align-items: center;
		height: 56px;
		width: 100%;
		padding: 0 8px 0 16px;
		box-sizing: border-box;
	}

	.header-left {
		display: flex;
		flex: 1 0 0;
		gap: 10px;
		align-items: center;
		min-width: 0;
	}

	.header-title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 17px;
		line-height: 23px;
		letter-spacing: -0.43px;
		color: var(--text-primary);
	}

	.header-right {
		display: flex;
		gap: 8px;
		align-items: center;
	}

	.header-action {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 44px;
		height: 44px;
		background: transparent;
		border: none;
		cursor: pointer;
		color: var(--text-primary);
		border-radius: 8px;
		transition: background-color var(--transition-base);
	}

	.header-action:hover {
		background: var(--bg-tertiary);
	}

	.card-footer {
		display: flex;
		gap: 8px;
		align-items: center;
		padding: 16px;
		width: 100%;
		box-sizing: border-box;
	}

	.footer-button {
		flex: 1 0 0;
		height: 44px;
		padding: 15px 24px;
		border-radius: 999px;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 15px;
		line-height: 24px;
		letter-spacing: -0.24px;
		cursor: pointer;
		border: none;
		transition: background-color var(--transition-base);
	}

	.footer-button.primary {
		background: var(--brand-primary);
		color: var(--text-inverse);
	}

	.footer-button.primary:hover {
		background: var(--brand-primary-hover);
	}

	.footer-button.secondary {
		background: var(--bg-tertiary);
		color: var(--text-primary);
	}

	.footer-button.secondary:hover {
		background: var(--bg-secondary);
	}
</style>
