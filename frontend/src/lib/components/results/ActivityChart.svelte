<script lang="ts">
	import type { PlayerState } from '$lib/api/types';
	import { PLAYER_COLORS } from '$lib/utils/colors';
	import { onMount } from 'svelte';

	let { players }: { players: PlayerState[] } = $props();

	let canvas: HTMLCanvasElement;

	onMount(async () => {
		const { Chart, BarController, BarElement, CategoryScale, LinearScale, Legend, Tooltip } = await import('chart.js');
		Chart.register(BarController, BarElement, CategoryScale, LinearScale, Legend, Tooltip);

		new Chart(canvas, {
			type: 'bar',
			data: {
				labels: players.map((p) => p.id),
				datasets: [
					{
						label: 'Swap Requests',
						data: players.map((p) => p.metrics.num_requests),
						backgroundColor: players.map((_, i) => PLAYER_COLORS[i] + '88'),
						borderColor: players.map((_, i) => PLAYER_COLORS[i]),
						borderWidth: 1
					},
					{
						label: 'Successful Swaps',
						data: players.map((p) => p.metrics.num_swaps),
						backgroundColor: players.map((_, i) => PLAYER_COLORS[i]),
						borderColor: players.map((_, i) => PLAYER_COLORS[i]),
						borderWidth: 1
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						position: 'top',
						labels: { color: '#a0a0b8', font: { size: 11 } }
					},
					tooltip: {
						backgroundColor: '#222240',
						titleColor: '#e8e8f0',
						bodyColor: '#a0a0b8',
						borderColor: '#333355',
						borderWidth: 1
					}
				},
				scales: {
					x: {
						ticks: { color: '#a0a0b8' },
						grid: { color: '#333355' }
					},
					y: {
						ticks: { color: '#a0a0b8' },
						grid: { color: '#333355' },
						beginAtZero: true
					}
				}
			}
		});
	});
</script>

<div class="chart-card">
	<h3>Player Activity</h3>
	<div class="chart-container">
		<canvas bind:this={canvas}></canvas>
	</div>
</div>

<style>
	.chart-card {
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

	.chart-container {
		height: 250px;
	}
</style>
