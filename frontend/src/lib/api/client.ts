import type { ConfigConstraints, GameConfig } from './types';

export const API_BASE = import.meta.env.VITE_API_URL || '';

export async function createGame(config: Partial<GameConfig>): Promise<string> {
	const res = await fetch(`${API_BASE}/api/games`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(config)
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail || 'Failed to create game');
	}
	const data = await res.json();
	return data.game_id;
}

export async function getStrategies(): Promise<string[]> {
	const res = await fetch(`${API_BASE}/api/strategies`);
	const data = await res.json();
	return data.strategies;
}

export async function getConfigConstraints(): Promise<ConfigConstraints> {
	const res = await fetch(`${API_BASE}/api/config-constraints`);
	return res.json();
}

export async function getGame(gameId: string) {
	const res = await fetch(`${API_BASE}/api/games/${gameId}`);
	if (!res.ok) throw new Error('Game not found');
	return res.json();
}

export async function getGameEvents(gameId: string) {
	const res = await fetch(`${API_BASE}/api/games/${gameId}/events`);
	if (!res.ok) throw new Error('Failed to fetch events');
	return res.json();
}
