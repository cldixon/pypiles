<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { createGame, getStrategies } from '$lib/api/client';
	import ConfigSummary from '$lib/components/config/ConfigSummary.svelte';

	let numPlayers = $state(2);
	let pileSize = $state(4);
	let numPilesPerPlayer = $state(6);
	let winningScore = $state<number | null>(null);
	let strategy = $state('GreedySwapper');
	let strategies = $state<string[]>([]);
	let error = $state('');
	let loading = $state(false);

	const maxPilesPerPlayer = $derived(Math.floor(49 / numPlayers));
	const itemsRequired = $derived(numPlayers * numPilesPerPlayer + 1);
	const totalCards = $derived(itemsRequired * pileSize);
	const cardsPerPlayer = $derived(numPilesPerPlayer * pileSize);
	const isValid = $derived(
		numPlayers * numPilesPerPlayer <= 49 && itemsRequired <= 50
	);

	// Clamp piles when player count changes
	$effect(() => {
		if (numPilesPerPlayer > maxPilesPerPlayer) {
			numPilesPerPlayer = maxPilesPerPlayer;
		}
	});

	onMount(async () => {
		try {
			strategies = await getStrategies();
		} catch {
			strategies = ['GreedySwapper'];
		}
	});

	async function handleStart() {
		if (!isValid) return;
		error = '';
		loading = true;
		try {
			const gameId = await createGame({
				num_players: numPlayers,
				pile_size: pileSize,
				num_piles_per_player: numPilesPerPlayer,
				winning_score: winningScore,
				strategy
			});
			goto(`/game/${gameId}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create game';
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>PyPiles - Configure Game</title>
</svelte:head>

<div class="config-page">
	<div class="hero">
		<h1>New Game</h1>
		<p>Configure your concurrent card game simulation</p>
	</div>

	<div class="config-layout">
		<div class="config-form">
			<div class="form-group">
				<label for="players">
					Players
					<span class="value-badge">{numPlayers}</span>
				</label>
				<input
					id="players"
					type="range"
					min="2"
					max="8"
					bind:value={numPlayers}
				/>
				<div class="range-labels">
					<span>2</span>
					<span>8</span>
				</div>
			</div>

			<div class="form-group">
				<label for="piles">
					Piles per Player
					<span class="value-badge">{numPilesPerPlayer}</span>
				</label>
				<input
					id="piles"
					type="range"
					min="1"
					max={maxPilesPerPlayer}
					bind:value={numPilesPerPlayer}
				/>
				<div class="range-labels">
					<span>1</span>
					<span>{maxPilesPerPlayer}</span>
				</div>
			</div>

			<div class="form-group">
				<label for="pile-size">
					Pile Size (cards per pile)
					<span class="value-badge">{pileSize}</span>
				</label>
				<input
					id="pile-size"
					type="range"
					min="2"
					max="10"
					bind:value={pileSize}
				/>
				<div class="range-labels">
					<span>2</span>
					<span>10</span>
				</div>
			</div>

			<div class="form-group">
				<label for="winning-score">
					Winning Score
					<span class="value-badge">{winningScore ?? 'All piles'}</span>
				</label>
				<input
					id="winning-score"
					type="range"
					min="1"
					max={numPilesPerPlayer}
					value={winningScore ?? numPilesPerPlayer}
					oninput={(e) => {
						const v = parseInt(e.currentTarget.value);
						winningScore = v === numPilesPerPlayer ? null : v;
					}}
				/>
				<div class="range-labels">
					<span>1</span>
					<span>{numPilesPerPlayer} (all)</span>
				</div>
			</div>

			<div class="form-group">
				<label for="strategy">Strategy</label>
				<select id="strategy" bind:value={strategy}>
					{#each strategies as s}
						<option value={s}>{s}</option>
					{/each}
				</select>
			</div>

			{#if error}
				<div class="error">{error}</div>
			{/if}

			<button
				class="start-btn"
				onclick={handleStart}
				disabled={!isValid || loading}
			>
				{loading ? 'Starting...' : 'Start Game'}
			</button>
		</div>

		<ConfigSummary
			{numPlayers}
			{pileSize}
			{numPilesPerPlayer}
			{itemsRequired}
			{totalCards}
			{cardsPerPlayer}
			{isValid}
		/>
	</div>
</div>

<style>
	.config-page {
		max-width: 800px;
		margin: 0 auto;
	}

	.hero {
		margin-bottom: 2rem;
	}

	.hero h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 0.25rem;
	}

	.hero p {
		color: var(--text-secondary);
	}

	.config-layout {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
	}

	@media (max-width: 700px) {
		.config-layout {
			grid-template-columns: 1fr;
		}
	}

	.config-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--text-secondary);
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.value-badge {
		background: var(--accent);
		color: white;
		padding: 0.1rem 0.5rem;
		border-radius: 10px;
		font-size: 0.75rem;
		font-weight: 700;
	}

	input[type='range'] {
		-webkit-appearance: none;
		appearance: none;
		width: 100%;
		height: 6px;
		background: var(--border);
		border-radius: 3px;
		outline: none;
	}

	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 18px;
		height: 18px;
		background: var(--accent);
		border-radius: 50%;
		cursor: pointer;
	}

	.range-labels {
		display: flex;
		justify-content: space-between;
		font-size: 0.7rem;
		color: var(--text-muted);
	}

	select {
		background: var(--bg-card);
		color: var(--text-primary);
		border: 1px solid var(--border);
		padding: 0.5rem 0.75rem;
		border-radius: var(--radius);
		font-size: 0.9rem;
	}

	.error {
		background: rgba(225, 112, 85, 0.15);
		color: var(--danger);
		padding: 0.75rem;
		border-radius: var(--radius);
		font-size: 0.85rem;
	}

	.start-btn {
		background: var(--accent);
		color: white;
		border: none;
		padding: 0.875rem 1.5rem;
		border-radius: var(--radius);
		font-size: 1rem;
		font-weight: 600;
		transition: background 0.2s;
		margin-top: 0.5rem;
	}

	.start-btn:hover:not(:disabled) {
		background: var(--accent-light);
	}

	.start-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
