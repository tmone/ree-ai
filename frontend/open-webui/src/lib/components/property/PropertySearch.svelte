<script lang="ts">
	import { searchProperties, type PropertySearchRequest } from '$lib/apis/ree-ai';
	import PropertyCard from './PropertyCard.svelte';
	import { toast } from 'svelte-sonner';

	export let token: string;
	export let onPropertySelect: ((property: any) => void) | undefined = undefined;

	let query = '';
	let propertyType = '';
	let location = '';
	let minPrice = '';
	let maxPrice = '';
	let minArea = '';
	let maxArea = '';

	let results: any[] = [];
	let loading = false;
	let totalResults = 0;

	const propertyTypes = [
		{ value: '', label: 'Tất cả' },
		{ value: 'apartment', label: 'Căn hộ' },
		{ value: 'house', label: 'Nhà riêng' },
		{ value: 'villa', label: 'Biệt thự' },
		{ value: 'land', label: 'Đất nền' },
		{ value: 'townhouse', label: 'Nhà phố' },
		{ value: 'office', label: 'Văn phòng' }
	];

	const handleSearch = async () => {
		if (!query.trim()) {
			toast.error('Vui lòng nhập từ khóa tìm kiếm');
			return;
		}

		loading = true;
		try {
			const request: PropertySearchRequest = {
				query,
				filters: {},
				limit: 20
			};

			if (propertyType) {
				request.filters!.property_type = [propertyType];
			}
			if (location) {
				request.filters!.location = [location];
			}
			if (minPrice) {
				request.filters!.min_price = parseFloat(minPrice) * 1000000;
			}
			if (maxPrice) {
				request.filters!.max_price = parseFloat(maxPrice) * 1000000;
			}
			if (minArea) {
				request.filters!.min_area = parseFloat(minArea);
			}
			if (maxArea) {
				request.filters!.max_area = parseFloat(maxArea);
			}

			const response = await searchProperties(token, request);
			results = response.results;
			totalResults = response.total;

			if (results.length === 0) {
				toast.info('Không tìm thấy bất động sản phù hợp');
			} else {
				toast.success(`Tìm thấy ${totalResults} bất động sản`);
			}
		} catch (error: any) {
			console.error('Search error:', error);
			toast.error('Lỗi tìm kiếm: ' + error.message);
		} finally {
			loading = false;
		}
	};

	const handleClearFilters = () => {
		propertyType = '';
		location = '';
		minPrice = '';
		maxPrice = '';
		minArea = '';
		maxArea = '';
	};
</script>

