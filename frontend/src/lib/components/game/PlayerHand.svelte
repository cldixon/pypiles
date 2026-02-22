<script lang="ts">
	import Card from './Card.svelte';
	import { PLAYER_COLORS } from '$lib/utils/colors';

	let {
		playerId,
		piles,
		completed,
		score,
		playerIndex
	}: {
		playerId: string;
		piles: string[][];
		completed: string[][];
		score: number;
		playerIndex: number;
	} = $props();

	const color = $derived(PLAYER_COLORS[playerIndex] || PLAYER_COLORS[0]);
</script>

<div class="player-hand" style="--player-color: {color}">
	<div class="player-header">
		<span class="player-id">{playerId}</span>
		<span class="player-score">{score} completed</span>
	</div>

	<div class="piles">
		{#each piles as pile, i}
			<div class="pile">
				<span class="pile-label">Pile {i + 1}</span>
				<div class="pile-cards">
					{#each pile as cardId}
						<Card {cardId} compact />
					{/each}
				</div>
			</div>
		{/each}
	</div>

	{#if completed.length > 0}
		<div class="completed-section">
			<span class="completed-label">Completed</span>
			<div class="completed-piles">
				{#each completed as pile, i}
					<div class="completed-pile">
						<span class="check-mark">&#10003;</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.player-hand {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-left: 3px solid var(--player-color);
		border-radius: var(--radius-lg);
		padding: 0.75rem;
	}

	.player-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.player-id {
		font-weight: 700;
		font-size: 0.9rem;
		color: var(--player-color);
	}

	.player-score {
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.piles {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.pile {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}

	.pile-label {
		font-size: 0.6rem;
		color: var(--text-muted);
		min-width: 2.5rem;
	}

	.pile-cards {
		display: flex;
		gap: 0.25rem;
		flex: 1;
		min-width: 0;
	}

	.completed-section {
		margin-top: 0.5rem;
		padding-top: 0.5rem;
		border-top: 1px solid var(--border);
	}

	.completed-label {
		font-size: 0.65rem;
		color: var(--success);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.completed-piles {
		display: flex;
		gap: 0.25rem;
		margin-top: 0.25rem;
	}

	.completed-pile {
		width: 24px;
		height: 24px;
		background: var(--success);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.check-mark {
		color: white;
		font-size: 0.7rem;
		font-weight: 700;
	}
</style>
