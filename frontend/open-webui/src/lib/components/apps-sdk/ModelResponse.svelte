<script lang="ts">
	// Props
	export let content: string = '';
</script>

<div class="model-response">
	<p class="response-text">{content}</p>
	<slot />
</div>

<style>
	.model-response {
		display: flex;
		flex-direction: column;
		gap: 8px;
		align-items: flex-start;
		padding-bottom: 16px;
		width: 100%;
	}

	.response-text {
		margin: 0;
		flex: 1;
		font-family: var(--font-sans);
		font-size: 16px;
		line-height: 26px;
		letter-spacing: -0.4px;
		color: var(--text-primary);
		white-space: pre-wrap;
	}
</style>
