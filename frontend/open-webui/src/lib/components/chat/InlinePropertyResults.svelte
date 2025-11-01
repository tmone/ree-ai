<script lang="ts">
	/**
	 * Inline Property Results Component
	 *
	 * OpenAI Conversational Design: Properties appear naturally in chat flow
	 *
	 * Features:
	 * - Shows max 3 properties inline (OpenAI "Simple" principle)
	 * - "View All" CTA for more results
	 * - Uses CompactPropertyCard for concise display
	 * - ARIA accessible
	 */

	import CompactPropertyCard from '../property/CompactPropertyCard.svelte';
	import type { Property } from '$lib/apis/ree-ai';

	export let properties: Property[] = [];
	export let totalResults: number = 0;
	export let userQuery: string = '';
	export let onPropertySelect: ((property: Property) => void) | undefined = undefined;
	export let onViewAll: (() => void) | undefined = undefined;

	// Show max 3 properties inline (OpenAI principle: Simple)
	$: displayedProperties = properties.slice(0, 3);
	$: hasMore = totalResults > 3;
</script>

<div class="inline-property-results" role="region" aria-label="Kết quả bất động sản">
	<!-- Intro text (OpenAI: Context-driven) -->
	<p class="results-intro">
		Tôi tìm thấy <strong>{totalResults}</strong> bất động sản phù hợp
		{#if userQuery}
			với yêu cầu "{userQuery}"
		{/if}. Đây là {displayedProperties.length} lựa chọn phù hợp nhất:
	</p>

	<!-- Property cards carousel -->
	<div class="property-carousel" role="list" aria-label="Danh sách bất động sản">
		{#each displayedProperties as property (property.property_id)}
			<div role="listitem">
				<CompactPropertyCard {property} onViewDetails={onPropertySelect} />
			</div>
		{/each}
	</div>

	<!-- View All CTA (OpenAI: One clear next action) -->
	{#if hasMore && onViewAll}
		<button class="view-all-cta" on:click={onViewAll} aria-label="Xem tất cả {totalResults} kết quả">
			Xem tất cả {totalResults} kết quả →
		</button>
	{/if}
</div>

<style>
	/* OpenAI Design Standards Compliant Styles */

	.inline-property-results {
		max-width: 600px;
		padding: var(--space-4, 16px);
		background: var(--bg-secondary, #f3f4f6);
		border-radius: var(--radius-md, 12px);
		margin: var(--space-4, 16px) 0;
	}

	.results-intro {
		margin: 0 0 var(--space-4, 16px) 0;
		font-size: var(--text-sm, 14px);
		color: var(--text-secondary, #6b7280);
		line-height: var(--leading-normal, 1.5);
	}

	.results-intro strong {
		color: var(--text-primary, #111827);
		font-weight: var(--font-semibold, 600);
	}

	.property-carousel {
		display: flex;
		flex-direction: column;
		gap: var(--space-3, 12px);
		margin-bottom: var(--space-4, 16px);
	}

	/* OpenAI Compliance: Brand color ONLY on primary CTA */
	.view-all-cta {
		width: 100%;
		padding: var(--space-3, 12px) var(--space-4, 16px);
		background: var(--brand-primary, #3b82f6);
		color: var(--text-inverse, white);
		border: none;
		border-radius: var(--radius-base, 8px);
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-semibold, 600);
		cursor: pointer;
		transition: background var(--transition-base, 0.2s);
		text-align: center;
	}

	.view-all-cta:hover {
		background: var(--brand-primary-hover, #2563eb);
	}

	.view-all-cta:focus-visible {
		outline: 2px solid var(--brand-primary, #3b82f6);
		outline-offset: 2px;
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.inline-property-results {
			background: var(--bg-secondary-dark, #111827);
		}
	}

	/* Mobile responsive */
	@media (max-width: 640px) {
		.inline-property-results {
			max-width: 100%;
		}
	}
</style>
