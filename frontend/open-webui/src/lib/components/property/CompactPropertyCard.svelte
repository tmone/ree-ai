<script lang="ts">
	/**
	 * Compact Property Card - OpenAI Apps SDK Compliant
	 *
	 * Follows "Simple" principle: One card, a few key details, one clear CTA
	 * Design: Extracted from Figma (400px max-width, 60px thumbnail)
	 *
	 * Data points (4 only):
	 * - Title
	 * - Location + Key Feature (bedrooms + area)
	 * - Price
	 * - CTA: "View details"
	 */

	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';

	const i18n: Writable<i18nType> = getContext('i18n');

	export let property: any;
	export let onClick: ((property: any) => void) | undefined = undefined;
	export let language: string | undefined = undefined; // Override language from detected query language

	// Helper to translate with optional language override
	function t(key: string): string {
		if (language) {
			return $i18n.t(key, { lng: language });
		}
		return $i18n.t(key);
	}

	// Format price with i18n support
	function formatPrice(priceValue: string | number): string {
		// If already formatted (contains non-digit chars like "tỷ", "triệu", "billion"), return as-is
		if (typeof priceValue === 'string' && /[^\d.,\s]/.test(priceValue)) {
			return priceValue;
		}

		const num = typeof priceValue === 'string' ? parseFloat(priceValue.replace(/[,.\s]/g, '')) : priceValue;
		if (isNaN(num) || num <= 0) return t('Negotiable');

		if (num >= 1000000000) {
			const billions = num / 1000000000;
			return `${billions % 1 === 0 ? billions : billions.toFixed(1)} ${t('billion')}`;
		} else if (num >= 1000000) {
			const millions = num / 1000000;
			return `${millions % 1 === 0 ? millions : millions.toFixed(0)} ${t('million')}`;
		}
		return num.toLocaleString('vi-VN');
	}

	// Format key feature: "2BR 75m²" or "200m²" with i18n
	function getKeyFeature(prop: any): string {
		const bedrooms = prop.bedrooms || 0;
		const area = prop.area || prop.areaDisplay || '';

		if (bedrooms > 0) {
			return `${bedrooms}${t('BR')} ${area}m²`;
		}
		return `${area}m²`;
	}

	function handleClick() {
		if (onClick) {
			onClick(property);
		}
	}
</script>

<article
	class="compact-property-card"
	role="button"
	tabindex="0"
	on:click={handleClick}
	on:keypress={(e) => e.key === 'Enter' && handleClick()}
	aria-label={`Property: ${property.title}`}
>
	<!-- Thumbnail (60x60px per Figma specs) -->
	{#if property.imageUrl}
		<img
			src={property.imageUrl}
			alt={property.title}
			class="thumbnail"
			loading="lazy"
		/>
	{:else}
		<div class="thumbnail placeholder" role="img" aria-label="No image available">
			<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
			</svg>
		</div>
	{/if}

	<!-- Content: Title + Location + Price -->
	<div class="content">
		<!-- Title (1 line max, truncated) -->
		<h4 class="title">{property.title}</h4>

		<!-- Location + Key Feature (1 line) -->
		<p class="metadata">
			<span class="sr-only">Location:</span>
			📍 {property.address || property.location} • {getKeyFeature(property)}
		</p>

		<!-- Price (emphasized) -->
		<p class="price">
			<span class="sr-only">Price:</span>
			<strong>{formatPrice(property.price)}</strong>
		</p>
	</div>

	<!-- ONE clear CTA (brand color per OpenAI standards) -->
	<button
		class="btn-primary cta-button"
		on:click|stopPropagation={handleClick}
		aria-label="View property details"
	>
		{t('View details')} →
	</button>
</article>

<style>
	.compact-property-card {
		display: flex;
		gap: 12px;
		padding: 12px;
		max-width: 400px;
		background: #ffffff;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		align-items: center;
		transition: border-color 150ms ease-in-out;
		cursor: pointer;
	}

	.compact-property-card:hover {
		border-color: #d1d5db;
	}

	.compact-property-card:focus-visible {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	.thumbnail {
		width: 60px;
		height: 60px;
		min-width: 60px;
		border-radius: 6px;
		object-fit: cover;
	}

	.thumbnail.placeholder {
		display: flex;
		align-items: center;
		justify-content: center;
		background: #e8e8e8;
		color: #9ca3af;
	}

	.thumbnail.placeholder svg {
		width: 24px;
		height: 24px;
	}

	.content {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.title {
		color: #0d0d0d;
		font-size: 14px;
		font-weight: 600;
		margin: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.metadata {
		color: #6b7280;
		font-size: 12px;
		margin: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.price {
		color: #0d0d0d;
		font-size: 14px;
		font-weight: 700;
		margin: 0;
	}

	.cta-button {
		padding: 8px 16px;
		border-radius: 6px;
		font-size: 14px;
		font-weight: 600;
		white-space: nowrap;
		border: none;
		cursor: pointer;
		background-color: #3b82f6;
		color: white;
		transition: background-color 150ms ease-in-out;
	}

	.cta-button:hover {
		background-color: #2563eb;
	}

	.cta-button:active {
		background-color: #1d4ed8;
	}

	.cta-button:focus-visible {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

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

	@media (max-width: 480px) {
		.compact-property-card {
			flex-direction: column;
			align-items: stretch;
		}

		.thumbnail {
			width: 100%;
			height: 150px;
		}

		.cta-button {
			width: 100%;
		}
	}

	/* Dark mode */
	@media (prefers-color-scheme: dark) {
		.compact-property-card {
			background: #212121;
			border-color: #404040;
		}

		.compact-property-card:hover {
			border-color: #525252;
		}

		.title,
		.price {
			color: #ffffff;
		}

		.metadata {
			color: #cdcdcd;
		}

		.thumbnail.placeholder {
			background: #2d2d2d;
		}
	}
</style>
