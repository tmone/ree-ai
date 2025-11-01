<script lang="ts">
	/**
	 * Smart Suggestions Component
	 *
	 * OpenAI Intelligent + Proactive Design
	 *
	 * Features:
	 * - Context-aware suggestions based on user behavior
	 * - OpenAI compliant (no unsolicited promotions)
	 * - Dismissible suggestions
	 * - ARIA accessible with role="status"
	 *
	 * IMPORTANT: Only shows contextual nudges tied to user intent
	 * (OpenAI rule: no unsolicited promotions or re-engagement campaigns)
	 */

	import { onMount } from 'svelte';

	export let suggestion: string | null = null;
	export let onDismiss: (() => void) | undefined = undefined;
	export let onAccept: (() => void) | undefined = undefined;

	let isDismissed = false;

	// Auto-dismiss after showing once per session
	function handleDismiss() {
		isDismissed = true;
		if (onDismiss) {
			onDismiss();
		}

		// Store dismissal in session storage to not show again
		sessionStorage.setItem('suggestion_dismissed', 'true');
	}

	function handleAccept() {
		if (onAccept) {
			onAccept();
		}
		handleDismiss();
	}

	onMount(() => {
		// Check if user already dismissed in this session
		const wasDismissed = sessionStorage.getItem('suggestion_dismissed');
		if (wasDismissed === 'true') {
			isDismissed = true;
		}
	});

	$: showSuggestion = suggestion && !isDismissed;
</script>

{#if showSuggestion}
	<div
		class="smart-suggestion"
		role="status"
		aria-live="polite"
		aria-label="Gợi ý thông minh"
	>
		<div class="suggestion-icon" aria-hidden="true">
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
					d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
				/>
			</svg>
		</div>

		<div class="suggestion-content">
			<p class="suggestion-text">{suggestion}</p>

			<div class="suggestion-actions">
				<button
					class="accept-button"
					on:click={handleAccept}
					aria-label="Chấp nhận gợi ý"
				>
					Xem ngay
				</button>

				<button
					class="dismiss-button"
					on:click={handleDismiss}
					aria-label="Bỏ qua gợi ý"
				>
					Bỏ qua
				</button>
			</div>
		</div>

		<button
			class="close-button"
			on:click={handleDismiss}
			aria-label="Đóng gợi ý"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
				aria-hidden="true"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>
	</div>
{/if}

<style>
	/* OpenAI Design Standards Compliant */

	.smart-suggestion {
		display: flex;
		align-items: flex-start;
		gap: var(--space-3, 12px);
		padding: var(--space-4, 16px);
		background: var(--color-info-bg, #dbeafe);
		border-left: 4px solid var(--color-info, #2563eb);
		border-radius: var(--radius-base, 6px);
		margin: var(--space-4, 16px) 0;
		position: relative;
		animation: slideIn 0.3s ease-out;
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.suggestion-icon {
		flex-shrink: 0;
		width: 24px;
		height: 24px;
		color: var(--color-info, #2563eb);
	}

	.suggestion-icon svg {
		width: 100%;
		height: 100%;
	}

	.suggestion-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: var(--space-3, 12px);
	}

	.suggestion-text {
		margin: 0;
		font-size: var(--text-sm, 14px);
		line-height: var(--leading-normal, 1.5);
		color: var(--text-primary, #111827);
	}

	.suggestion-actions {
		display: flex;
		gap: var(--space-2, 8px);
	}

	/* OpenAI Compliance: Brand color ONLY on primary CTA */
	.accept-button {
		padding: var(--space-2, 8px) var(--space-3, 12px);
		background: var(--brand-primary, #3b82f6);
		color: var(--text-inverse, white);
		border: none;
		border-radius: var(--radius-base, 6px);
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-semibold, 600);
		cursor: pointer;
		transition: background var(--transition-base, 0.2s);
	}

	.accept-button:hover {
		background: var(--brand-primary-hover, #2563eb);
	}

	.accept-button:focus-visible {
		outline: 2px solid var(--brand-primary, #3b82f6);
		outline-offset: 2px;
	}

	/* OpenAI Compliance: System colors for secondary actions */
	.dismiss-button {
		padding: var(--space-2, 8px) var(--space-3, 12px);
		background: transparent;
		color: var(--text-secondary, #6b7280);
		border: 1px solid var(--border-color, #e5e7eb);
		border-radius: var(--radius-base, 6px);
		font-size: var(--text-sm, 14px);
		font-weight: var(--font-medium, 500);
		cursor: pointer;
		transition: all var(--transition-base, 0.2s);
	}

	.dismiss-button:hover {
		background: var(--bg-secondary, #f3f4f6);
		border-color: var(--border-color-hover, #d1d5db);
	}

	.dismiss-button:focus-visible {
		outline: 2px solid var(--border-color-focus, #3b82f6);
		outline-offset: 2px;
	}

	.close-button {
		position: absolute;
		top: var(--space-2, 8px);
		right: var(--space-2, 8px);
		display: flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		padding: 0;
		background: transparent;
		border: none;
		color: var(--text-tertiary, #9ca3af);
		cursor: pointer;
		transition: color var(--transition-base, 0.2s);
	}

	.close-button:hover {
		color: var(--text-secondary, #6b7280);
	}

	.close-button svg {
		width: 16px;
		height: 16px;
	}

	/* Dark mode */
	@media (prefers-color-scheme: dark) {
		.smart-suggestion {
			background: rgba(37, 99, 235, 0.1);
			border-left-color: var(--color-info, #2563eb);
		}
	}

	/* Mobile responsive */
	@media (max-width: 640px) {
		.suggestion-actions {
			flex-direction: column;
		}

		.accept-button,
		.dismiss-button {
			width: 100%;
		}
	}
</style>
