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

<div class="property-search">
	<div class="search-header">
		<h2>Tìm kiếm bất động sản</h2>
		<p class="search-description">
			Sử dụng AI để tìm kiếm bất động sản phù hợp với nhu cầu của bạn
		</p>
	</div>

	<div class="search-form">
		<div class="search-input-group">
			<input
				type="text"
				placeholder="Nhập từ khóa tìm kiếm... (vd: căn hộ 2 phòng ngủ quận 1)"
				bind:value={query}
				on:keypress={(e) => e.key === 'Enter' && handleSearch()}
				class="search-input"
			/>
			<button on:click={handleSearch} disabled={loading} class="search-button">
				{#if loading}
					<span class="spinner"></span>
				{:else}
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
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

		<details class="filters-section">
			<summary>Bộ lọc nâng cao</summary>
			<div class="filters-grid">
				<div class="filter-group">
					<label>Loại hình</label>
					<select bind:value={propertyType}>
						{#each propertyTypes as type}
							<option value={type.value}>{type.label}</option>
						{/each}
					</select>
				</div>

				<div class="filter-group">
					<label>Khu vực</label>
					<input
						type="text"
						placeholder="vd: Quận 1, TP.HCM"
						bind:value={location}
					/>
				</div>

				<div class="filter-group">
					<label>Giá tối thiểu (triệu)</label>
					<input type="number" placeholder="0" bind:value={minPrice} />
				</div>

				<div class="filter-group">
					<label>Giá tối đa (triệu)</label>
					<input type="number" placeholder="∞" bind:value={maxPrice} />
				</div>

				<div class="filter-group">
					<label>Diện tích tối thiểu (m²)</label>
					<input type="number" placeholder="0" bind:value={minArea} />
				</div>

				<div class="filter-group">
					<label>Diện tích tối đa (m²)</label>
					<input type="number" placeholder="∞" bind:value={maxArea} />
				</div>
			</div>

			<button on:click={handleClearFilters} class="clear-filters-button">
				Xóa bộ lọc
			</button>
		</details>
	</div>

	{#if loading}
		<div class="loading-state">
			<div class="spinner-large"></div>
			<p>Đang tìm kiếm...</p>
		</div>
	{:else if results.length > 0}
		<div class="results-section">
			<div class="results-header">
				<h3>Kết quả tìm kiếm</h3>
				<span class="results-count">{totalResults} bất động sản</span>
			</div>

			<div class="results-grid">
				{#each results as property}
					<PropertyCard {property} onClick={onPropertySelect} />
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.property-search {
		width: 100%;
		max-width: 1200px;
		margin: 0 auto;
		padding: 24px;
	}

	.search-header {
		margin-bottom: 24px;
	}

	.search-header h2 {
		font-size: 28px;
		font-weight: 700;
		color: #111827;
		margin: 0 0 8px 0;
	}

	.search-description {
		color: #6b7280;
		font-size: 14px;
		margin: 0;
	}

	.search-form {
		background: white;
		padding: 24px;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 32px;
	}

	.search-input-group {
		display: flex;
		gap: 12px;
		margin-bottom: 16px;
	}

	.search-input {
		flex: 1;
		padding: 12px 16px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		font-size: 16px;
		transition: border-color 0.2s;
	}

	.search-input:focus {
		outline: none;
		border-color: #3b82f6;
	}

	.search-button {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 12px 24px;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 16px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.2s;
	}

	.search-button:hover:not(:disabled) {
		background: #2563eb;
	}

	.search-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.search-button svg {
		width: 20px;
		height: 20px;
	}

	.filters-section {
		margin-top: 16px;
	}

	.filters-section summary {
		cursor: pointer;
		font-weight: 600;
		color: #3b82f6;
		padding: 8px 0;
	}

	.filters-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 16px;
		margin: 16px 0;
	}

	.filter-group {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.filter-group label {
		font-size: 14px;
		font-weight: 500;
		color: #374151;
	}

	.filter-group input,
	.filter-group select {
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 14px;
	}

	.filter-group input:focus,
	.filter-group select:focus {
		outline: none;
		border-color: #3b82f6;
	}

	.clear-filters-button {
		padding: 8px 16px;
		background: #f3f4f6;
		color: #374151;
		border: none;
		border-radius: 6px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.2s;
	}

	.clear-filters-button:hover {
		background: #e5e7eb;
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 64px 24px;
		gap: 16px;
	}

	.spinner,
	.spinner-large {
		border: 3px solid #f3f4f6;
		border-top-color: #3b82f6;
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
		margin-top: 32px;
	}

	.results-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
	}

	.results-header h3 {
		font-size: 24px;
		font-weight: 700;
		color: #111827;
		margin: 0;
	}

	.results-count {
		font-size: 14px;
		color: #6b7280;
		background: #f3f4f6;
		padding: 6px 12px;
		border-radius: 16px;
	}

	.results-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 24px;
	}
</style>
