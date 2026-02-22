<script lang="ts">
	import { CARD_COLORS, CARD_TEXT_COLORS } from '$lib/utils/colors';
	import { parseCard, formatItemName } from '$lib/utils/cardParser';

	let { cardId, compact = false, highlight = false }: {
		cardId: string;
		compact?: boolean;
		highlight?: boolean;
	} = $props();

	const card = $derived(parseCard(cardId));
	const bgColor = $derived(CARD_COLORS[card.color] || '#444');
	const textColor = $derived(CARD_TEXT_COLORS[card.color] || '#fff');
</script>

<div
	class="card"
	class:compact
	class:highlight
	style="background: {bgColor}; color: {textColor}"
>
	<span class="item">{formatItemName(card.item)}</span>
	{#if !compact}
		<span class="color">{card.color}</span>
	{/if}
</div>

<style>
	.card {
		padding: 0.4rem 0.6rem;
		border-radius: 6px;
		font-size: 0.7rem;
		font-weight: 600;
		display: flex;
		flex-direction: column;
		gap: 0.1rem;
		transition: transform 0.2s, box-shadow 0.2s;
		border: 1px solid rgba(255, 255, 255, 0.1);
		min-width: 0;
		overflow: hidden;
	}

	.card.compact {
		padding: 0.25rem 0.4rem;
		font-size: 0.6rem;
	}

	.card.highlight {
		box-shadow: 0 0 12px rgba(108, 92, 231, 0.6);
		transform: scale(1.05);
	}

	.item {
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.color {
		font-size: 0.6rem;
		opacity: 0.7;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
</style>
