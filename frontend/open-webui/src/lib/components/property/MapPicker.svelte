<script lang="ts">
	/**
	 * MapPicker Component - Core Map with Draggable Marker
	 *
	 * Following OpenAI Apps SDK Design Guidelines:
	 * - Single-purpose focus: Select location on map
	 * - Clear visual hierarchy
	 * - Consistent with system design
	 */
	import { onMount, onDestroy, createEventDispatcher } from 'svelte';
	import L from 'leaflet';
	import 'leaflet/dist/leaflet.css';

	export let latitude: number = 10.7769; // Default: Ho Chi Minh City
	export let longitude: number = 106.7009;
	export let zoom: number = 15;
	export let readonly: boolean = false;
	export let height: string = '100%';

	const dispatch = createEventDispatcher();

	let mapContainer: HTMLDivElement;
	let map: L.Map | null = null;
	let marker: L.Marker | null = null;

	// Fix Leaflet default icon issue
	const defaultIcon = L.icon({
		iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
		iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
		shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
		iconSize: [25, 41],
		iconAnchor: [12, 41],
		popupAnchor: [1, -34],
		shadowSize: [41, 41]
	});

	onMount(() => {
		if (!mapContainer) return;

		// Initialize map
		map = L.map(mapContainer, {
			center: [latitude, longitude],
			zoom: zoom,
			zoomControl: true,
			attributionControl: false
		});

		// Add tile layer (OpenStreetMap)
		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			maxZoom: 19
		}).addTo(map);

		// Add draggable marker
		marker = L.marker([latitude, longitude], {
			icon: defaultIcon,
			draggable: !readonly
		}).addTo(map);

		// Handle marker drag
		if (!readonly) {
			marker.on('dragend', () => {
				if (marker) {
					const pos = marker.getLatLng();
					latitude = pos.lat;
					longitude = pos.lng;
					dispatch('locationchange', { lat: pos.lat, lng: pos.lng });
				}
			});

			// Handle map click
			map.on('click', (e: L.LeafletMouseEvent) => {
				if (marker && map) {
					marker.setLatLng(e.latlng);
					latitude = e.latlng.lat;
					longitude = e.latlng.lng;
					dispatch('locationchange', { lat: e.latlng.lat, lng: e.latlng.lng });
				}
			});
		}

		// Add attribution separately
		L.control.attribution({
			prefix: false,
			position: 'bottomright'
		}).addAttribution('© OpenStreetMap').addTo(map);
	});

	onDestroy(() => {
		if (map) {
			map.remove();
			map = null;
		}
	});

	// Update marker position when props change
	$: if (marker && map) {
		marker.setLatLng([latitude, longitude]);
		map.setView([latitude, longitude], zoom);
	}

	export function setLocation(lat: number, lng: number) {
		if (marker && map) {
			latitude = lat;
			longitude = lng;
			marker.setLatLng([lat, lng]);
			map.setView([lat, lng], zoom);
		}
	}
</script>

<div class="map-picker-container" style="height: {height}">
	<div bind:this={mapContainer} class="map-view"></div>

	{#if !readonly}
		<div class="map-instructions">
			<span class="instruction-text">
				Click hoặc kéo marker để chọn vị trí
			</span>
		</div>
	{/if}
</div>

<style>
	.map-picker-container {
		position: relative;
		width: 100%;
		border-radius: 8px;
		overflow: hidden;
		background: #f3f4f6;
	}

	.map-view {
		width: 100%;
		height: 100%;
	}

	.map-instructions {
		position: absolute;
		bottom: 12px;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(0, 0, 0, 0.75);
		color: white;
		padding: 8px 16px;
		border-radius: 20px;
		font-size: 12px;
		pointer-events: none;
		z-index: 1000;
	}

	.instruction-text {
		white-space: nowrap;
	}

	/* Override Leaflet styles for better integration */
	:global(.leaflet-control-zoom) {
		border: none !important;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
	}

	:global(.leaflet-control-zoom a) {
		background: white !important;
		color: #374151 !important;
	}

	:global(.leaflet-control-zoom a:hover) {
		background: #f3f4f6 !important;
	}
</style>
