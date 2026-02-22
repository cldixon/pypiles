<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { getGame } from '$lib/api/client';
	import type { GameCompletePayload, PlayerState, GameConfig } from '$lib/api/types';
	import WinnerBanner from '$lib/components/results/WinnerBanner.svelte';
	import PlayerStatsTable from '$lib/components/results/PlayerStatsTable.svelte';
	import GameSummaryCard from '$lib/components/results/GameSummaryCard.svelte';
	import ActivityChart from '$lib/components/results/ActivityChart.svelte';

	const gameId = $derived(page.params.id ?? '');

	let loading = $state(true);
	let error = $state('');
	let gameData = $state<{
		config: GameConfig;
		final_state: GameCompletePayload;
		total_events: number;
	} | null>(null);

	onMount(async () => {
		try {
			const data = await getGame(gameId);
			if (data.phase !== 'completed' || !data.final_state) {
				error = 'Game has not completed yet.';
			} else {
				gameData = {
					config: data.config,
					final_state: data.final_state,
					total_events: data.total_events
				};
			}
		} catch {
			error = 'Failed to load game data.';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>PyPiles - Results {gameId.slice(0, 8)}</title>
</svelte:head>

{#if loading}
	<div class="loading">
		<div class="spinner"></div>
		<p>Loading results...</p>
	</div>
{:else if error}
	<div class="loading">
		<p class="error">{error}</p>
		<a href="/">New Game</a>
	</div>
{:else if gameData}
	<div class="results-page">
		<WinnerBanner
			winner={gameData.final_state.game_status.winner}
			durationMs={gameData.final_state.duration_ms}
		/>

		<div class="results-grid">
			<GameSummaryCard
				config={gameData.config}
				totalEvents={gameData.total_events}
				durationMs={gameData.final_state.duration_ms}
				centerPileMetrics={gameData.final_state.center_pile.metrics}
			/>

			<PlayerStatsTable players={gameData.final_state.players} />
		</div>

		<ActivityChart players={gameData.final_state.players} />

		<div class="actions">
			<a href="/" class="action-btn">New Game</a>
		</div>
	</div>
{/if}

<style>
	.loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 50vh;
		gap: 1rem;
	}

	.loading p {
		color: var(--text-secondary);
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

	.results-page {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.results-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}

	@media (max-width: 700px) {
		.results-grid {
			grid-template-columns: 1fr;
		}
	}

	.actions {
		display: flex;
		justify-content: center;
		margin-top: 1rem;
	}

	.action-btn {
		background: var(--accent);
		color: white;
		padding: 0.75rem 2rem;
		border-radius: var(--radius);
		font-weight: 600;
		font-size: 0.9rem;
	}

	.action-btn:hover {
		background: var(--accent-light);
		text-decoration: none;
	}
</style>
