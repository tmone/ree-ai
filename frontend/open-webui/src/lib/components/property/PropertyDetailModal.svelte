<script lang="ts">
	/**
	 * Property Detail Modal - OpenAI Apps SDK Inspector Pattern
	 *
	 * Shows PropertyInspector in a modal/popup overlay
	 * Design: User can close and return to property list (CTO requirement)
	 *
	 * Props:
	 * - property: Full property data
	 * - open: Boolean to control visibility
	 * - onClose: Callback when modal closes
	 */

	import PropertyInspector from '$lib/components/apps-sdk/PropertyInspector.svelte';
	import { createEventDispatcher } from 'svelte';

	export let property: any;
	export let open: boolean = false;

	const dispatch = createEventDispatcher();

	function handleClose() {
		open = false;
		dispatch('close');
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) {
			handleClose();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) {
			handleClose();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
	<!-- Modal Overlay -->
	<div
		class="modal-overlay"
		role="dialog"
		aria-modal="true"
		aria-labelledby="modal-title"
		on:click={handleBackdropClick}
		transition:fade={{ duration: 200 }}
	>
		<!-- Modal Container -->
		<div class="modal-container" transition:scale={{ duration: 200, start: 0.95 }}>
			<!-- Close Button -->
			<button
				class="close-button"
				on:click={handleClose}
				aria-label="Close property details"
				type="button"
			>
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
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
			</button>

			<!-- Property Inspector Component -->
			<div class="modal-content">
				<PropertyInspector
					id={property?.id || ''}
					title={property?.title || ''}
					address={property?.address || property?.location || ''}
					price={property?.price || ''}
					pricePerM2={property?.pricePerM2 || ''}
					area={property?.area || property?.areaDisplay || ''}
					bedrooms={property?.bedrooms || 0}
					bathrooms={property?.bathrooms || 0}
					floors={property?.floors || 0}
					direction={property?.direction || ''}
					images={property?.images || (property?.imageUrl ? [property.imageUrl] : [])}
					description={property?.description || ''}
					propertyType={property?.propertyType || ''}
					transactionType={property?.transactionType || 'sale'}
					legalStatus={property?.legalStatus || ''}
					furniture={property?.furniture || ''}
					contact={property?.contact || null}
					amenities={property?.amenities || []}
					on:close={handleClose}
				/>
			</div>
		</div>
	</div>
{/if}

<script context="module">
	import { fade, scale } from 'svelte/transition';
</script>

<style>
	/* Modal Overlay - Full screen backdrop */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 1300; /* --z-modal from design tokens */

		/* Backdrop */
		background-color: rgba(0, 0, 0, 0.5);

		/* Center content */
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 16px;

		/* Prevent scroll on body */
		overflow-y: auto;
	}

	/* Modal Container - Inspector wrapper */
	.modal-container {
		position: relative;
		width: 100%;
		max-width: 480px; /* --inspector-width from design tokens */
		max-height: 80vh; /* --inspector-max-height */

		/* OpenAI System Colors */
		background: #ffffff;
		border-radius: 12px;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

		/* Spacing */
		padding: 24px; /* --space-6 */

		/* Overflow */
		overflow-y: auto;
		overflow-x: hidden;
	}

	/* Close Button - Top right */
	.close-button {
		position: absolute;
		top: 16px;
		right: 16px;
		z-index: 10;

		/* Size */
		width: 32px;
		height: 32px;
		padding: 0;

		/* Style */
		background: rgba(0, 0, 0, 0.05);
		border: none;
		border-radius: 6px;
		cursor: pointer;

		/* Center icon */
		display: flex;
		align-items: center;
		justify-content: center;

		/* Transition */
		transition: background-color 150ms ease-in-out;
	}

	.close-button:hover {
		background: rgba(0, 0, 0, 0.1);
	}

	.close-button:focus-visible {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	.close-button svg {
		width: 20px;
		height: 20px;
		color: #0d0d0d;
	}

	/* Modal Content - PropertyInspector container */
	.modal-content {
		/* Remove default padding from PropertyInspector if needed */
		margin: 0;
	}

	/* Dark Mode */
	@media (prefers-color-scheme: dark) {
		.modal-container {
			background: #212121;
		}

		.close-button {
			background: rgba(255, 255, 255, 0.1);
		}

		.close-button:hover {
			background: rgba(255, 255, 255, 0.2);
		}

		.close-button svg {
			color: #ffffff;
		}
	}

	/* Mobile Responsive */
	@media (max-width: 768px) {
		.modal-overlay {
			padding: 0;
		}

		.modal-container {
			max-width: 100%;
			max-height: 100vh;
			border-radius: 0;
			height: 100%;
		}
	}

	/* Scrollbar styling */
	.modal-container::-webkit-scrollbar {
		width: 8px;
	}

	.modal-container::-webkit-scrollbar-track {
		background: transparent;
	}

	.modal-container::-webkit-scrollbar-thumb {
		background: #e5e7eb;
		border-radius: 4px;
	}

	.modal-container::-webkit-scrollbar-thumb:hover {
		background: #d1d5db;
	}

	@media (prefers-color-scheme: dark) {
		.modal-container::-webkit-scrollbar-thumb {
			background: #404040;
		}

		.modal-container::-webkit-scrollbar-thumb:hover {
			background: #525252;
		}
	}
</style>
