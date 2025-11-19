<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import ListRow from './ListRow.svelte';

	const dispatch = createEventDispatcher();

	// Props
	export let items: Array<{
		title: string;
		subtitle?: string;
		imageUrl?: string;
		actionIcon?: 'plus' | 'chevron' | 'check';
	}> = [];
	export let showActions: boolean = true;

	function handleItemAction(event: CustomEvent, index: number) {
		dispatch('itemAction', { ...event.detail, index });
	}
</script>

<div class="list-group">
	{#each items as item, index}
		<ListRow
			title={item.title}
			subtitle={item.subtitle || ''}
			imageUrl={item.imageUrl || ''}
			showAction={showActions}
			actionIcon={item.actionIcon || 'plus'}
			hasBorder={index < items.length - 1}
			on:action={(e) => handleItemAction(e, index)}
		/>
	{/each}
</div>

<style>
	.list-group {
		display: flex;
		flex-direction: column;
		align-items: stretch;
		width: 100%;
	}
</style>
