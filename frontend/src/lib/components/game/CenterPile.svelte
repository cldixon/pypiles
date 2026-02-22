<script lang="ts">
	import Card from './Card.svelte';

	let { cards }: { cards: string[] } = $props();
</script>

<div class="center-pile">
	<h3>Center Pile</h3>
	<div class="cards">
		{#each cards as cardId (cardId)}
			<div class="card-slot">
				<Card {cardId} />
			</div>
		{/each}
	</div>
</div>

<style>
	.center-pile {
		background: var(--bg-secondary);
		border: 2px solid var(--accent);
		border-radius: var(--radius-lg);
		padding: 1rem;
		text-align: center;
	}

	h3 {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--accent-light);
		margin-bottom: 0.75rem;
	}

	.cards {
		display: flex;
		gap: 0.5rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.card-slot {
		transition: transform 0.3s;
	}
</style>
