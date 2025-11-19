<script lang="ts">
	/**
	 * LocationPickerCard - Inline Card Component
	 *
	 * OpenAI Apps SDK Design Guidelines:
	 * - Inline cards: "Lightweight, single-purpose widgets"
	 * - Primary actions: Limited to two per card maximum
	 * - Single-purpose focus: Select location action
	 * - Clear visual hierarchy: headline, supporting text, CTA
	 */
	import { createEventDispatcher } from 'svelte';
	import MapPicker from './MapPicker.svelte';

	export let propertyId: string = '';
	export let address: string = '';
	export let initialLat: number = 10.7769;
	export let initialLng: number = 106.7009;
	export let isExpanded: boolean = false;

	const dispatch = createEventDispatcher();

	let selectedLat = initialLat;
	let selectedLng = initialLng;
	let showPreview = false;

	function handleLocationChange(event: CustomEvent<{ lat: number; lng: number }>) {
		selectedLat = event.detail.lat;
		selectedLng = event.detail.lng;
	}

	function handleExpand() {
		dispatch('expand', { propertyId, lat: selectedLat, lng: selectedLng });
	}

	function handleConfirm() {
		dispatch('confirm', {
			propertyId,
			latitude: selectedLat,
			longitude: selectedLng
		});
	}

	function handleSkip() {
		dispatch('skip', { propertyId });
	}
</script>

<div class="location-picker-card">
	<!-- Header -->
	<div class="card-header">
		<div class="header-icon">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="20"
				height="20"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
				<circle cx="12" cy="10" r="3" />
			</svg>
		</div>
		<div class="header-content">
			<h4 class="card-title">Chọn vị trí trên bản đồ</h4>
			<p class="card-subtitle">
				{#if address}
					{address}
				{:else}
					Giúp người mua dễ dàng tìm đến
				{/if}
			</p>
		</div>
	</div>

	<!-- Map Preview (Inline) -->
	{#if showPreview && !isExpanded}
		<div class="map-preview">
			<MapPicker
				latitude={selectedLat}
				longitude={selectedLng}
				height="200px"
				on:locationchange={handleLocationChange}
			/>
		</div>
	{/if}

	<!-- Coordinates Display -->
	{#if selectedLat !== initialLat || selectedLng !== initialLng}
		<div class="coordinates-display">
			<span class="coord-label">Tọa độ đã chọn:</span>
			<span class="coord-value">{selectedLat.toFixed(6)}, {selectedLng.toFixed(6)}</span>
		</div>
	{/if}

	<!-- Actions - Maximum 2 primary actions per OpenAI guidelines -->
	<div class="card-actions">
		{#if !showPreview}
			<button class="btn-primary" on:click={() => (showPreview = true)}>
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
				Chọn vị trí
			</button>
			<button class="btn-secondary" on:click={handleSkip}> Bỏ qua </button>
		{:else}
			<button class="btn-primary" on:click={handleConfirm}>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="16"
					height="16"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<polyline points="20 6 9 17 4 12" />
				</svg>
				Xác nhận
			</button>
			<button class="btn-expand" on:click={handleExpand}> Mở rộng </button>
		{/if}
	</div>
</div>

<style>
	.location-picker-card {
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 12px;
		overflow: hidden;
		max-width: 400px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.card-header {
		display: flex;
		align-items: flex-start;
		gap: 12px;
		padding: 16px;
		border-bottom: 1px solid #f3f4f6;
	}

	.header-icon {
		flex-shrink: 0;
		width: 40px;
		height: 40px;
		background: #eff6ff;
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #3b82f6;
	}

	.header-content {
		flex: 1;
		min-width: 0;
	}

	.card-title {
		margin: 0 0 4px 0;
		font-size: 15px;
		font-weight: 600;
		color: #111827;
	}

	.card-subtitle {
		margin: 0;
		font-size: 13px;
		color: #6b7280;
		line-height: 1.4;
	}

	.map-preview {
		height: 200px;
		border-bottom: 1px solid #f3f4f6;
	}

	.coordinates-display {
		padding: 12px 16px;
		background: #f9fafb;
		border-bottom: 1px solid #f3f4f6;
		font-size: 12px;
	}

	.coord-label {
		color: #6b7280;
		margin-right: 8px;
	}

	.coord-value {
		font-family: 'SF Mono', 'Menlo', monospace;
		color: #111827;
		font-weight: 500;
	}

	.card-actions {
		display: flex;
		gap: 8px;
		padding: 12px 16px;
	}

	.btn-primary,
	.btn-secondary,
	.btn-expand {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		padding: 10px 16px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.15s ease;
		border: none;
	}

	.btn-primary {
		background: #3b82f6;
		color: white;
	}

	.btn-primary:hover {
		background: #2563eb;
	}

	.btn-secondary {
		background: #f3f4f6;
		color: #374151;
	}

	.btn-secondary:hover {
		background: #e5e7eb;
	}

	.btn-expand {
		background: transparent;
		color: #6b7280;
		border: 1px solid #e5e7eb;
	}

	.btn-expand:hover {
		background: #f9fafb;
		color: #374151;
	}

	/* Dark mode support */
	:global(.dark) .location-picker-card {
		background: #1f2937;
		border-color: #374151;
	}

	:global(.dark) .card-header {
		border-color: #374151;
	}

	:global(.dark) .card-title {
		color: #f9fafb;
	}

	:global(.dark) .card-subtitle {
		color: #9ca3af;
	}

	:global(.dark) .header-icon {
		background: #1e3a5f;
	}

	:global(.dark) .coordinates-display {
		background: #111827;
		border-color: #374151;
	}

	:global(.dark) .coord-value {
		color: #f9fafb;
	}

	:global(.dark) .btn-secondary {
		background: #374151;
		color: #f3f4f6;
	}

	:global(.dark) .btn-expand {
		border-color: #4b5563;
		color: #9ca3af;
	}
</style>
