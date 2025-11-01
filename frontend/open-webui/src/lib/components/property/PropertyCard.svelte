<script lang="ts">
	import type { Property } from '$lib/apis/ree-ai';

	export let property: Property;
	export let onClick: ((property: Property) => void) | undefined = undefined;

	const formatPrice = (price: number): string => {
		if (price >= 1000000000) {
			return `${(price / 1000000000).toFixed(1)} tỷ`;
		}
		return `${(price / 1000000).toFixed(0)} triệu`;
	};

	const formatArea = (area: number): string => {
		return `${area.toFixed(0)} m²`;
	};

	const getPropertyTypeLabel = (type: string): string => {
		const labels: Record<string, string> = {
			apartment: 'Căn hộ',
			house: 'Nhà riêng',
			villa: 'Biệt thự',
			land: 'Đất nền',
			townhouse: 'Nhà phố',
			office: 'Văn phòng'
		};
		return labels[type] || type;
	};
</script>

<article
	class="property-card"
	role="article"
	aria-label="Thông tin bất động sản: {property.title}"
>
	<button
		class="property-card-clickable"
		on:click={() => onClick && onClick(property)}
		type="button"
		aria-label="Xem chi tiết {property.title}"
	>
		<div class="property-image">
			{#if property.images && property.images.length > 0}
				<img src={property.images[0]} alt={property.title} loading="lazy" />
			{:else}
				<div class="placeholder-image" role="img" aria-label="Hình ảnh bất động sản chưa có sẵn">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
						/>
					</svg>
				</div>
			{/if}
			<!-- OpenAI Compliance: Badge is OK to use brand color -->
			<div class="property-type-badge" aria-label="Loại hình: {getPropertyTypeLabel(property.property_type)}">
				{getPropertyTypeLabel(property.property_type)}
			</div>
		</div>

		<div class="property-content">
			<h3 class="property-title">{property.title}</h3>

			<div class="property-location">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					aria-hidden="true"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
					/>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
					/>
				</svg>
				<span aria-label="Vị trí">{property.location}</span>
			</div>

			<!-- WCAG AA: Use semantic HTML (dl/dt/dd) for stats -->
			<dl class="property-stats" aria-label="Thông số bất động sản">
				<div class="stat">
					<dt class="stat-label">Diện tích</dt>
					<dd class="stat-value">{formatArea(property.area)}</dd>
				</div>
				{#if property.bedrooms}
					<div class="stat">
						<dt class="stat-label">Phòng ngủ</dt>
						<dd class="stat-value">{property.bedrooms}</dd>
					</div>
				{/if}
				{#if property.bathrooms}
					<div class="stat">
						<dt class="stat-label">Phòng tắm</dt>
						<dd class="stat-value">{property.bathrooms}</dd>
					</div>
				{/if}
			</dl>

			<!-- OpenAI Compliance: Use font-weight for emphasis, not custom color -->
			<p class="property-price">
				<span class="sr-only">Giá:</span>
				<strong aria-label="{property.price.toLocaleString()} đồng Việt Nam">
					{formatPrice(property.price)} VNĐ
				</strong>
			</p>

			{#if property.score}
				<div class="property-score" aria-label="Độ phù hợp: {(property.score * 100).toFixed(0)} phần trăm">
					Độ phù hợp: {(property.score * 100).toFixed(0)}%
				</div>
			{/if}
		</div>
	</button>
</article>

<style>
	/* OpenAI Design Standards Compliant Styles */

	.property-card {
		width: 100%;
	}

	.property-card-clickable {
		display: flex;
		flex-direction: column;
		background: var(--bg-primary, #ffffff);
		border-radius: var(--radius-md, 12px);
		overflow: hidden;
		box-shadow: var(--shadow-base, 0 2px 8px rgba(0, 0, 0, 0.1));
		transition: all var(--transition-base, 0.2s ease);
		cursor: pointer;
		width: 100%;
		text-align: left;
		border: 1px solid var(--border-color, #e5e7eb);
		padding: 0;
	}

	.property-card-clickable:hover {
		box-shadow: var(--shadow-md, 0 4px 16px rgba(0, 0, 0, 0.15));
		transform: translateY(-2px);
	}

	.property-card-clickable:focus-visible {
		outline: 2px solid var(--brand-primary, #3b82f6);
		outline-offset: 2px;
	}

	.property-image {
		position: relative;
		width: 100%;
		height: 200px;
		background: var(--bg-secondary, #f3f4f6);
		overflow: hidden;
	}

	.property-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.placeholder-image {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-tertiary, #9ca3af);
	}

	.placeholder-image svg {
		width: 64px;
		height: 64px;
	}

	/* OpenAI Compliance: Badge can use brand color */
	.property-type-badge {
		position: absolute;
		top: var(--space-3, 12px);
		right: var(--space-3, 12px);
		background: var(--brand-primary, rgba(59, 130, 246, 0.9));
		color: var(--text-inverse, white);
		padding: var(--space-1, 4px) var(--space-3, 12px);
		border-radius: var(--radius-full, 16px);
		font-size: var(--text-xs, 12px);
		font-weight: var(--font-semibold, 600);
	}

	.property-content {
		padding: var(--space-4, 16px);
		display: flex;
		flex-direction: column;
		gap: var(--space-3, 12px);
	}

	.property-title {
		font-size: var(--text-base, 16px);
		font-weight: var(--font-semibold, 600);
		color: var(--text-primary, #111827);
		margin: 0;
		line-height: var(--leading-tight, 1.4);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.property-location {
		display: flex;
		align-items: center;
		gap: var(--space-2, 6px);
		color: var(--text-secondary, #6b7280);
		font-size: var(--text-sm, 14px);
	}

	.property-location svg {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
	}

	/* Semantic HTML for stats (dl/dt/dd) */
	.property-stats {
		display: flex;
		gap: var(--space-4, 16px);
		padding: var(--space-3, 12px) 0;
		border-top: 1px solid var(--border-color, #e5e7eb);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
		margin: 0;
	}

	.stat {
		display: flex;
		flex-direction: column;
		gap: var(--space-1, 4px);
	}

	.stat-label {
		font-size: var(--text-xs, 12px);
		color: var(--text-secondary, #6b7280);
	}

	.stat-value {
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-semibold, 600);
		color: var(--text-primary, #111827);
		margin: 0;
	}

	/* OpenAI Compliance: Use system color + font-weight, not custom red */
	.property-price {
		font-size: var(--text-xl, 20px);
		margin: 0;
	}

	.property-price strong {
		font-weight: var(--font-bold, 700);
		color: var(--text-primary, #111827);
	}

	.property-score {
		font-size: var(--text-xs, 12px);
		color: var(--color-success, #059669);
		background: var(--color-success-bg, #d1fae5);
		padding: var(--space-1, 4px) var(--space-2, 8px);
		border-radius: var(--radius-sm, 4px);
		width: fit-content;
	}

	/* Screen reader only text */
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.property-card-clickable {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
		}
	}
</style>
