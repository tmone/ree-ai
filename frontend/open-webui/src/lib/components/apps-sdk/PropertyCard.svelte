<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props - Property data structure for REE AI
	export let id: string = '';
	export let title: string = '';
	export let address: string = '';
	export let price: string = '';
	export let priceUnit: string = 'VNĐ';
	export let area: string = '';
	export let areaUnit: string = 'm²';
	export let bedrooms: number = 0;
	export let bathrooms: number = 0;
	export let imageUrl: string = '';
	export let propertyType: string = '';
	export let transactionType: 'sale' | 'rent' = 'sale';

	function handleClick() {
		dispatch('click', { id, title });
	}

	function handleViewDetails() {
		dispatch('viewDetails', { id });
	}

	function formatPrice(price: string): string {
		// Format Vietnamese price (e.g., "2.5 tỷ", "15 triệu/tháng")
		return price;
	}
</script>

<div class="property-card" on:click={handleClick} on:keypress={handleClick} role="button" tabindex="0">
	{#if imageUrl}
		<div class="image-container">
			<img src={imageUrl} alt={title} class="property-image" />
			<div class="image-overlay"></div>
			{#if propertyType}
				<div class="property-type-badge">
					{propertyType}
				</div>
			{/if}
			{#if transactionType === 'rent'}
				<div class="transaction-badge rent">Cho thuê</div>
			{:else}
				<div class="transaction-badge sale">Bán</div>
			{/if}
		</div>
	{/if}

	<div class="content">
		<div class="header">
			<h3 class="title">{title}</h3>
			<p class="address">{address}</p>
		</div>

		<div class="price-section">
			<span class="price">{formatPrice(price)}</span>
			<span class="price-unit">{priceUnit}</span>
		</div>

		<div class="specs">
			{#if area}
				<div class="spec-item">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M21 21H3V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M21 9V3H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M3 15V21H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					<span>{area} {areaUnit}</span>
				</div>
			{/if}
			{#if bedrooms > 0}
				<div class="spec-item">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M3 21V7C3 5.89543 3.89543 5 5 5H19C20.1046 5 21 5.89543 21 7V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M3 11H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M7 11V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					<span>{bedrooms} PN</span>
				</div>
			{/if}
			{#if bathrooms > 0}
				<div class="spec-item">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M4 12H20V16C20 18.2091 18.2091 20 16 20H8C5.79086 20 4 18.2091 4 16V12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M6 12V5C6 3.89543 6.89543 3 8 3H8.5C9.60457 3 10.5 3.89543 10.5 5V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					<span>{bathrooms} WC</span>
				</div>
			{/if}
		</div>

		<button class="view-details-btn" on:click|stopPropagation={handleViewDetails}>
			Xem chi tiết
		</button>
	</div>
</div>

<style>
	.property-card {
		display: flex;
		flex-direction: column;
		width: 260px;
		background: white;
		border: 1px solid var(--border-light, rgba(13, 13, 13, 0.05));
		border-radius: 16px;
		overflow: hidden;
		cursor: pointer;
		transition: all var(--transition-base);
		flex-shrink: 0;
	}

	.property-card:hover {
		box-shadow: var(--shadow-lg);
		transform: translateY(-2px);
	}

	.dark .property-card {
		background: var(--bg-secondary);
		border-color: var(--border-default-dark);
	}

	.image-container {
		position: relative;
		width: 100%;
		aspect-ratio: 4/3;
		overflow: hidden;
	}

	.property-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.image-overlay {
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgba(0, 0, 0, 0.3) 0%, transparent 50%);
	}

	.property-type-badge {
		position: absolute;
		top: 12px;
		left: 12px;
		padding: 4px 8px;
		background: rgba(0, 0, 0, 0.6);
		border-radius: 6px;
		font-family: var(--font-sans);
		font-size: 11px;
		font-weight: 500;
		color: white;
	}

	.transaction-badge {
		position: absolute;
		top: 12px;
		right: 12px;
		padding: 4px 8px;
		border-radius: 6px;
		font-family: var(--font-sans);
		font-size: 11px;
		font-weight: 600;
	}

	.transaction-badge.sale {
		background: var(--brand-primary);
		color: white;
	}

	.transaction-badge.rent {
		background: var(--status-warning, #e25507);
		color: white;
	}

	.content {
		display: flex;
		flex-direction: column;
		gap: 12px;
		padding: 16px;
	}

	.header {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 15px;
		line-height: 20px;
		color: var(--text-primary);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.address {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 13px;
		line-height: 18px;
		color: var(--text-secondary);
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.price-section {
		display: flex;
		align-items: baseline;
		gap: 4px;
	}

	.price {
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 18px;
		line-height: 24px;
		color: var(--brand-primary);
	}

	.price-unit {
		font-family: var(--font-sans);
		font-size: 12px;
		color: var(--text-secondary);
	}

	.specs {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
	}

	.spec-item {
		display: flex;
		align-items: center;
		gap: 4px;
		font-family: var(--font-sans);
		font-size: 12px;
		color: var(--text-secondary);
	}

	.spec-item svg {
		color: var(--text-tertiary);
	}

	.view-details-btn {
		width: 100%;
		padding: 10px;
		background: var(--bg-tertiary);
		border: none;
		border-radius: 8px;
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 13px;
		color: var(--text-primary);
		cursor: pointer;
		transition: all var(--transition-base);
	}

	.view-details-btn:hover {
		background: var(--bg-secondary);
	}
</style>
