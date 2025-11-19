<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import MediaCarousel from './MediaCarousel.svelte';
	import Button from './Button.svelte';
	import ListGroup from './ListGroup.svelte';

	const dispatch = createEventDispatcher();

	// Props - Property data for REE AI Inspector
	export let id: string = '';
	export let title: string = '';
	export let address: string = '';
	export let price: string = '';
	export let pricePerM2: string = '';
	export let area: string = '';
	export let bedrooms: number = 0;
	export let bathrooms: number = 0;
	export let floors: number = 0;
	export let direction: string = '';
	export let images: string[] = [];
	export let description: string = '';
	export let propertyType: string = '';
	export let transactionType: 'sale' | 'rent' = 'sale';
	export let legalStatus: string = '';
	export let furniture: string = '';
	export let contact: { name: string; phone: string } | null = null;
	export let amenities: string[] = [];

	function handleClose() {
		dispatch('close');
	}

	function handleContact() {
		dispatch('contact', { id, contact });
	}

	function handleSave() {
		dispatch('save', { id });
	}

	function handleShare() {
		dispatch('share', { id, title });
	}

	// Build specs list for ListGroup
	$: specItems = [
		...(area ? [{ title: 'Diện tích', subtitle: `${area} m²`, actionIcon: 'chevron' as const }] : []),
		...(bedrooms > 0 ? [{ title: 'Phòng ngủ', subtitle: `${bedrooms} phòng`, actionIcon: 'chevron' as const }] : []),
		...(bathrooms > 0 ? [{ title: 'Phòng tắm', subtitle: `${bathrooms} phòng`, actionIcon: 'chevron' as const }] : []),
		...(floors > 0 ? [{ title: 'Số tầng', subtitle: `${floors} tầng`, actionIcon: 'chevron' as const }] : []),
		...(direction ? [{ title: 'Hướng', subtitle: direction, actionIcon: 'chevron' as const }] : []),
		...(legalStatus ? [{ title: 'Pháp lý', subtitle: legalStatus, actionIcon: 'chevron' as const }] : []),
		...(furniture ? [{ title: 'Nội thất', subtitle: furniture, actionIcon: 'chevron' as const }] : [])
	];
</script>

