<script lang="ts">
	/**
	 * PropertyMessage Component
	 * Displays property cards within chat messages
	 * Usage: When AI response contains property data
	 */
	import { PropertyCard } from '$lib/components/property';
	import type { Property } from '$lib/apis/ree-ai';

	export let properties: Property[] = [];
	export let onPropertyClick: ((property: Property) => void) | undefined = undefined;

	// Parse properties from message if needed
	$: validProperties = properties.filter((p) => p && p.id && p.title);
</script>

{#if validProperties.length > 0}
	<div class="property-message">
		<div class="property-message-header">
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
					d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
				/>
			</svg>
			<span>Bất động sản được tìm thấy</span>
			<span class="property-count">{validProperties.length}</span>
		</div>

		<div class="property-grid">
			{#each validProperties as property}
				<PropertyCard {property} onClick={onPropertyClick} />
			{/each}
		</div>

		{#if validProperties.length > 3}
			<div class="property-footer">
				<p>Hiển thị {Math.min(3, validProperties.length)} / {validProperties.length} kết quả</p>
			</div>
		{/if}
	</div>
{/if}

<style>
	.property-message {
		margin: 16px 0;
		background: #f9fafb;
		border-radius: 12px;
		padding: 16px;
		border: 1px solid #e5e7eb;
	}

	.property-message-header {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 16px;
		color: #374151;
		font-weight: 600;
		font-size: 14px;
	}

	.property-message-header svg {
		width: 20px;
		height: 20px;
		color: #3b82f6;
	}

	.property-count {
		margin-left: auto;
		background: #3b82f6;
		color: white;
		padding: 2px 8px;
		border-radius: 12px;
		font-size: 12px;
		font-weight: 700;
	}

	.property-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 16px;
		max-height: 600px;
		overflow-y: auto;
	}

	/* Show max 3 properties in chat */
	.property-grid :global(.property-card:nth-child(n + 4)) {
		display: none;
	}

	.property-footer {
		margin-top: 16px;
		padding-top: 16px;
		border-top: 1px solid #e5e7eb;
		text-align: center;
	}

	.property-footer p {
		margin: 0;
		font-size: 14px;
		color: #6b7280;
	}

	@media (max-width: 768px) {
		.property-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
