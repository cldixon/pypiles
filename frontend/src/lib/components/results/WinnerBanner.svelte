<script lang="ts">
	import { PLAYER_COLORS } from '$lib/utils/colors';

	let { winner, durationMs }: { winner: string | null; durationMs: number } = $props();

	const playerIndex = $derived(winner ? parseInt(winner.replace('P', '')) - 1 : 0);
	const color = $derived(PLAYER_COLORS[playerIndex] || PLAYER_COLORS[0]);
</script>

<div class="banner" style="--winner-color: {color}">
	<div class="trophy">&#127942;</div>
	<h1>
		{#if winner}
			{winner} Wins!
		{:else}
			Game Over
		{/if}
	</h1>
	<p class="duration">
		Completed in {durationMs < 1000 ? durationMs.toFixed(1) + 'ms' : (durationMs / 1000).toFixed(2) + 's'}
	</p>
</div>

<style>
	.banner {
		background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
		border: 2px solid var(--winner-color);
		border-radius: var(--radius-lg);
		padding: 2rem;
		text-align: center;
	}

	.trophy {
		font-size: 3rem;
		margin-bottom: 0.5rem;
	}

	h1 {
		font-size: 2rem;
		color: var(--winner-color);
		margin-bottom: 0.25rem;
	}

	.duration {
		color: var(--text-muted);
		font-size: 0.9rem;
	}
</style>