<div class="property-search" role="search" aria-label="Tìm kiếm bất động sản">
	<div class="search-header">
		<h2 id="search-heading">Tìm kiếm bất động sản</h2>
		<p class="search-description">
			Sử dụng AI để tìm kiếm bất động sản phù hợp với nhu cầu của bạn
		</p>
	</div>

	<form class="search-form" on:submit|preventDefault={handleSearch} aria-labelledby="search-heading">
		<div class="search-input-group">
			<label for="property-search-input" class="sr-only">Từ khóa tìm kiếm</label>
			<input
				id="property-search-input"
				type="text"
				placeholder="Nhập từ khóa tìm kiếm... (vd: căn hộ 2 phòng ngủ quận 1)"
				bind:value={query}
				on:keypress={(e) => e.key === 'Enter' && handleSearch()}
				class="search-input"
				aria-describedby="search-description"
				aria-required="true"
			/>
			<button
				on:click={handleSearch}
				disabled={loading}
				class="search-button"
				type="submit"
				aria-label={loading ? 'Đang tìm kiếm...' : 'Bắt đầu tìm kiếm'}
			>
				{#if loading}
					<span class="spinner" aria-hidden="true"></span>
				{:else}
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
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/>
					</svg>
				{/if}
				Tìm kiếm
			</button>
		</div>

		<details class="filters-section" aria-label="Bộ lọc nâng cao">
			<summary>Bộ lọc nâng cao</summary>
			<fieldset class="filters-grid" aria-label="Bộ lọc tìm kiếm">
				<legend class="sr-only">Tiêu chí lọc bất động sản</legend>

				<div class="filter-group">
					<label for="filter-property-type">Loại hình</label>
					<select id="filter-property-type" bind:value={propertyType} aria-label="Chọn loại hình bất động sản">
						{#each propertyTypes as type}
							<option value={type.value}>{type.label}</option>
						{/each}
					</select>
				</div>

				<div class="filter-group">
					<label for="filter-location">Khu vực</label>
					<input
						id="filter-location"
						type="text"
						placeholder="vd: Quận 1, TP.HCM"
						bind:value={location}
						aria-label="Nhập khu vực tìm kiếm"
					/>
				</div>

				<div class="filter-group">
					<label for="filter-min-price">Giá tối thiểu (triệu)</label>
					<input
						id="filter-min-price"
						type="number"
						placeholder="0"
						bind:value={minPrice}
						aria-label="Giá tối thiểu tính bằng triệu đồng"
						min="0"
					/>
				</div>

				<div class="filter-group">
					<label for="filter-max-price">Giá tối đa (triệu)</label>
					<input
						id="filter-max-price"
						type="number"
						placeholder="∞"
						bind:value={maxPrice}
						aria-label="Giá tối đa tính bằng triệu đồng"
						min="0"
					/>
				</div>

				<div class="filter-group">
					<label for="filter-min-area">Diện tích tối thiểu (m²)</label>
					<input
						id="filter-min-area"
						type="number"
						placeholder="0"
						bind:value={minArea}
						aria-label="Diện tích tối thiểu tính bằng mét vuông"
						min="0"
					/>
				</div>

				<div class="filter-group">
					<label for="filter-max-area">Diện tích tối đa (m²)</label>
					<input
						id="filter-max-area"
						type="number"
						placeholder="∞"
						bind:value={maxArea}
						aria-label="Diện tích tối đa tính bằng mét vuông"
						min="0"
					/>
				</div>
			</fieldset>

			<button
				on:click={handleClearFilters}
				class="clear-filters-button"
				type="button"
				aria-label="Xóa tất cả bộ lọc"
			>
				Xóa bộ lọc
			</button>
		</details>
	</form>

	{#if loading}
		<div class="loading-state" role="status" aria-live="polite" aria-label="Đang tìm kiếm">
			<div class="spinner-large" aria-hidden="true"></div>
			<p>Đang tìm kiếm...</p>
		</div>
	{:else if results.length > 0}
		<section class="results-section" aria-labelledby="results-heading" role="region">
			<div class="results-header">
				<h3 id="results-heading">Kết quả tìm kiếm</h3>
				<span class="results-count" aria-label="Tìm thấy {totalResults} bất động sản">
					{totalResults} bất động sản
				</span>
			</div>

			<div class="results-grid" role="list" aria-label="Danh sách bất động sản">
				{#each results as property}
					<div role="listitem">
						<PropertyCard {property} onClick={onPropertySelect} />
					</div>
				{/each}
			</div>
		</section>
	{/if}
</div>

<style>
	/* OpenAI Design Standards Compliant Styles */

	.property-search {
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
		padding: var(--space-6, 24px);
	}

	.search-header {
		margin-bottom: var(--space-6, 24px);
	}

	.search-header h2 {
		font-size: var(--text-3xl, 28px);
		font-weight: var(--font-bold, 700);
		color: var(--text-primary, #111827);
		margin: 0 0 var(--space-2, 8px) 0;
	}

	.search-description {
		color: var(--text-secondary, #6b7280);
		font-size: var(--text-sm, 14px);
		margin: 0;
	}

	.search-form {
		background: var(--bg-primary, white);
		padding: var(--space-6, 24px);
		border-radius: var(--radius-md, 12px);
		box-shadow: var(--shadow-base, 0 2px 8px rgba(0, 0, 0, 0.1));
		margin-bottom: var(--space-8, 32px);
	}

	.search-input-group {
		display: flex;
		gap: var(--space-3, 12px);
		margin-bottom: var(--space-4, 16px);
	}

	.search-input {
		flex: 1;
		padding: var(--space-3, 12px) var(--space-4, 16px);
		border: 2px solid var(--border-color, #e5e7eb);
		border-radius: var(--radius-base, 8px);
		font-size: var(--text-base, 16px);
		transition: border-color var(--transition-base, 0.2s);
		color: var(--text-primary, #111827);
		background: var(--bg-primary, white);
	}

	.search-input:focus {
		outline: none;
		border-color: var(--brand-primary, #3b82f6);
	}

	/* OpenAI Compliance: Brand color ONLY on primary CTA */
	.search-button {
		display: flex;
		align-items: center;
		gap: var(--space-2, 8px);
		padding: var(--space-3, 12px) var(--space-6, 24px);
		background: var(--brand-primary, #3b82f6);
		color: var(--text-inverse, white);
		border: none;
		border-radius: var(--radius-base, 8px);
		font-size: var(--text-base, 16px);
		font-weight: var(--font-semibold, 600);
		cursor: pointer;
		transition: background var(--transition-base, 0.2s);
	}

	.search-button:hover:not(:disabled) {
		background: var(--brand-primary-hover, #2563eb);
	}

	.search-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.search-button:focus-visible {
		outline: 2px solid var(--brand-primary, #3b82f6);
		outline-offset: 2px;
	}

	.search-button svg {
		width: 20px;
		height: 20px;
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

	.filters-section {
		margin-top: var(--space-4, 16px);
	}

	.filters-section summary {
		cursor: pointer;
		font-weight: var(--font-semibold, 600);
		color: var(--brand-primary, #3b82f6);
		padding: var(--space-2, 8px) 0;
	}

	.filters-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: var(--space-4, 16px);
		margin: var(--space-4, 16px) 0;
		border: none;
		padding: 0;
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: var(--space-2, 6px);
	}

	.filter-group label {
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-medium, 500);
		color: var(--text-primary, #374151);
	}

	.filter-group input,
	.filter-group select {
		padding: var(--space-2, 8px) var(--space-3, 12px);
		border: 1px solid var(--border-color, #d1d5db);
		border-radius: var(--radius-base, 6px);
		font-size: var(--text-sm, 14px);
		color: var(--text-primary, #111827);
		background: var(--bg-primary, white);
	}

	.filter-group input:focus,
	.filter-group select:focus {
		outline: none;
		border-color: var(--brand-primary, #3b82f6);
	}

	/* OpenAI Compliance: Use system colors for secondary actions */
	.clear-filters-button {
		padding: var(--space-2, 8px) var(--space-4, 16px);
		background: var(--bg-secondary, #f3f4f6);
		color: var(--text-primary, #374151);
		border: none;
		border-radius: var(--radius-base, 6px);
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-medium, 500);
		cursor: pointer;
		transition: background var(--transition-base, 0.2s);
	}

	.clear-filters-button:hover {
		background: var(--bg-tertiary, #e5e7eb);
	}

	.clear-filters-button:focus-visible {
		outline: 2px solid var(--border-color-focus, #3b82f6);
		outline-offset: 2px;
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: var(--space-16, 64px) var(--space-6, 24px);
		gap: var(--space-4, 16px);
	}

	.spinner,
	.spinner-large {
		border: 3px solid var(--bg-secondary, #f3f4f6);
		border-top-color: var(--brand-primary, #3b82f6);
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	.spinner {
		width: 20px;
		height: 20px;
	}

	.spinner-large {
		width: 48px;
		height: 48px;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.results-section {
		margin-top: var(--space-8, 32px);
	}

	.results-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-6, 24px);
	}

	.results-header h3 {
		font-size: var(--text-2xl, 24px);
		font-weight: var(--font-bold, 700);
		color: var(--text-primary, #111827);
		margin: 0;
	}

	.results-count {
		font-size: var(--text-sm, 14px);
		color: var(--text-secondary, #6b7280);
		background: var(--bg-secondary, #f3f4f6);
		padding: var(--space-2, 6px) var(--space-3, 12px);
		border-radius: var(--radius-full, 16px);
	}

	.results-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--space-6, 24px);
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.search-form {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
		}

		.search-input,
		.filter-group input,
		.filter-group select {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
			color: var(--text-primary-dark, #f9fafb);
		}
	}
</style>
