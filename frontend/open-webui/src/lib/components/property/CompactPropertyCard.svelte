<script lang="ts">
	/**
	 * Compact Property Card - OpenAI Design Standards Compliant
	 *
	 * Follows OpenAI principle: "One card, a few key details, a clear CTA"
	 *
	 * Design Principles:
	 * - Shows ONLY 4 critical data points (title, location, key feature, price)
	 * - ONE clear call-to-action
	 * - Fits in conversational flow (max height 100px)
	 * - Brand color ONLY on CTA button
	 * - WCAG AA accessible
	 */

	import type { Property } from '$lib/apis/ree-ai';

	export let property: Property;
	export let onViewDetails: ((property: Property) => void) | undefined = undefined;

	// Format price in Vietnamese style
	const formatPrice = (price: number): string => {
		if (price >= 1000000000) {
			return `${(price / 1000000000).toFixed(1)} tỷ`;
		}
		return `${(price / 1000000).toFixed(0)} triệu`;
	};

	// Get ONE key feature (most relevant to user)
	const getKeyFeature = (property: Property): string => {
		const parts: string[] = [];

		// Property type specific features
		if (property.property_type === 'apartment' || property.property_type === 'house') {
			if (property.bedrooms) {
				parts.push(`${property.bedrooms}PN`);
			}
		}

		// Always show area (universal)
		if (property.area) {
			parts.push(`${property.area.toFixed(0)}m²`);
		}

		return parts.join(' • ') || 'N/A';
	};

	// Handle CTA click
	const handleClick = () => {
		if (onViewDetails) {
			onViewDetails(property);
		}
	};

	// Get fallback image
	const propertyImage = property.images && property.images.length > 0
		? property.images[0]
		: '/placeholder-property.jpg';
</script>

<article
	class="compact-property-card"
	role="article"
	aria-label="Thông tin bất động sản: {property.title}"
>
	<!-- Thumbnail Image -->
	<div class="thumbnail-container">
		<img
			src={propertyImage}
			alt={property.title}
			class="thumbnail"
			loading="lazy"
		/>
	</div>

	<!-- Property Information -->
	<div class="content">
		<!-- Title (1 line max) -->
		<h4 class="title">{property.title}</h4>

		<!-- Location + Key Feature (1 line) -->
		<p class="metadata">
			<span class="location" aria-label="Vị trí">
				📍 {property.location}
			</span>
			<span class="separator" aria-hidden="true">•</span>
			<span class="feature" aria-label="Đặc điểm">
				{getKeyFeature(property)}
			</span>
		</p>

		<!-- Price (emphasized) -->
		<p class="price">
			<span class="sr-only">Giá:</span>
			<strong aria-label="{property.price.toLocaleString()} đồng Việt Nam">
				{formatPrice(property.price)} VNĐ
			</strong>
		</p>
	</div>

	<!-- ONE Clear CTA -->
	<button
		class="cta-button"
		on:click={handleClick}
		aria-label="Xem chi tiết {property.title}"
	>
		Xem chi tiết →
	</button>
</article>

<style>
	/* Container - Horizontal layout for chat integration */
	.compact-property-card {
		display: flex;
		gap: 12px;
		padding: 12px;
		border: 1px solid var(--border-color, #e5e7eb);
		border-radius: 8px;
		align-items: center;
		max-width: 500px;
		background: var(--bg-primary, #ffffff);
		transition: box-shadow 0.2s ease;
	}

	.compact-property-card:hover {
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
	}

	/* Thumbnail - Small, square aspect ratio */
	.thumbnail-container {
		flex-shrink: 0;
		width: 64px;
		height: 64px;
		border-radius: 6px;
		overflow: hidden;
		background: var(--bg-secondary, #f3f4f6);
	}

	.thumbnail {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	/* Content - Flexible text container */
	.content {
		flex: 1;
		min-width: 0; /* Allow text truncation */
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	/* Title - Single line with ellipsis */
	.title {
		font-size: 14px;
		font-weight: 600;
		color: var(--text-primary, #111827);
		margin: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		line-height: 1.4;
	}

	/* Metadata - Location + Key Feature */
	.metadata {
		font-size: 12px;
		color: var(--text-secondary, #6b7280);
		margin: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.separator {
		margin: 0 6px;
	}

	/* Price - Emphasized with weight, NOT custom color */
	.price {
		font-size: 14px;
		margin: 0;
	}

	.price strong {
		font-weight: 700;
		color: var(--text-primary, #111827);
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

	/* CTA Button - ONLY place for brand color (OpenAI requirement) */
	.cta-button {
		flex-shrink: 0;
		padding: 8px 16px;
		background: var(--brand-primary, #3b82f6);
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		white-space: nowrap;
		transition: background 0.2s ease;
	}

	.cta-button:hover {
		background: var(--brand-primary-hover, #2563eb);
	}

	.cta-button:focus-visible {
		outline: 2px solid var(--brand-primary, #3b82f6);
		outline-offset: 2px;
	}

	/* Mobile Responsive - Stack vertically on small screens */
	@media (max-width: 480px) {
		.compact-property-card {
			flex-direction: column;
			align-items: stretch;
		}

		.thumbnail-container {
			width: 100%;
			height: 120px;
		}

		.cta-button {
			width: 100%;
		}
	}

	/* Dark mode support (if needed) */
	@media (prefers-color-scheme: dark) {
		.compact-property-card {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
		}

		.title {
			color: var(--text-primary-dark, #f9fafb);
		}

		.metadata {
			color: var(--text-secondary-dark, #9ca3af);
		}

		.price strong {
			color: var(--text-primary-dark, #f9fafb);
		}
	}
</style>
