import { writable } from 'svelte/store';
import type {
	GameSetupPayload,
	GameEvent,
	GameCompletePayload,
	PlayerState
} from '$lib/api/types';

export type GamePhase = 'connecting' | 'setup' | 'playing' | 'complete' | 'error';

export interface GameState {
	phase: GamePhase;
	setup: GameSetupPayload | null;
	events: GameEvent[];
	completion: GameCompletePayload | null;
	progress: number;
	error: string | null;
	// Live game state derived from events
	centerPile: string[];
	playerPiles: Map<string, string[][]>;
	playerCompleted: Map<string, string[][]>;
	playerScores: Map<string, number>;
	recentSwaps: SwapHighlight[];
}

export interface SwapHighlight {
	id: number;
	playerId: string;
	sentCard: string;
	receivedCard: string;
	pileIdx: number;
	timestamp: number;
}

function createInitialState(): GameState {
	return {
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
	};
}

function createGameStore() {
	const { subscribe, set, update } = writable<GameState>(createInitialState());

	let swapIdCounter = 0;

	return {
		subscribe,
		reset() {
			swapIdCounter = 0;
			set(createInitialState());
		},
		setSetup(setup: GameSetupPayload) {
			update((s) => {
				const playerPiles = new Map<string, string[][]>();
				const playerCompleted = new Map<string, string[][]>();
				const playerScores = new Map<string, number>();
				for (const p of setup.players) {
					playerPiles.set(p.id, [...p.piles]);
					playerCompleted.set(p.id, []);
					playerScores.set(p.id, 0);
				}
				return {
					...s,
					phase: 'setup',
					setup,
					centerPile: [...setup.center_pile],
					playerPiles,
					playerCompleted,
					playerScores
				};
			});
		},
		startPlaying() {
			update((s) => ({ ...s, phase: 'playing' }));
		},
		addEvents(events: GameEvent[], progress: number) {
			update((s) => {
				const newRecentSwaps = [...s.recentSwaps];
				let centerPile = [...s.centerPile];
				const playerPiles = new Map(s.playerPiles);
				const playerCompleted = new Map(s.playerCompleted);
				const playerScores = new Map(s.playerScores);

				for (const event of events) {
					switch (event.event_type) {
						case 'swap_succeeded': {
							const data = event.data as {
								player_id: string;
								pile_idx: number;
								card_idx: number;
								sent_card: string;
								received_card: string;
								target_position: number;
							};
							// Update player's pile
							const piles = playerPiles.get(data.player_id);
							if (piles && piles[data.pile_idx]) {
								piles[data.pile_idx] = [...piles[data.pile_idx]];
								piles[data.pile_idx][data.card_idx] = data.received_card;
								playerPiles.set(data.player_id, [...piles]);
							}
							newRecentSwaps.push({
								id: swapIdCounter++,
								playerId: data.player_id,
								sentCard: data.sent_card,
								receivedCard: data.received_card,
								pileIdx: data.pile_idx,
								timestamp: Date.now()
							});
							// Keep only last 10 swaps
							while (newRecentSwaps.length > 10) newRecentSwaps.shift();
							break;
						}
						case 'center_pile_updated': {
							const data = event.data as { cards_after: string[] };
							centerPile = [...data.cards_after];
							break;
						}
						case 'pile_completed': {
							const data = event.data as {
								player_id: string;
								pile_idx: number;
								pile_cards: string[];
								score: number;
							};
							const piles = playerPiles.get(data.player_id);
							if (piles) {
								const completedList = playerCompleted.get(data.player_id) || [];
								completedList.push(data.pile_cards);
								playerCompleted.set(data.player_id, [...completedList]);
								piles.splice(data.pile_idx, 1);
								playerPiles.set(data.player_id, [...piles]);
							}
							playerScores.set(data.player_id, data.score);
							break;
						}
					}
				}

				return {
					...s,
					events: [...s.events, ...events],
					progress,
					centerPile,
					playerPiles,
					playerCompleted,
					playerScores,
					recentSwaps: newRecentSwaps
				};
			});
		},
		setComplete(completion: GameCompletePayload) {
			update((s) => ({
				...s,
				phase: 'complete',
				completion,
				progress: 1
			}));
		},
		setError(message: string) {
			update((s) => ({ ...s, phase: 'error', error: message }));
		}
	};
}

export const gameStore = createGameStore();
