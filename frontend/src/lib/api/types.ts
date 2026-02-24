export interface GameConfig {
	num_players: number;
	pile_size: number;
	num_piles_per_player: number;
	winning_score: number | null;
	player_characters: string[];
}

export interface Character {
	id: string;
	name: string;
	description: string;
}

export interface CardInfo {
	id: string;
	color: string;
	item: string;
}

export interface PlayerSetup {
	id: string;
	piles: string[][];
	num_piles: number;
}

export interface GameSetupPayload {
	config: GameConfig;
	center_pile: string[];
	players: PlayerSetup[];
	total_events: number;
}

export interface GameEvent {
	seq: number;
	timestamp: number;
	event_type: string;
	actor: string;
	data: Record<string, unknown>;
}

export interface EventBatchPayload {
	events: GameEvent[];
	progress: number;
}

export interface PlayerMetrics {
	num_requests: number;
	num_swaps: number;
}

export interface PlayerState {
	id: string;
	remaining: string[][];
	completed: string[][];
	metrics: PlayerMetrics;
	score: number;
}

export interface CenterPileMetrics {
	num_views: number;
	num_requests: number;
	num_swaps: number;
}

export interface GameCompletePayload {
	game_status: {
		active: boolean;
		start_time: string;
		end_time: string | null;
		winner: string | null;
	};
	center_pile: {
		cards: string[];
		metrics: CenterPileMetrics;
	};
	players: PlayerState[];
	duration_ms: number;
	total_events: number;
}

export interface WSMessage {
	type: 'game_setup' | 'event_batch' | 'game_complete' | 'error';
	game_id: string;
	payload: GameSetupPayload | EventBatchPayload | GameCompletePayload | { message: string };
}

export interface PlaybackControl {
	type: 'playback_control';
	action: 'pause' | 'resume' | 'set_speed' | 'skip_to_end';
	value?: number;
}

export interface ConfigConstraints {
	num_players: { min: number; max: number };
	pile_size: { min: number; max: number };
	num_piles_per_player: { min: number; max: number };
	product_constraint: string;
	total_items: number;
	total_colors: number;
}
