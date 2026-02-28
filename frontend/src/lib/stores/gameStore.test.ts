import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { gameStore } from './gameStore';
import type {
	GameSetupPayload,
	GameEvent,
	GameCompletePayload
} from '$lib/api/types';

function state() {
	return get(gameStore);
}

function mockSetup(): GameSetupPayload {
	return {
		config: {
			num_players: 2,
			pile_size: 4,
			num_piles_per_player: 2,
			winning_score: null,
			player_characters: ['greedy-nathan', 'greedy-nathan']
		},
		center_pile: ['red::tophat', 'blue::cardigan', 'green::hoody', 'yellow::mittens'],
		players: [
			{
				id: 'P1',
				piles: [
					['red::flip-flops', 'blue::flip-flops', 'green::flip-flops', 'yellow::flip-flops'],
					['red::cardigan', 'blue::hoody', 'green::mittens', 'yellow::tophat']
				],
				num_piles: 2
			},
			{
				id: 'P2',
				piles: [
					['pink::tophat', 'orange::tophat', 'purple::tophat', 'white::cardigan'],
					['pink::hoody', 'orange::mittens', 'purple::cardigan', 'white::hoody']
				],
				num_piles: 2
			}
		],
		total_events: 20,
		mode: 'replay'
	};
}

describe('gameStore', () => {
	beforeEach(() => {
		gameStore.reset();
	});

	describe('initial state', () => {
		it('starts in connecting phase', () => {
			expect(state().phase).toBe('connecting');
		});

		it('has empty events', () => {
			expect(state().events).toEqual([]);
		});

		it('has zero progress', () => {
			expect(state().progress).toBe(0);
		});

		it('has no error', () => {
			expect(state().error).toBeNull();
		});
	});

	describe('reset', () => {
		it('returns to initial state after modification', () => {
			gameStore.setSetup(mockSetup());
			gameStore.reset();
			expect(state().phase).toBe('connecting');
			expect(state().setup).toBeNull();
			expect(state().playerPiles.size).toBe(0);
		});
	});

	describe('setSetup', () => {
		it('transitions to setup phase', () => {
			gameStore.setSetup(mockSetup());
			expect(state().phase).toBe('setup');
		});

		it('populates center pile', () => {
			gameStore.setSetup(mockSetup());
			expect(state().centerPile).toEqual([
				'red::tophat', 'blue::cardigan', 'green::hoody', 'yellow::mittens'
			]);
		});

		it('populates player piles map', () => {
			gameStore.setSetup(mockSetup());
			expect(state().playerPiles.size).toBe(2);
			expect(state().playerPiles.has('P1')).toBe(true);
			expect(state().playerPiles.has('P2')).toBe(true);
			expect(state().playerPiles.get('P1')!.length).toBe(2);
		});

		it('initializes scores to zero', () => {
			gameStore.setSetup(mockSetup());
			expect(state().playerScores.get('P1')).toBe(0);
			expect(state().playerScores.get('P2')).toBe(0);
		});

		it('initializes completed piles as empty', () => {
			gameStore.setSetup(mockSetup());
			expect(state().playerCompleted.get('P1')).toEqual([]);
			expect(state().playerCompleted.get('P2')).toEqual([]);
		});
	});

	describe('startPlaying', () => {
		it('transitions from setup to playing', () => {
			gameStore.setSetup(mockSetup());
			gameStore.startPlaying();
			expect(state().phase).toBe('playing');
		});
	});

	describe('addEvents - swap_succeeded', () => {
		it('updates player pile with received card', () => {
			gameStore.setSetup(mockSetup());
			gameStore.startPlaying();
			const events: GameEvent[] = [
				{
					seq: 0,
					timestamp: 1000,
					event_type: 'swap_succeeded',
					actor: 'P1',
					data: {
						player_id: 'P1',
						pile_idx: 1,
						card_idx: 0,
						sent_card: 'red::cardigan',
						received_card: 'pink::tophat',
						target_position: 0
					}
				}
			];
			gameStore.addEvents(events, 0.1);
			const p1Piles = state().playerPiles.get('P1')!;
			expect(p1Piles[1][0]).toBe('pink::tophat');
		});

		it('adds swap to recentSwaps', () => {
			gameStore.setSetup(mockSetup());
			const events: GameEvent[] = [
				{
					seq: 0,
					timestamp: 1000,
					event_type: 'swap_succeeded',
					actor: 'P1',
					data: {
						player_id: 'P1',
						pile_idx: 0,
						card_idx: 0,
						sent_card: 'red::flip-flops',
						received_card: 'pink::tophat',
						target_position: 0
					}
				}
			];
			gameStore.addEvents(events, 0.1);
			expect(state().recentSwaps.length).toBe(1);
			expect(state().recentSwaps[0].sentCard).toBe('red::flip-flops');
			expect(state().recentSwaps[0].receivedCard).toBe('pink::tophat');
		});

		it('limits recentSwaps to 10', () => {
			gameStore.setSetup(mockSetup());
			const events: GameEvent[] = Array.from({ length: 12 }, (_, i) => ({
				seq: i,
				timestamp: 1000 + i,
				event_type: 'swap_succeeded',
				actor: 'P1',
				data: {
					player_id: 'P1',
					pile_idx: 0,
					card_idx: 0,
					sent_card: `card-${i}`,
					received_card: `card-${i + 100}`,
					target_position: 0
				}
			}));
			gameStore.addEvents(events, 0.5);
			expect(state().recentSwaps.length).toBe(10);
		});

		it('updates progress', () => {
			gameStore.setSetup(mockSetup());
			gameStore.addEvents([], 0.5);
			expect(state().progress).toBe(0.5);
		});
	});

	describe('addEvents - center_pile_updated', () => {
		it('replaces center pile cards', () => {
			gameStore.setSetup(mockSetup());
			const events: GameEvent[] = [
				{
					seq: 0,
					timestamp: 1000,
					event_type: 'center_pile_updated',
					actor: 'CP',
					data: { cards_after: ['a::x', 'b::y', 'c::z', 'd::w'] }
				}
			];
			gameStore.addEvents(events, 0.2);
			expect(state().centerPile).toEqual(['a::x', 'b::y', 'c::z', 'd::w']);
		});
	});

	describe('addEvents - pile_completed', () => {
		it('moves pile from active to completed and updates score', () => {
			gameStore.setSetup(mockSetup());
			const events: GameEvent[] = [
				{
					seq: 0,
					timestamp: 1000,
					event_type: 'pile_completed',
					actor: 'P1',
					data: {
						player_id: 'P1',
						pile_idx: 0,
						pile_cards: [
							'red::flip-flops',
							'blue::flip-flops',
							'green::flip-flops',
							'yellow::flip-flops'
						],
						score: 1
					}
				}
			];
			gameStore.addEvents(events, 0.3);
			expect(state().playerPiles.get('P1')!.length).toBe(1);
			expect(state().playerCompleted.get('P1')!.length).toBe(1);
			expect(state().playerScores.get('P1')).toBe(1);
		});
	});

	describe('setComplete', () => {
		it('transitions to complete phase with progress 1', () => {
			gameStore.setSetup(mockSetup());
			gameStore.startPlaying();
			const completion: GameCompletePayload = {
				game_status: {
					active: false,
					start_time: '2025-01-01',
					end_time: '2025-01-01',
					winner: 'P1'
				},
				center_pile: {
					cards: [],
					metrics: { num_views: 10, num_requests: 5, num_swaps: 3 }
				},
				players: [],
				duration_ms: 55,
				total_events: 20
			};
			gameStore.setComplete(completion);
			expect(state().phase).toBe('complete');
			expect(state().completion).toBe(completion);
			expect(state().progress).toBe(1);
		});
	});

	describe('setError', () => {
		it('sets error phase and message', () => {
			gameStore.setError('Connection failed');
			expect(state().phase).toBe('error');
			expect(state().error).toBe('Connection failed');
		});
	});
});
