<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import { GameWebSocket } from '$lib/api/websocket';
	import { gameStore, type GameState } from '$lib/stores/gameStore';
	import GameBoard from '$lib/components/game/GameBoard.svelte';
	import EventLog from '$lib/components/game/EventLog.svelte';
	import PlaybackControls from '$lib/components/game/PlaybackControls.svelte';

	const gameId = $derived(page.params.id ?? '');

	let ws: GameWebSocket | null = $state(null);
	let paused = $state(false);
	let speed = $state(1.0);
	let gameState: GameState = $state({
		phase: 'connecting',
		setup: null,
		events: [],
		completion: null,
		progress: 0,
		error: null,
		centerPile: [],
		playerPiles: new Map(),
		playerCompleted: new Map(),
		playerScores: new Map(),
		recentSwaps: []
	});

	let unsubscribe: (() => void) | null = null;

	onMount(() => {
		gameStore.reset();
		unsubscribe = gameStore.subscribe((v) => { gameState = v; });
		ws = new GameWebSocket(gameId);
		ws.connect();
	});

	onDestroy(() => {
		ws?.disconnect();
		unsubscribe?.();
	});

	function handlePause() {
		paused = true;
		ws?.sendControl('pause');
	}

	function handleResume() {
		paused = false;
		ws?.sendControl('resume');
	}

	function handleSetSpeed(newSpeed: number) {
		speed = newSpeed;
		ws?.sendControl('set_speed', newSpeed);
	}

	function handleSkipToEnd() {
		ws?.sendControl('skip_to_end');
	}

	function viewResults() {
		goto(`/results/${gameId}`);
	}
</script>

<svelte:head>
	<title>PyPiles - Game {gameId.slice(0, 8)}</title>
</svelte:head>

{#if gameState.phase === 'connecting'}
	<div class="status-page">
		<div class="spinner"></div>
		<p>Connecting to game...</p>
	</div>
{:else if gameState.phase === 'error'}
	<div class="status-page">
		<h2>Error</h2>
		<p class="error">{gameState.error}</p>
		<a href="/">Back to config</a>
	</div>
{:else if gameState.phase === 'setup'}
	<div class="status-page">
		<h2>Game Ready</h2>
		<p>{gameState.setup?.config.num_players} players, {gameState.setup?.total_events} events to replay</p>
		<p class="subtext">Starting playback...</p>
	</div>
{:else}
	<!-- Playing or Complete -->
	<div class="game-page">
		<div class="game-header">
			<h2>
				{#if gameState.phase === 'complete'}
					Game Complete
					{#if gameState.completion?.game_status.winner}
						 - {gameState.completion.game_status.winner} Wins!
					{/if}
				{:else}
					Game In Progress
				{/if}
			</h2>
			{#if gameState.phase === 'complete'}
				<button class="results-btn" onclick={viewResults}>View Results</button>
			{/if}
		</div>

		<PlaybackControls
			progress={gameState.progress}
			{paused}
			{speed}
			totalEvents={gameState.setup?.total_events || 0}
			currentEvents={gameState.events.length}
			onPause={handlePause}
			onResume={handleResume}
			onSetSpeed={handleSetSpeed}
			onSkipToEnd={handleSkipToEnd}
		/>

		<div class="game-layout">
			<div class="board-area">
				<GameBoard state={gameState} />
			</div>
			<div class="log-area">
				<EventLog events={gameState.events} />
			</div>
		</div>
	</div>
{/if}

<style>
	.status-page {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 50vh;
		gap: 1rem;
	}

	.status-page h2 {
		font-size: 1.5rem;
	}

	.status-page p {
		color: var(--text-secondary);
	}

	.subtext {
		color: var(--text-muted) !important;
		font-size: 0.85rem;
	}

	.error {
		color: var(--danger) !important;
	}

	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid var(--border);
		border-top-color: var(--accent);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	.game-page {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.game-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.game-header h2 {
		font-size: 1.25rem;
	}

	.results-btn {
		background: var(--accent);
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: var(--radius);
		font-size: 0.85rem;
		font-weight: 600;
	}

	.results-btn:hover {
		background: var(--accent-light);
	}

	.game-layout {
		display: grid;
		grid-template-columns: 1fr 300px;
		gap: 1rem;
	}

	@media (max-width: 900px) {
		.game-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
