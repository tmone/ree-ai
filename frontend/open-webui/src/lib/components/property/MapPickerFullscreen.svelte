<script lang="ts">
	/**
	 * MapPickerFullscreen - Fullscreen Map View
	 *
	 * OpenAI Apps SDK Design Guidelines:
	 * - Fullscreen views: "Immersive experiences for complex workflows"
	 * - Maps qualify for fullscreen expansion when containing "explorable map with pins"
	 * - Clear exit point with close button
	 */
	import { createEventDispatcher } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import MapPicker from './MapPicker.svelte';

	export let isOpen: boolean = false;
	export let propertyId: string = '';
	export let address: string = '';
	export let latitude: number = 10.7769;
	export let longitude: number = 106.7009;

	const dispatch = createEventDispatcher();

	let selectedLat = latitude;
	let selectedLng = longitude;
	let searchQuery = address;
	let isSearching = false;

	function handleLocationChange(event: CustomEvent<{ lat: number; lng: number }>) {
		selectedLat = event.detail.lat;
		selectedLng = event.detail.lng;
	}

	function handleConfirm() {
		dispatch('confirm', {
			propertyId,
			latitude: selectedLat,
			longitude: selectedLng
		});
		isOpen = false;
	}

	function handleClose() {
		dispatch('close');
		isOpen = false;
	}

	// Search location by address using Nominatim (OpenStreetMap)
	async function searchLocation() {
		if (!searchQuery.trim()) return;

		isSearching = true;
		try {
			const response = await fetch(
				`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`
			);
			const results = await response.json();

			if (results.length > 0) {
				selectedLat = parseFloat(results[0].lat);
				selectedLng = parseFloat(results[0].lon);
			}
		} catch (error) {
			console.error('Location search failed:', error);
		} finally {
			isSearching = false;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			handleClose();
		}
	}

	// Reset selected coordinates when opening
	$: if (isOpen) {
		selectedLat = latitude;
		selectedLng = longitude;
		searchQuery = address;
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
	<div class="fullscreen-overlay" transition:fade={{ duration: 200 }}>
		<div class="fullscreen-container" transition:fly={{ y: 50, duration: 300 }}>
			<!-- Header -->
			<div class="fullscreen-header">
				<div class="header-left">
					<button class="close-btn" on:click={handleClose}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<line x1="18" y1="6" x2="6" y2="18" />
							<line x1="6" y1="6" x2="18" y2="18" />
						</svg>
					</button>
					<h2 class="header-title">Chọn vị trí bất động sản</h2>
				</div>

				<button class="confirm-btn" on:click={handleConfirm}>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="18"
						height="18"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<polyline points="20 6 9 17 4 12" />
					</svg>
					Xác nhận
				</button>
			</div>

			<!-- Search Bar -->
			<div class="search-bar">
				<div class="search-input-wrapper">
					<svg
						class="search-icon"
						xmlns="http://www.w3.org/2000/svg"
						width="18"
						height="18"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<circle cx="11" cy="11" r="8" />
						<line x1="21" y1="21" x2="16.65" y2="16.65" />
					</svg>
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="Tìm địa chỉ..."
						on:keydown={(e) => e.key === 'Enter' && searchLocation()}
					/>
					{#if isSearching}
						<div class="search-spinner"></div>
					{/if}
				</div>
				<button class="search-btn" on:click={searchLocation} disabled={isSearching}> Tìm </button>
			</div>

			<!-- Map -->
			<div class="map-container">
				<MapPicker
					bind:latitude={selectedLat}
					bind:longitude={selectedLng}
					zoom={16}
					height="100%"
					on:locationchange={handleLocationChange}
				/>
			</div>

			<!-- Footer with coordinates -->
			<div class="fullscreen-footer">
				<div class="coordinates-info">
					<span class="coord-icon">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="16"
							height="16"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
							<circle cx="12" cy="10" r="3" />
						</svg>
					</span>
					<span class="coord-text">
						{selectedLat.toFixed(6)}, {selectedLng.toFixed(6)}
					</span>
				</div>
				<p class="footer-hint">Click hoặc kéo marker để chọn vị trí chính xác</p>
			</div>
		</div>
	</div>
{/if}

<style>
	.fullscreen-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 16px;
	}

	.fullscreen-container {
		width: 100%;
		max-width: 900px;
		height: 90vh;
		max-height: 700px;
		background: white;
		border-radius: 16px;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
	}

	.fullscreen-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16px 20px;
		border-bottom: 1px solid #e5e7eb;
		background: #f9fafb;
	}

	.header-left {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.close-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: 8px;
		border: none;
		background: transparent;
		color: #6b7280;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.close-btn:hover {
		background: #e5e7eb;
		color: #111827;
	}

	.header-title {
		margin: 0;
		font-size: 18px;
		font-weight: 600;
		color: #111827;
	}

	.confirm-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 10px 20px;
		border-radius: 8px;
		border: none;
		background: #3b82f6;
		color: white;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.confirm-btn:hover {
		background: #2563eb;
	}

	.search-bar {
		display: flex;
		gap: 8px;
		padding: 12px 20px;
		border-bottom: 1px solid #e5e7eb;
	}

	.search-input-wrapper {
		flex: 1;
		position: relative;
		display: flex;
		align-items: center;
	}

	.search-icon {
		position: absolute;
		left: 12px;
		color: #9ca3af;
		pointer-events: none;
	}

	.search-input-wrapper input {
		width: 100%;
		padding: 10px 12px 10px 40px;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-size: 14px;
		outline: none;
		transition: border-color 0.15s ease;
	}

	.search-input-wrapper input:focus {
		border-color: #3b82f6;
	}

	.search-spinner {
		position: absolute;
		right: 12px;
		width: 16px;
		height: 16px;
		border: 2px solid #e5e7eb;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.search-btn {
		padding: 10px 20px;
		border-radius: 8px;
		border: 1px solid #d1d5db;
		background: white;
		color: #374151;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.search-btn:hover:not(:disabled) {
		background: #f9fafb;
		border-color: #9ca3af;
	}

	.search-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.map-container {
		flex: 1;
		min-height: 0;
	}

	.fullscreen-footer {
		padding: 12px 20px;
		border-top: 1px solid #e5e7eb;
		background: #f9fafb;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.coordinates-info {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.coord-icon {
		color: #3b82f6;
		display: flex;
	}

	.coord-text {
		font-family: 'SF Mono', 'Menlo', monospace;
		font-size: 13px;
		color: #374151;
		font-weight: 500;
	}

	.footer-hint {
		margin: 0;
		font-size: 12px;
		color: #9ca3af;
	}

	/* Dark mode */
	:global(.dark) .fullscreen-container {
		background: #1f2937;
	}

	:global(.dark) .fullscreen-header,
	:global(.dark) .fullscreen-footer {
		background: #111827;
		border-color: #374151;
	}

	:global(.dark) .header-title {
		color: #f9fafb;
	}

	:global(.dark) .close-btn {
		color: #9ca3af;
	}

	:global(.dark) .close-btn:hover {
		background: #374151;
		color: #f9fafb;
	}

	:global(.dark) .search-bar {
		border-color: #374151;
	}

	:global(.dark) .search-input-wrapper input {
		background: #374151;
		border-color: #4b5563;
		color: #f9fafb;
	}

	:global(.dark) .search-btn {
		background: #374151;
		border-color: #4b5563;
		color: #f3f4f6;
	}

	:global(.dark) .coord-text {
		color: #f3f4f6;
	}

	/* Mobile responsive */
	@media (max-width: 640px) {
		.fullscreen-container {
			height: 100vh;
			max-height: none;
			border-radius: 0;
		}

		.fullscreen-overlay {
			padding: 0;
		}

		.fullscreen-footer {
			flex-direction: column;
			align-items: flex-start;
			gap: 8px;
		}
	}
</style>
