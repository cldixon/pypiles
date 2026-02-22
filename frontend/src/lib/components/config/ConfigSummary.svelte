<script lang="ts">
	let {
		numPlayers,
		pileSize,
		numPilesPerPlayer,
		itemsRequired,
		totalCards,
		cardsPerPlayer,
		isValid
	}: {
		numPlayers: number;
		pileSize: number;
		numPilesPerPlayer: number;
		itemsRequired: number;
		totalCards: number;
		cardsPerPlayer: number;
		isValid: boolean;
	} = $props();
</script>

<div class="summary">
	<h3>Game Summary</h3>

	<div class="stats">
		<div class="stat">
			<span class="stat-label">Players</span>
			<span class="stat-value">{numPlayers}</span>
		</div>
		<div class="stat">
			<span class="stat-label">Cards per Player</span>
			<span class="stat-value">{cardsPerPlayer}</span>
		</div>
		<div class="stat">
			<span class="stat-label">Center Pile</span>
			<span class="stat-value">{pileSize} cards</span>
		</div>
		<div class="stat">
			<span class="stat-label">Clothing Items</span>
			<span class="stat-value">{itemsRequired} / 50</span>
		</div>
		<div class="stat">
			<span class="stat-label">Total Cards</span>
			<span class="stat-value">{totalCards}</span>
		</div>
		<div class="stat">
			<span class="stat-label">Piles to Complete</span>
			<span class="stat-value">{numPilesPerPlayer} per player</span>
		</div>
	</div>

	{#if !isValid}
		<div class="warning">
			Too many items required ({itemsRequired}). Maximum is 50.
			Reduce players or piles per player.
		</div>
	{/if}

	<div class="how-it-works">
		<h4>How It Works</h4>
		<p>
			Each player gets {numPilesPerPlayer} piles of {pileSize} cards. Cards are clothing
			items in various colors. Players concurrently race to swap cards with the center
			pile, trying to make each pile contain {pileSize} cards of the same item.
			First to complete all piles wins.
		</p>
	</div>
</div>

<style>
	.summary {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 1.5rem;
	}

	h3 {
		font-size: 1rem;
		margin-bottom: 1rem;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 600;
	}

	.stats {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-bottom: 1.25rem;
	}

	.stat {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.stat-label {
		font-size: 0.85rem;
		color: var(--text-muted);
	}

	.stat-value {
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.warning {
		background: rgba(253, 203, 110, 0.15);
		color: var(--warning);
		padding: 0.75rem;
		border-radius: var(--radius);
		font-size: 0.8rem;
		margin-bottom: 1rem;
	}

	.how-it-works {
		border-top: 1px solid var(--border);
		padding-top: 1rem;
	}

	h4 {
		font-size: 0.8rem;
		color: var(--text-muted);
		margin-bottom: 0.5rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.how-it-works p {
		font-size: 0.8rem;
		color: var(--text-secondary);
		line-height: 1.5;
	}
</style>
