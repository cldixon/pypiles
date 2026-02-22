<script lang="ts">
	import type { PlayerState } from '$lib/api/types';
	import { PLAYER_COLORS } from '$lib/utils/colors';

	let { players }: { players: PlayerState[] } = $props();

	function successRate(p: PlayerState): string {
		if (p.metrics.num_requests === 0) return '0%';
		return ((p.metrics.num_swaps / p.metrics.num_requests) * 100).toFixed(1) + '%';
	}
</script>

<div class="stats-card">
	<h3>Player Statistics</h3>
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>Player</th>
					<th>Score</th>
					<th>Requests</th>
					<th>Swaps</th>
					<th>Success Rate</th>
					<th>Remaining</th>
				</tr>
			</thead>
			<tbody>
				{#each players as player, i}
					<tr>
						<td>
							<span class="player-dot" style="background: {PLAYER_COLORS[i]}"></span>
							{player.id}
						</td>
						<td class="num">{player.score}</td>
						<td class="num">{player.metrics.num_requests}</td>
						<td class="num">{player.metrics.num_swaps}</td>
						<td class="num">{successRate(player)}</td>
						<td class="num">{player.remaining.length}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<style>
	.stats-card {
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

	.table-wrapper {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}

	th {
		text-align: left;
		padding: 0.5rem;
		border-bottom: 1px solid var(--border);
		color: var(--text-secondary);
		font-weight: 600;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.03em;
	}

	td {
		padding: 0.5rem;
		border-bottom: 1px solid rgba(51, 51, 85, 0.5);
	}

	.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	.player-dot {
		display: inline-block;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		margin-right: 0.4rem;
	}
</style>
