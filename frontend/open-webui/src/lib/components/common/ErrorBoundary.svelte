<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	export let fallback: any = null;

	let error: Error | null = null;
	let errorInfo: any = null;

	function handleError(event: ErrorEvent) {
		error = event.error;
		errorInfo = {
			message: event.message,
			filename: event.filename,
			lineno: event.lineno,
			colno: event.colno
		};
		console.error('Error caught by boundary:', error, errorInfo);
	}

	function reset() {
		error = null;
		errorInfo = null;
	}

	onMount(() => {
		window.addEventListener('error', handleError);
	});

	onDestroy(() => {
		window.removeEventListener('error', handleError);
	});
</script>

{#if error}
	{#if fallback}
		<svelte:component this={fallback} {error} {errorInfo} {reset} />
	{:else}
		<div class="error-boundary">
			<div class="error-content">
				<div class="error-icon">
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
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
				</div>

				<h2 class="error-title">Đã xảy ra lỗi</h2>

				<p class="error-message">
					{error?.message || 'Một lỗi không xác định đã xảy ra'}
				</p>

				{#if process.env.NODE_ENV === 'development' && errorInfo}
					<details class="error-details">
						<summary>Chi tiết lỗi (Development only)</summary>
						<pre>{JSON.stringify(errorInfo, null, 2)}</pre>
						{#if error.stack}
							<pre class="error-stack">{error.stack}</pre>
						{/if}
					</details>
				{/if}

				<div class="error-actions">
					<button class="retry-button" on:click={reset}> Thử lại </button>
					<button class="home-button" on:click={() => (window.location.href = '/')}>
						Về trang chủ
					</button>
				</div>
			</div>
		</div>
	{/if}
{:else}
	<slot />
{/if}

<style>
	.error-boundary {
		min-height: 400px;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24px;
		background: #fef2f2;
	}

	.error-content {
		max-width: 600px;
		background: white;
		border-radius: 12px;
		padding: 48px;
		text-align: center;
		border: 2px solid #fca5a5;
	}

	.error-icon {
		width: 80px;
		height: 80px;
		margin: 0 auto 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #fee2e2;
		border-radius: 50%;
		color: #dc2626;
	}

	.error-icon svg {
		width: 48px;
		height: 48px;
	}

	.error-title {
		font-size: 28px;
		font-weight: 700;
		color: #991b1b;
		margin: 0 0 16px 0;
	}

	.error-message {
		font-size: 16px;
		color: #6b7280;
		margin: 0 0 24px 0;
		line-height: 1.5;
	}

	.error-details {
		text-align: left;
		margin: 24px 0;
		padding: 16px;
		background: #f9fafb;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
	}

	.error-details summary {
		cursor: pointer;
		font-weight: 600;
		color: #374151;
		margin-bottom: 12px;
	}

	.error-details pre {
		font-size: 12px;
		overflow-x: auto;
		padding: 12px;
		background: #1f2937;
		color: #f3f4f6;
		border-radius: 4px;
		margin: 8px 0;
	}

	.error-stack {
		max-height: 200px;
		overflow-y: auto;
	}

	.error-actions {
		display: flex;
		gap: 12px;
		justify-content: center;
	}

	.retry-button,
	.home-button {
		padding: 12px 24px;
		border: none;
		border-radius: 8px;
		font-size: 16px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}

	.retry-button {
		background: #3b82f6;
		color: white;
	}

	.retry-button:hover {
		background: #2563eb;
	}

	.home-button {
		background: #f3f4f6;
		color: #374151;
	}

	.home-button:hover {
		background: #e5e7eb;
	}

	@media (max-width: 768px) {
		.error-content {
			padding: 32px 24px;
		}

		.error-title {
			font-size: 24px;
		}

		.error-actions {
			flex-direction: column;
		}

		.retry-button,
		.home-button {
			width: 100%;
		}
	}
</style>
