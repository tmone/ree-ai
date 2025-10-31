<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { PropertySearch, PropertyDetails } from '$lib/components/property';
	import { toast } from 'svelte-sonner';

	// Get user token from localStorage or store
	let token = '';
	let selectedProperty: any = null;
	let showDetails = false;

	onMount(() => {
		// Get token from localStorage (Open WebUI stores it there)
		const storedToken = localStorage.getItem('token');
		if (!storedToken) {
			toast.error('Vui lòng đăng nhập');
			goto('/auth');
			return;
		}
		token = storedToken;
	});

	function handlePropertySelect(property: any) {
		selectedProperty = property;
		showDetails = true;
	}

	function closeDetails() {
		showDetails = false;
		selectedProperty = null;
	}
</script>

<svelte:head>
	<title>Tìm kiếm Bất động sản - REE AI</title>
</svelte:head>

<div class="properties-page">
	<div class="page-header">
		<div class="header-content">
			<h1>Tìm kiếm Bất động sản</h1>
			<p class="header-description">
				Sử dụng AI để tìm kiếm bất động sản phù hợp với nhu cầu của bạn
			</p>
		</div>
	</div>

	<div class="page-content">
		{#if token}
			<PropertySearch {token} onPropertySelect={handlePropertySelect} />
		{:else}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Đang tải...</p>
			</div>
		{/if}
	</div>

	{#if showDetails && selectedProperty}
		<PropertyDetails property={selectedProperty} onClose={closeDetails} />
	{/if}
</div>

<style>
	.properties-page {
		min-height: 100vh;
		background: #f9fafb;
	}

	.page-header {
		background: white;
		border-bottom: 1px solid #e5e7eb;
		padding: 32px 24px;
	}

	.header-content {
		max-width: 1200px;
		margin: 0 auto;
	}

	.page-header h1 {
		font-size: 32px;
		font-weight: 700;
		color: #111827;
		margin: 0 0 8px 0;
	}

	.header-description {
		font-size: 16px;
		color: #6b7280;
		margin: 0;
	}

	.page-content {
		max-width: 1200px;
		margin: 0 auto;
		padding: 24px;
	}

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 64px 24px;
		gap: 16px;
	}

	.spinner {
		border: 4px solid #f3f4f6;
		border-top-color: #3b82f6;
		border-radius: 50%;
		width: 48px;
		height: 48px;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 768px) {
		.page-header {
			padding: 24px 16px;
		}

		.page-header h1 {
			font-size: 24px;
		}

		.page-content {
			padding: 16px;
		}
	}
</style>
