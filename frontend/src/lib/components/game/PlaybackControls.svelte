<script lang="ts">
	let {
		progress,
		paused,
		speed,
		mode = 'replay',
		totalEvents,
		currentEvents,
		onPause,
		onResume,
		onSetSpeed,
		onSkipToEnd
	}: {
		progress: number;
		paused: boolean;
		speed: number;
		mode?: 'live' | 'replay';
		totalEvents: number;
		currentEvents: number;
		onPause: () => void;
		onResume: () => void;
		onSetSpeed: (speed: number) => void;
		onSkipToEnd: () => void;
	} = $props();

	const isLive = $derived(mode === 'live');
	const progressPercent = $derived(Math.round(progress * 100));
</script>

<div class="playback-controls">
	{#if isLive}
		<div class="live-bar">
			<span class="live-indicator">LIVE</span>
			<div class="live-pulse"></div>
		</div>
	{:else}
		<div class="progress-bar">
			<div class="progress-fill" style="width: {progressPercent}%"></div>
		</div>
	{/if}

	<div class="controls">
		<button class="control-btn" onclick={() => paused ? onResume() : onPause()}>
			{#if paused}
				&#9654;
			{:else}
				&#9646;&#9646;
			{/if}
		</button>

		{#if !isLive}
			<div class="speed-control">
				<span class="speed-label">Speed</span>
				<input
					type="range"
					min="0.1"
					max="20"
					step="0.1"
					value={speed}
					oninput={(e) => onSetSpeed(parseFloat(e.currentTarget.value))}
				/>
				<span class="speed-value">{speed.toFixed(1)}x</span>
			</div>
		{:else}
			<div class="live-spacer"></div>
		{/if}

		<button class="control-btn skip-btn" onclick={onSkipToEnd}>
			&#9654;&#9654;
		</button>

		<span class="event-counter">
			{#if isLive}
				{currentEvents} events
			{:else}
				{currentEvents} / {totalEvents} events
			{/if}
		</span>
	</div>
</div>

<style>
	.playback-controls {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 0.75rem;
	}

	.progress-bar {
		height: 4px;
		background: var(--border);
		border-radius: 2px;
		overflow: hidden;
		margin-bottom: 0.75rem;
	}

	.progress-fill {
		height: 100%;
		background: var(--accent);
		transition: width 0.15s;
		border-radius: 2px;
	}

	.live-bar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
	}

	.live-indicator {
		font-size: 0.65rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		color: #ef4444;
	}

	.live-pulse {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #ef4444;
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.3; }
	}

	.controls {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.control-btn {
		background: var(--bg-card);
		border: 1px solid var(--border);
		color: var(--text-primary);
		width: 32px;
		height: 32px;
		border-radius: var(--radius);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.8rem;
	}

	.control-btn:hover {
		background: var(--bg-hover);
	}

	.speed-control {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex: 1;
	}

	.speed-label {
		font-size: 0.7rem;
		color: var(--text-muted);
	}

	.speed-control input[type='range'] {
		-webkit-appearance: none;
		appearance: none;
		height: 4px;
		background: var(--border);
		border-radius: 2px;
		flex: 1;
	}

	.speed-control input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 14px;
		height: 14px;
		background: var(--accent);
		border-radius: 50%;
		cursor: pointer;
	}

	.speed-value {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--accent-light);
		min-width: 3rem;
		text-align: right;
	}

	.live-spacer {
		flex: 1;
	}

	.event-counter {
		font-size: 0.7rem;
		color: var(--text-muted);
		white-space: nowrap;
	}
</style>
