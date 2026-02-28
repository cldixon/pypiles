<script lang="ts">
	import CenterPile from './CenterPile.svelte';
	import PlayerHand from './PlayerHand.svelte';
	import type { GameState } from '$lib/stores/gameStore';

	let { state }: { state: GameState } = $props();

	const players = $derived(
		state.setup?.players.map((p, i) => ({
			id: p.id,
			index: i,
			piles: state.playerPiles.get(p.id) || [],
			completed: state.playerCompleted.get(p.id) || [],
			score: state.playerScores.get(p.id) || 0
		})) || []
	);
</script>

<div class="game-board">
	<div class="center-top">
		<CenterPile cards={state.centerPile} />
	</div>

	<div class="players-grid">
		{#each players as player}
			<PlayerHand
				playerId={player.id}
				piles={player.piles}
				completed={player.completed}
				score={player.score}
				playerIndex={player.index}
			/>
		{/each}
	</div>
</div>

<style>
	.game-board {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.center-top {
		display: flex;
		justify-content: center;
	}

	.players-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1rem;
	}
</style>
