<script lang="ts">
	export let count: number = 1;
</script>

{#each Array(count) as _, i}
	<div class="property-card-skeleton">
		<div class="skeleton-image"></div>

		<div class="skeleton-content">
			<div class="skeleton-title"></div>
			<div class="skeleton-location"></div>

			<div class="skeleton-stats">
				<div class="skeleton-stat"></div>
				<div class="skeleton-stat"></div>
				<div class="skeleton-stat"></div>
			</div>

			<div class="skeleton-price"></div>
		</div>
	</div>
{/each}

<style>
	.property-card-skeleton {
		display: flex;
		flex-direction: column;
		background: white;
		border-radius: 12px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
		animation: pulse 1.5s ease-in-out infinite;
	}

	.skeleton-image {
		width: 100%;
		height: 200px;
		background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
	}

	.skeleton-content {
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.skeleton-title {
		height: 20px;
		background: #f3f4f6;
		border-radius: 4px;
		width: 80%;
	}

	.skeleton-location {
		height: 16px;
		background: #f3f4f6;
		border-radius: 4px;
		width: 60%;
	}

	.skeleton-stats {
		display: flex;
		gap: 16px;
		padding: 12px 0;
		border-top: 1px solid #e5e7eb;
		border-bottom: 1px solid #e5e7eb;
	}

	.skeleton-stat {
		height: 40px;
		background: #f3f4f6;
		border-radius: 4px;
		flex: 1;
	}

	.skeleton-price {
		height: 24px;
		background: #f3f4f6;
		border-radius: 4px;
		width: 50%;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.7;
		}
	}
</style>
