<script lang="ts">
	/**
	 * Property Card Skeleton Loader
	 *
	 * OpenAI Responsive Design: Better perceived performance
	 *
	 * Features:
	 * - Animated skeleton matching PropertyCard layout
	 * - Shows while properties are loading
	 * - Improves perceived performance (OpenAI "Responsive" principle)
	 * - ARIA accessible with loading state
	 */

	export let count: number = 1;
</script>

{#each Array(count) as _, i}
	<div
		class="property-card-skeleton"
		role="status"
		aria-label="Đang tải bất động sản"
		aria-busy="true"
	>
		<div class="skeleton-image"></div>

		<div class="skeleton-content">
			<div class="skeleton-title"></div>
			<div class="skeleton-title" style="width: 70%;"></div>

			<div class="skeleton-location"></div>

			<div class="skeleton-stats">
				<div class="skeleton-stat"></div>
				<div class="skeleton-stat"></div>
				<div class="skeleton-stat"></div>
			</div>

			<div class="skeleton-price"></div>
		</div>

		<span class="sr-only">Đang tải thông tin bất động sản...</span>
	</div>
{/each}

<style>
	/* OpenAI Responsive: Skeleton loaders for better perceived performance */

	.property-card-skeleton {
		display: flex;
		flex-direction: column;
		background: var(--bg-primary, white);
		border-radius: var(--radius-md, 12px);
		overflow: hidden;
		box-shadow: var(--shadow-base, 0 2px 8px rgba(0, 0, 0, 0.1));
		border: 1px solid var(--border-color, #e5e7eb);
		animation: pulse 1.5s ease-in-out infinite;
	}

	.skeleton-image {
		width: 100%;
		height: 200px;
		background: linear-gradient(
			90deg,
			var(--bg-secondary, #f3f4f6) 25%,
			var(--bg-tertiary, #e5e7eb) 50%,
			var(--bg-secondary, #f3f4f6) 75%
		);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
	}

	.skeleton-content {
		padding: var(--space-4, 16px);
		display: flex;
		flex-direction: column;
		gap: var(--space-3, 12px);
	}

	.skeleton-title {
		height: 20px;
		background: var(--bg-secondary, #f3f4f6);
		border-radius: var(--radius-sm, 4px);
		width: 80%;
	}

	.skeleton-location {
		height: 16px;
		background: var(--bg-secondary, #f3f4f6);
		border-radius: var(--radius-sm, 4px);
		width: 60%;
	}

	.skeleton-stats {
		display: flex;
		gap: var(--space-4, 16px);
		padding: var(--space-3, 12px) 0;
		border-top: 1px solid var(--border-color, #e5e7eb);
		border-bottom: 1px solid var(--border-color, #e5e7eb);
	}

	.skeleton-stat {
		height: 40px;
		background: var(--bg-secondary, #f3f4f6);
		border-radius: var(--radius-sm, 4px);
		flex: 1;
	}

	.skeleton-price {
		height: 24px;
		background: var(--bg-secondary, #f3f4f6);
		border-radius: var(--radius-sm, 4px);
		width: 50%;
	}

	/* Screen reader only */
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border-width: 0;
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

	/* Dark mode */
	@media (prefers-color-scheme: dark) {
		.property-card-skeleton {
			background: var(--bg-primary-dark, #1f2937);
			border-color: var(--border-color-dark, #374151);
		}

		.skeleton-image {
			background: linear-gradient(
				90deg,
				var(--bg-secondary-dark, #111827) 25%,
				var(--bg-tertiary-dark, #374151) 50%,
				var(--bg-secondary-dark, #111827) 75%
			);
		}

		.skeleton-title,
		.skeleton-location,
		.skeleton-stat,
		.skeleton-price {
			background: var(--bg-secondary-dark, #111827);
		}

		.skeleton-stats {
			border-color: var(--border-color-dark, #374151);
		}
	}
</style>
