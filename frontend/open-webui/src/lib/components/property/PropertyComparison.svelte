<script lang="ts">
	/**
	 * Property Comparison Component
	 *
	 * OpenAI Intelligent Design: Help users make informed decisions
	 *
	 * Features:
	 * - Side-by-side comparison of 2-3 properties
	 * - Highlight differences (better/worse/equal)
	 * - Score each property based on user preferences
	 * - Clear CTAs for next actions
	 * - ARIA accessible comparison table
	 */

	import { onMount } from 'svelte';
	import type { Property } from '$lib/apis/ree-ai';

	export let properties: Property[] = [];
	export let isOpen: boolean = false;
	export let onClose: (() => void) | undefined = undefined;
	export let onSelectProperty: ((property: Property) => void) | undefined = undefined;

	// Limit to 3 properties for clarity
	$: comparedProperties = properties.slice(0, 3);

	// Comparison attributes
	const attributes = [
		{ key: 'price', label: 'Giá', format: formatPrice, unit: 'VNĐ', compare: 'lower_better' },
		{ key: 'area', label: 'Diện tích', format: (v: number) => v.toFixed(0), unit: 'm²', compare: 'higher_better' },
		{ key: 'bedrooms', label: 'Phòng ngủ', format: (v: number) => v || 'N/A', unit: '', compare: 'higher_better' },
		{ key: 'bathrooms', label: 'Phòng tắm', format: (v: number) => v || 'N/A', unit: '', compare: 'higher_better' },
		{ key: 'property_type', label: 'Loại hình', format: getPropertyTypeLabel, unit: '', compare: 'none' },
		{ key: 'location', label: 'Vị trí', format: (v: string) => v, unit: '', compare: 'none' }
	];

	function formatPrice(price: number): string {
		if (price >= 1000000000) {
			return `${(price / 1000000000).toFixed(1)} tỷ`;
		}
		return `${(price / 1000000).toFixed(0)} triệu`;
	}

	function getPropertyTypeLabel(type: string): string {
		const labels: Record<string, string> = {
			apartment: 'Căn hộ',
			house: 'Nhà riêng',
			villa: 'Biệt thự',
			land: 'Đất nền',
			townhouse: 'Nhà phố',
			office: 'Văn phòng'
		};
		return labels[type] || type;
	}

	function getComparisonClass(attr: any, propertyValue: any, allValues: any[]): string {
		if (attr.compare === 'none') return '';

		const numericValues = allValues.filter(v => typeof v === 'number');
		if (numericValues.length === 0) return '';

		const numValue = typeof propertyValue === 'number' ? propertyValue : 0;

		if (attr.compare === 'lower_better') {
			const min = Math.min(...numericValues);
			if (numValue === min) return 'best-value';
			const max = Math.max(...numericValues);
			if (numValue === max) return 'worst-value';
		} else if (attr.compare === 'higher_better') {
			const max = Math.max(...numericValues);
			if (numValue === max) return 'best-value';
			const min = Math.min(...numericValues);
			if (numValue === min) return 'worst-value';
		}

		return '';
	}

	function calculateScore(property: Property): number {
		// Simple scoring based on price and area value
		const priceScore = property.price < 5000000000 ? 30 : property.price < 10000000000 ? 20 : 10;
		const areaScore = property.area > 100 ? 30 : property.area > 70 ? 20 : 10;
		const bedroomScore = (property.bedrooms || 0) * 10;
		const bathroomScore = (property.bathrooms || 0) * 5;

		const total = priceScore + areaScore + bedroomScore + bathroomScore;
		return Math.min(100, total);
	}

	// Handle ESC key
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && isOpen && onClose) {
			onClose();
		}
	}

	$: if (isOpen) {
		document.body.style.overflow = 'hidden';
	} else {
		document.body.style.overflow = '';
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen && comparedProperties.length > 0}
	<div
		class="comparison-overlay"
		role="dialog"
		aria-modal="true"
		aria-labelledby="comparison-title"
	>
		<!-- Backdrop -->
		<button
			class="backdrop"
			on:click={onClose}
			aria-label="Đóng so sánh"
			tabindex="-1"
		></button>

		<!-- Comparison content -->
		<div class="comparison-content">
			<!-- Header -->
			<header class="comparison-header">
				<h2 id="comparison-title">So sánh bất động sản ({comparedProperties.length})</h2>

				<button class="close-button" on:click={onClose} aria-label="Đóng">
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
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</header>

			<!-- Comparison table -->
			<div class="comparison-table-container">
				<table class="comparison-table" role="table" aria-label="Bảng so sánh bất động sản">
					<thead>
						<tr>
							<th scope="col" class="attribute-header">
								<span class="sr-only">Thuộc tính</span>
							</th>
							{#each comparedProperties as property (property.property_id)}
								<th scope="col" class="property-header">
									<!-- Property image -->
									<div class="property-image-small">
										{#if property.images && property.images.length > 0}
											<img src={property.images[0]} alt={property.title} />
										{:else}
											<div class="placeholder-small">🏠</div>
										{/if}
									</div>

									<!-- Property title -->
									<div class="property-title-small">
										{property.title}
									</div>

									<!-- Overall score -->
									<div class="property-score-badge">
										<span class="score-label">Điểm:</span>
										<span class="score-value">{calculateScore(property)}/100</span>
									</div>
								</th>
							{/each}
						</tr>
					</thead>

					<tbody>
						{#each attributes as attr}
							<tr>
								<th scope="row" class="attribute-label">{attr.label}</th>
								{#each comparedProperties as property}
									{@const value = property[attr.key]}
									{@const allValues = comparedProperties.map(p => p[attr.key])}
									{@const compClass = getComparisonClass(attr, value, allValues)}
									<td class="attribute-value {compClass}">
										{#if value !== undefined && value !== null}
											<span class="value">
												{attr.format(value)}
												{#if attr.unit}
													<span class="unit">{attr.unit}</span>
												{/if}
											</span>

											{#if compClass === 'best-value'}
												<span class="indicator best" aria-label="Tốt nhất">✓</span>
											{:else if compClass === 'worst-value'}
												<span class="indicator worst" aria-label="Kém nhất">−</span>
											{/if}
										{:else}
											<span class="value-na">N/A</span>
										{/if}
									</td>
								{/each}
							</tr>
						{/each}
					</tbody>

					<!-- Action row -->
					<tfoot>
						<tr>
							<th scope="row" class="attribute-label">Hành động</th>
							{#each comparedProperties as property}
								<td class="action-cell">
									<button
										class="select-button"
										on:click={() => onSelectProperty && onSelectProperty(property)}
										aria-label="Chọn {property.title}"
									>
										Chọn BĐS này
									</button>
								</td>
							{/each}
						</tr>
					</tfoot>
				</table>
			</div>

			<!-- Legend -->
			<div class="comparison-legend" role="note" aria-label="Chú thích">
				<p class="legend-title">Chú thích:</p>
				<div class="legend-items">
					<span class="legend-item">
						<span class="indicator best">✓</span> Giá trị tốt nhất
					</span>
					<span class="legend-item">
						<span class="indicator worst">−</span> Giá trị kém nhất
					</span>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	/* OpenAI Design Standards Compliant */

	.comparison-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--space-6, 24px);
	}

	.backdrop {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		cursor: pointer;
		border: none;
		padding: 0;
	}

	.comparison-content {
		position: relative;
		width: 100%;
		max-width: 1200px;
		max-height: 90vh;
		background: var(--bg-primary, #ffffff);
		border-radius: var(--radius-lg, 12px);
		box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.12));
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.comparison-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-6, 24px);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
		flex-shrink: 0;
	}

	.comparison-header h2 {
		font-size: var(--text-2xl, 24px);
		font-weight: var(--font-bold, 700);
		color: var(--text-primary, #111827);
		margin: 0;
	}

	.close-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40px;
		height: 40px;
		border: none;
		background: var(--bg-secondary, #f3f4f6);
		border-radius: var(--radius-base, 6px);
		cursor: pointer;
		transition: background var(--transition-base, 0.2s);
	}

	.close-button:hover {
		background: var(--bg-tertiary, #e5e7eb);
	}

	.close-button svg {
		width: 20px;
		height: 20px;
		color: var(--text-primary, #111827);
	}

	.comparison-table-container {
		flex: 1;
		overflow: auto;
		padding: var(--space-6, 24px);
	}

	.comparison-table {
		width: 100%;
		border-collapse: separate;
		border-spacing: 0;
	}

	.attribute-header {
		width: 150px;
	}

	.property-header {
		text-align: center;
		padding: var(--space-4, 16px);
		border-bottom: 2px solid var(--border-color, #e5e7eb);
	}

	.property-image-small {
		width: 80px;
		height: 80px;
		margin: 0 auto var(--space-3, 12px);
		border-radius: var(--radius-base, 6px);
		overflow: hidden;
	}

	.property-image-small img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.placeholder-small {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--bg-secondary, #f3f4f6);
		font-size: var(--text-3xl, 28px);
	}

	.property-title-small {
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-semibold, 600);
		color: var(--text-primary, #111827);
		margin-bottom: var(--space-2, 8px);
		line-height: 1.4;
		max-width: 200px;
		margin-left: auto;
		margin-right: auto;
	}

	.property-score-badge {
		display: inline-flex;
		align-items: center;
		gap: var(--space-1, 4px);
		padding: var(--space-1, 4px) var(--space-2, 8px);
		background: var(--color-info-bg, #dbeafe);
		color: var(--color-info, #2563eb);
		border-radius: var(--radius-full, 16px);
		font-size: var(--text-xs, 12px);
		font-weight: var(--font-semibold, 600);
	}

	.attribute-label {
		text-align: left;
		padding: var(--space-3, 12px) var(--space-4, 16px);
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-medium, 500);
		color: var(--text-secondary, #6b7280);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
		background: var(--bg-secondary, #f3f4f6);
	}

	.attribute-value {
		text-align: center;
		padding: var(--space-3, 12px);
		font-size: var(--text-sm, 14px);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
	}

	.value {
		display: inline-flex;
		align-items: baseline;
		gap: var(--space-1, 4px);
		font-weight: var(--font-semibold, 600);
		color: var(--text-primary, #111827);
	}

	.unit {
		font-size: var(--text-xs, 12px);
		color: var(--text-secondary, #6b7280);
		font-weight: var(--font-normal, 400);
	}

	.value-na {
		color: var(--text-tertiary, #9ca3af);
		font-style: italic;
	}

	.best-value {
		background: var(--color-success-bg, #d1fae5);
	}

	.worst-value {
		background: var(--color-error-bg, #fee2e2);
	}

	.indicator {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 20px;
		height: 20px;
		border-radius: 50%;
		font-size: var(--text-xs, 12px);
		font-weight: var(--font-bold, 700);
		margin-left: var(--space-2, 8px);
	}

	.indicator.best {
		background: var(--color-success, #059669);
		color: white;
	}

	.indicator.worst {
		background: var(--color-error, #dc2626);
		color: white;
	}

	.action-cell {
		text-align: center;
		padding: var(--space-4, 16px);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
	}

	/* OpenAI Compliance: Brand color ONLY on primary CTA */
	.select-button {
		padding: var(--space-2, 8px) var(--space-4, 16px);
		background: var(--brand-primary, #3b82f6);
		color: var(--text-inverse, white);
		border: none;
		border-radius: var(--radius-base, 6px);
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-semibold, 600);
		cursor: pointer;
		transition: background var(--transition-base, 0.2s);
	}

	.select-button:hover {
		background: var(--brand-primary-hover, #2563eb);
	}

	.select-button:focus-visible {
		outline: 2px solid var(--brand-primary, #3b82f6);
		outline-offset: 2px;
	}

	.comparison-legend {
		padding: var(--space-4, 16px) var(--space-6, 24px);
		background: var(--bg-secondary, #f3f4f6);
		border-top: 1px solid var(--border-color, #e5e7eb);
	}

	.legend-title {
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-semibold, 600);
		color: var(--text-primary, #111827);
		margin: 0 0 var(--space-2, 8px) 0;
	}

	.legend-items {
		display: flex;
		gap: var(--space-6, 24px);
	}

	.legend-item {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2, 8px);
		font-size: var(--text-sm, 14px);
		color: var(--text-secondary, #6b7280);
	}

	/* Screen reader only */
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

	/* Dark mode */
	@media (prefers-color-scheme: dark) {
		.comparison-content {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
		}

		.comparison-header,
		.comparison-legend {
			border-color: var(--border-color-dark, #374151);
		}

		.attribute-label {
			background: var(--bg-secondary-dark, #111827);
		}
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.comparison-content {
			margin: 0;
			max-height: 100vh;
			border-radius: 0;
		}

		.comparison-table-container {
			overflow-x: auto;
		}

		.property-header {
			min-width: 150px;
		}
	}
</style>
