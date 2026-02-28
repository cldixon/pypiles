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
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
		max-width: 20rem;
		margin: 0 auto;
	}

	.card-slot {
		transition: transform 0.3s;
	}

	/* Fixed-size cards in center pile to prevent layout shifts */
	.card-slot :global(.card) {
		width: 9rem;
		height: 3rem;
		box-sizing: border-box;
		justify-content: center;
		align-items: center;
		text-align: center;
	}

	.card-slot :global(.item) {
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>
