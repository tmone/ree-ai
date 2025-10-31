<script lang="ts">
	export let title: string = 'Không có kết quả';
	export let description: string = 'Không tìm thấy bất động sản nào phù hợp với tìm kiếm của bạn';
	export let actionText: string = '';
	export let onAction: (() => void) | undefined = undefined;
	export let icon: 'search' | 'empty' | 'error' = 'search';
</script>

<div class="empty-state">
	<div class="empty-icon">
		{#if icon === 'search'}
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
		{:else if icon === 'empty'}
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
					d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
				/>
			</svg>
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
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		{/if}
	</div>

	<h3 class="empty-title">{title}</h3>
	<p class="empty-description">{description}</p>

	{#if actionText && onAction}
		<button class="empty-action" on:click={onAction}>
			{actionText}
		</button>
	{/if}
</div>

<style>
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 64px 24px;
		text-align: center;
		background: white;
		border-radius: 12px;
		border: 1px solid #e5e7eb;
	}

	.empty-icon {
		width: 80px;
		height: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #f3f4f6;
		border-radius: 50%;
		color: #9ca3af;
		margin-bottom: 24px;
	}

	.empty-icon svg {
		width: 48px;
		height: 48px;
	}

	.empty-title {
		font-size: 24px;
		font-weight: 700;
		color: #111827;
		margin: 0 0 12px 0;
	}

	.empty-description {
		font-size: 16px;
		color: #6b7280;
		margin: 0 0 24px 0;
		max-width: 400px;
	}

	.empty-action {
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

	.empty-action:hover {
		background: #2563eb;
	}

	@media (max-width: 768px) {
		.empty-state {
			padding: 48px 16px;
		}

		.empty-title {
			font-size: 20px;
		}

		.empty-description {
			font-size: 14px;
		}
	}
</style>