<div class="property-inspector">
	<div class="inspector-header">
		<button class="header-btn close" on:click={handleClose}>
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
			</svg>
		</button>
		<div class="header-actions">
			<button class="header-btn" on:click={handleShare}>
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M4 12V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M16 6L12 2L8 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M12 2V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
			<button class="header-btn" on:click={handleSave}>
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
			</button>
		</div>
	</div>

	{#if images.length > 0}
		<div class="media-section">
			<MediaCarousel {images} aspectRatio="420/280" />
		</div>
	{/if}

	<div class="details-section">
		<!-- Title and Price -->
		<div class="main-info">
			<div class="title-row">
				<h2 class="title">{title}</h2>
				{#if propertyType}
					<span class="property-type">{propertyType}</span>
				{/if}
			</div>
			<p class="address">{address}</p>

			<div class="price-row">
				<div class="price-main">
					<span class="price">{price}</span>
					{#if transactionType === 'rent'}
						<span class="price-period">/tháng</span>
					{/if}
				</div>
				{#if pricePerM2}
					<span class="price-per-m2">{pricePerM2}/m²</span>
				{/if}
			</div>
		</div>

		<!-- Quick Stats -->
		<div class="quick-stats">
			{#if area}
				<div class="stat">
					<span class="stat-value">{area}</span>
					<span class="stat-label">m²</span>
				</div>
			{/if}
			{#if bedrooms > 0}
				<div class="stat">
					<span class="stat-value">{bedrooms}</span>
					<span class="stat-label">PN</span>
				</div>
			{/if}
			{#if bathrooms > 0}
				<div class="stat">
					<span class="stat-value">{bathrooms}</span>
					<span class="stat-label">WC</span>
				</div>
			{/if}
			{#if floors > 0}
				<div class="stat">
					<span class="stat-value">{floors}</span>
					<span class="stat-label">Tầng</span>
				</div>
			{/if}
		</div>

		<!-- Action Buttons -->
		<div class="action-buttons">
			<Button text="Liên hệ ngay" variant="primary" fullWidth on:click={handleContact} />
			<Button text="Lưu tin" variant="secondary" on:click={handleSave} />
		</div>

		<!-- Description -->
		{#if description}
			<div class="section">
				<h3 class="section-title">Mô tả</h3>
				<p class="description">{description}</p>
			</div>
		{/if}

		<!-- Specifications -->
		{#if specItems.length > 0}
			<div class="section">
				<h3 class="section-title">Thông tin chi tiết</h3>
				<ListGroup items={specItems} showActions={false} />
			</div>
		{/if}

		<!-- Amenities -->
		{#if amenities.length > 0}
			<div class="section">
				<h3 class="section-title">Tiện ích</h3>
				<div class="amenities-grid">
					{#each amenities as amenity}
						<div class="amenity-item">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
								<path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
							</svg>
							<span>{amenity}</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Contact Info -->
		{#if contact}
			<div class="section contact-section">
				<h3 class="section-title">Thông tin liên hệ</h3>
				<div class="contact-info">
					<div class="contact-name">{contact.name}</div>
					<a href="tel:{contact.phone}" class="contact-phone">{contact.phone}</a>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.property-inspector {
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 420px;
		background: var(--bg-primary);
		height: 100%;
		overflow-y: auto;
	}

	.inspector-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px;
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		z-index: 10;
	}

	.header-actions {
		display: flex;
		gap: 8px;
	}

	.header-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		background: rgba(255, 255, 255, 0.9);
		border: none;
		border-radius: 50%;
		cursor: pointer;
		color: var(--text-primary);
		transition: all var(--transition-base);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.header-btn:hover {
		background: white;
		transform: scale(1.05);
	}

	.media-section {
		width: 100%;
		position: relative;
	}

	.details-section {
		display: flex;
		flex-direction: column;
		gap: 20px;
		padding: 20px;
	}

	.main-info {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.title-row {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
	}

	.title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 22px;
		line-height: 28px;
		color: var(--text-primary);
		flex: 1;
	}

	.property-type {
		padding: 4px 8px;
		background: var(--bg-tertiary);
		border-radius: 6px;
		font-family: var(--font-sans);
		font-size: 12px;
		font-weight: 500;
		color: var(--text-secondary);
		flex-shrink: 0;
	}

	.address {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 14px;
		line-height: 20px;
		color: var(--text-secondary);
	}

	.price-row {
		display: flex;
		align-items: baseline;
		gap: 12px;
		margin-top: 8px;
	}

	.price-main {
		display: flex;
		align-items: baseline;
		gap: 4px;
	}

	.price {
		font-family: var(--font-sans);
		font-weight: 700;
		font-size: 24px;
		line-height: 30px;
		color: var(--brand-primary);
	}

	.price-period {
		font-family: var(--font-sans);
		font-size: 14px;
		color: var(--text-secondary);
	}

	.price-per-m2 {
		font-family: var(--font-sans);
		font-size: 13px;
		color: var(--text-tertiary);
	}

	.quick-stats {
		display: flex;
		gap: 24px;
		padding: 16px 0;
		border-top: 1px solid var(--border-light);
		border-bottom: 1px solid var(--border-light);
	}

	.stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}

	.stat-value {
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 18px;
		color: var(--text-primary);
	}

	.stat-label {
		font-family: var(--font-sans);
		font-size: 12px;
		color: var(--text-secondary);
	}

	.action-buttons {
		display: flex;
		gap: 8px;
	}

	.section {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.section-title {
		margin: 0;
		font-family: var(--font-sans);
		font-weight: 600;
		font-size: 16px;
		color: var(--text-primary);
	}

	.description {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 14px;
		line-height: 22px;
		color: var(--text-secondary);
		white-space: pre-wrap;
	}

	.amenities-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 8px;
	}

	.amenity-item {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		background: var(--bg-tertiary);
		border-radius: 8px;
		font-family: var(--font-sans);
		font-size: 13px;
		color: var(--text-primary);
	}

	.amenity-item svg {
		color: var(--brand-primary);
		flex-shrink: 0;
	}

	.contact-section {
		padding: 16px;
		background: var(--bg-tertiary);
		border-radius: 12px;
	}

	.contact-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.contact-name {
		font-family: var(--font-sans);
		font-weight: 500;
		font-size: 15px;
		color: var(--text-primary);
	}

	.contact-phone {
		font-family: var(--font-sans);
		font-size: 14px;
		color: var(--brand-primary);
		text-decoration: none;
	}

	.contact-phone:hover {
		text-decoration: underline;
	}
</style>
