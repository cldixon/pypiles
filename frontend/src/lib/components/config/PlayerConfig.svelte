<script lang="ts">
	import type { Character } from '$lib/api/types';

	let {
		playerIndex,
		characters,
		selectedCharacterId = $bindable(),
	}: {
		playerIndex: number;
		characters: Character[];
		selectedCharacterId: string;
	} = $props();

	const selectedCharacter = $derived(
		characters.find((c) => c.id === selectedCharacterId)
	);
</script>

<div class="player-config">
	<div class="player-header">
		<span class="player-label">Player {playerIndex + 1}</span>
	</div>
	<select bind:value={selectedCharacterId}>
		{#each characters as char}
			<option value={char.id}>{char.name}</option>
		{/each}
	</select>
	{#if selectedCharacter}
		<p class="char-description">{selectedCharacter.description}</p>
	{/if}
</div>

<style>
	.player-config {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.player-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.player-label {
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	select {
		background: var(--bg-secondary);
		color: var(--text-primary);
		border: 1px solid var(--border);
		padding: 0.4rem 0.6rem;
		border-radius: var(--radius);
		font-size: 0.85rem;
		width: 100%;
	}

	.char-description {
		font-size: 0.75rem;
		color: var(--text-muted);
		margin: 0;
		line-height: 1.3;
	}
</style>
