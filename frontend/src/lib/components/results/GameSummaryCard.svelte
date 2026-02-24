<script lang="ts">
	import type { GameConfig, CenterPileMetrics } from '$lib/api/types';

	let { config, totalEvents, durationMs, centerPileMetrics }: {
		config: GameConfig;
		totalEvents: number;
		durationMs: number;
		centerPileMetrics: CenterPileMetrics;
	} = $props();

	const itemsUsed = $derived(config.num_players * config.num_piles_per_player + 1);
	const totalCards = $derived(itemsUsed * config.pile_size);
</script>

<div class="summary-card">
	<h3>Game Summary</h3>
	<div class="stats">
		<div class="stat">
			<span class="label">Players</span>
			<span class="value">{config.num_players}</span>
		</div>
		<div class="stat">
			<span class="label">Total Cards</span>
			<span class="value">{totalCards}</span>
		</div>
		<div class="stat">
			<span class="label">Items Used</span>
			<span class="value">{itemsUsed} / 50</span>
		</div>
		<div class="stat">
			<span class="label">Duration</span>
			<span class="value">{durationMs < 1000 ? durationMs.toFixed(1) + 'ms' : (durationMs / 1000).toFixed(2) + 's'}</span>
		</div>
		<div class="stat">
			<span class="label">Total Events</span>
			<span class="value">{totalEvents}</span>
		</div>
		<div class="stat">
			<span class="label">Characters</span>
			<span class="value">{config.player_characters.join(', ')}</span>
		</div>
		<div class="stat">
			<span class="label">Center Pile Views</span>
			<span class="value">{centerPileMetrics.num_views}</span>
		</div>
		<div class="stat">
			<span class="label">Center Pile Swaps</span>
			<span class="value">{centerPileMetrics.num_swaps}</span>
		</div>
	</div>
</div>

<style>
	.summary-card {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 1.25rem;
	}

	h3 {
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
		margin-bottom: 1rem;
	}

	.stats {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.stat {
		display: flex;
		justify-content: space-between;
	}

	.label {
		color: var(--text-muted);
		font-size: 0.85rem;
	}

	.value {
		color: var(--text-primary);
		font-weight: 600;
		font-size: 0.85rem;
		font-variant-numeric: tabular-nums;
	}
</style>
