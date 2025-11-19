<script lang="ts">
	// Props
	export let content: string = '';
	export let type: 'user' | 'assistant' = 'user';
	export let maxWidth: string = '456px';
</script>

<div class="conversation-message {type}">
	<div class="bubble" style="max-width: {maxWidth}">
		<p class="message-text">{content}</p>
		<slot />
	</div>
</div>

<style>
	.conversation-message {
		display: flex;
		flex-direction: column;
		gap: 6px;
		width: 100%;
	}

	.conversation-message.user {
		align-items: flex-end;
	}

	.conversation-message.assistant {
		align-items: flex-start;
	}

	.bubble {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		padding: 10px 20px;
		border-radius: 24px;
	}

	.conversation-message.user .bubble {
		background: var(--bg-tertiary);
	}

	.conversation-message.assistant .bubble {
		background: transparent;
		padding: 10px 0;
	}

	.message-text {
		margin: 0;
		font-family: var(--font-sans);
		font-size: 16px;
		line-height: 24px;
		letter-spacing: -0.32px;
		color: var(--text-primary);
		white-space: pre-wrap;
		width: 100%;
	}
</style>
