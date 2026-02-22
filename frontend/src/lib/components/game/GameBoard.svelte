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

<div class="game-board" class:two-players={players.length === 2} class:many-players={players.length > 2}>
	{#if players.length === 2}
		<!-- 2-player layout: player - center - player -->
		<div class="player-panel left">
			<PlayerHand
				playerId={players[0].id}
				piles={players[0].piles}
				completed={players[0].completed}
				score={players[0].score}
				playerIndex={0}
			/>
		</div>

		<div class="center-panel">
			<CenterPile cards={state.centerPile} />
		</div>

		<div class="player-panel right">
			<PlayerHand
				playerId={players[1].id}
				piles={players[1].piles}
				completed={players[1].completed}
				score={players[1].score}
				playerIndex={1}
			/>
		</div>
	{:else}
		<!-- 3+ player layout: center on top, players in grid below -->
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
	{/if}
</div>

<style>
	.game-board.two-players {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: 1.5rem;
		align-items: start;
	}

	.game-board.many-players {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.center-panel {
		display: flex;
		align-items: center;
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

	@media (max-width: 800px) {
		.game-board.two-players {
			grid-template-columns: 1fr;
		}

		.center-panel {
			justify-content: center;
		}
	}
</style>
