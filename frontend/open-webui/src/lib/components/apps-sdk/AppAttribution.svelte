<script lang="ts">
	// Props
	export let appName: string = '';
	export let appIcon: string = '';
</script>

<div class="app-attribution">
	<div class="content">
		{#if appIcon}
			<div class="app-icon">
				<img src={appIcon} alt={appName} />
			</div>
		{/if}
		<p class="app-name">{appName}</p>
	</div>
</div>

<style>
	.app-attribution {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		padding-bottom: 12px;
		width: 100%;
	}

	.content {
		display: flex;
		align-items: center;
		gap: 10px;
		height: 26px;
		width: 100%;
	}

	.app-icon {
		width: 24px;
		height: 24px;
		border-radius: 6px;
		overflow: hidden;
		flex-shrink: 0;
	}

	.app-icon img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.app-name {
		margin: 0;
		flex: 1;
		font-family: var(--font-sans);
		font-size: 17px;
		line-height: 23px;
		letter-spacing: -0.43px;
		color: var(--text-secondary);
	}
</style>
