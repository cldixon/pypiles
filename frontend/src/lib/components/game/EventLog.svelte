<script lang="ts">
	import type { GameEvent } from '$lib/api/types';
	import { PLAYER_COLORS } from '$lib/utils/colors';
	import { parseCard, formatItemName } from '$lib/utils/cardParser';

	let { events }: { events: GameEvent[] } = $props();

	// Show last 30 events, most recent first
	const displayEvents = $derived(events.slice(-30).reverse());

	function getPlayerColor(actor: string): string {
		const idx = parseInt(actor.replace('P', '')) - 1;
		return PLAYER_COLORS[idx] || '#888';
	}

	function formatEvent(event: GameEvent): string {
		const data = event.data as Record<string, string>;
		switch (event.event_type) {
			case 'swap_requested':
				return `wants ${formatItemName(parseCard(data.target_card).item)}`;
			case 'swap_succeeded':
				return `swapped ${formatItemName(parseCard(data.sent_card).item)} for ${formatItemName(parseCard(data.received_card).item)}`;
			case 'swap_failed':
				return `swap failed (card taken)`;
			case 'pile_completed':
				return `completed a pile! (score: ${data.score})`;
			case 'game_won':
				return `WON THE GAME!`;
			case 'player_no_swap':
				return `no swap available`;
			case 'center_pile_updated':
				return `center pile updated`;
			case 'game_started':
				return `Game started`;
			case 'game_ended':
				return `Game ended - ${data.winner} wins!`;
			default:
				return event.event_type;
		}
	}

	function getEventIcon(eventType: string): string {
		switch (eventType) {
			case 'swap_succeeded': return '&#8644;';
			case 'swap_failed': return '&#10007;';
			case 'pile_completed': return '&#9733;';
			case 'game_won': return '&#127942;';
			case 'swap_requested': return '&#8680;';
			case 'game_started': return '&#9654;';
			case 'game_ended': return '&#9632;';
			default: return '&#8226;';
		}
	}
</script>

<div class="event-log">
	<h3>Event Log</h3>
	<div class="events">
		{#each displayEvents as event (event.seq)}
			<div class="event" class:success={event.event_type === 'swap_succeeded'}
				class:fail={event.event_type === 'swap_failed'}
				class:complete={event.event_type === 'pile_completed' || event.event_type === 'game_won'}>
				<span class="event-icon">{@html getEventIcon(event.event_type)}</span>
				<span class="event-actor" style="color: {getPlayerColor(event.actor)}">{event.actor}</span>
				<span class="event-text">{formatEvent(event)}</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.event-log {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 0.75rem;
		max-height: 400px;
		display: flex;
		flex-direction: column;
	}

	h3 {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-muted);
		margin-bottom: 0.5rem;
	}

	.events {
		overflow-y: auto;
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	.event {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.2rem 0.3rem;
		border-radius: 4px;
		font-size: 0.7rem;
		color: var(--text-secondary);
	}

	.event.success {
		background: rgba(0, 184, 148, 0.08);
	}

	.event.fail {
		background: rgba(225, 112, 85, 0.08);
	}

	.event.complete {
		background: rgba(108, 92, 231, 0.12);
	}

	.event-icon {
		font-size: 0.75rem;
		min-width: 1rem;
		text-align: center;
	}

	.event-actor {
		font-weight: 700;
		min-width: 1.5rem;
	}

	.event-text {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>
