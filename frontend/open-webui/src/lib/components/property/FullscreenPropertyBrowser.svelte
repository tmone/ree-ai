<script lang="ts">
	/**
	 * Fullscreen Property Browser
	 *
	 * OpenAI Display Mode: Fullscreen for detailed browsing
	 *
	 * Features:
	 * - Immersive fullscreen experience for browsing >3 properties
	 * - Maintains chat composer overlay (OpenAI requirement)
	 * - Grid layout for efficient browsing
	 * - Filter and sort capabilities
	 * - ARIA accessible modal
	 */

	import { onMount } from 'svelte';
	import PropertyCard from './PropertyCard.svelte';
	import type { Property } from '$lib/apis/ree-ai';

	export let properties: Property[] = [];
	export let isOpen: boolean = false;
	export let onClose: (() => void) | undefined = undefined;
	export let onPropertySelect: ((property: Property) => void) | undefined = undefined;

	let sortBy: 'price_asc' | 'price_desc' | 'area_asc' | 'area_desc' | 'relevance' = 'relevance';
	let filterType: string = '';

	// Sort properties based on selected option
	$: sortedProperties = (() => {
		let sorted = [...properties];

		switch (sortBy) {
			case 'price_asc':
				sorted.sort((a, b) => a.price - b.price);
				break;
			case 'price_desc':
				sorted.sort((a, b) => b.price - a.price);
				break;
			case 'area_asc':
				sorted.sort((a, b) => a.area - b.area);
				break;
			case 'area_desc':
				sorted.sort((a, b) => b.area - a.area);
				break;
			case 'relevance':
			default:
				// Keep original order (relevance from search)
				break;
		}

		if (filterType) {
			sorted = sorted.filter((p) => p.property_type === filterType);
		}

		return sorted;
	})();

	// Handle ESC key to close
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape' && isOpen && onClose) {
			onClose();
		}
	}

	onMount(() => {
		if (isOpen) {
			// Prevent body scroll when modal is open
			document.body.style.overflow = 'hidden';
		}

		return () => {
			document.body.style.overflow = '';
		};
	});

	$: if (isOpen) {
		document.body.style.overflow = 'hidden';
	} else {
		document.body.style.overflow = '';
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
	<div
		class="fullscreen-browser-overlay"
		role="dialog"
		aria-modal="true"
		aria-labelledby="browser-title"
	>
		<!-- Backdrop -->
		<button
			class="backdrop"
			on:click={onClose}
			aria-label="Đóng trình duyệt bất động sản"
			tabindex="-1"
		></button>

		<!-- Browser content -->
		<div class="browser-content">
			<!-- Header with close button -->
			<header class="browser-header">
				<h2 id="browser-title">Tất cả kết quả ({properties.length})</h2>

				<div class="header-controls">
					<!-- Sort controls -->
					<div class="control-group">
						<label for="sort-select" class="sr-only">Sắp xếp theo</label>
						<select id="sort-select" bind:value={sortBy} class="sort-select">
							<option value="relevance">Độ phù hợp</option>
							<option value="price_asc">Giá: Thấp → Cao</option>
							<option value="price_desc">Giá: Cao → Thấp</option>
							<option value="area_asc">Diện tích: Nhỏ → Lớn</option>
							<option value="area_desc">Diện tích: Lớn → Nhỏ</option>
						</select>
					</div>

					<!-- Filter controls -->
					<div class="control-group">
						<label for="filter-select" class="sr-only">Lọc theo loại hình</label>
						<select id="filter-select" bind:value={filterType} class="filter-select">
							<option value="">Tất cả loại hình</option>
							<option value="apartment">Căn hộ</option>
							<option value="house">Nhà riêng</option>
							<option value="villa">Biệt thự</option>
							<option value="land">Đất nền</option>
							<option value="townhouse">Nhà phố</option>
							<option value="office">Văn phòng</option>
						</select>
					</div>

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
				</div>
			</header>

			<!-- Properties grid -->
			<div class="properties-grid" role="list" aria-label="Danh sách bất động sản">
				{#each sortedProperties as property (property.property_id)}
					<div role="listitem">
						<PropertyCard {property} onClick={onPropertySelect} />
					</div>
				{/each}
			</div>

			{#if sortedProperties.length === 0}
				<div class="empty-state">
					<p>Không tìm thấy bất động sản phù hợp với bộ lọc.</p>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	/* OpenAI Display Mode: Fullscreen */

	.fullscreen-browser-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
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

	.browser-content {
		position: relative;
		width: 100%;
		height: 100%;
		max-width: 1400px;
		max-height: 90vh;
		margin: var(--space-6, 24px);
		background: var(--bg-primary, #ffffff);
		border-radius: var(--radius-lg, 12px);
		box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.12));
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.browser-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: var(--space-6, 24px);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
		flex-shrink: 0;
	}

	.browser-header h2 {
		font-size: var(--text-2xl, 24px);
		font-weight: var(--font-bold, 700);
		color: var(--text-primary, #111827);
		margin: 0;
	}

	.header-controls {
		display: flex;
		gap: var(--space-3, 12px);
		align-items: center;
	}

	.control-group {
		display: flex;
		flex-direction: column;
	}

	.sort-select,
	.filter-select {
		padding: var(--space-2, 8px) var(--space-3, 12px);
		border: 1px solid var(--border-color, #e5e7eb);
		border-radius: var(--radius-base, 6px);
		font-size: var(--text-sm, 14px);
		color: var(--text-primary, #111827);
		background: var(--bg-primary, white);
		cursor: pointer;
	}

	.sort-select:focus,
	.filter-select:focus {
		outline: none;
		border-color: var(--brand-primary, #3b82f6);
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

	.properties-grid {
		flex: 1;
		overflow-y: auto;
		padding: var(--space-6, 24px);
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: var(--space-6, 24px);
		align-content: start;
	}

	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--space-16, 64px);
		color: var(--text-secondary, #6b7280);
		font-size: var(--text-base, 16px);
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
		.browser-content {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
		}

		.browser-header {
			border-bottom-color: var(--border-color-dark, #374151);
		}

		.sort-select,
		.filter-select {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
			color: var(--text-primary-dark, #f9fafb);
		}
	}

	/* Mobile responsive */
	@media (max-width: 768px) {
		.browser-content {
			margin: 0;
			max-height: 100vh;
			border-radius: 0;
		}

		.header-controls {
			flex-direction: column;
			align-items: stretch;
		}

		.properties-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
