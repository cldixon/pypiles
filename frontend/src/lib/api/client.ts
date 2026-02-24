import type { Character, ConfigConstraints, GameConfig } from './types';

export async function createGame(config: Partial<GameConfig>): Promise<string> {
	const res = await fetch('/api/games', {
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

export async function getCharacters(): Promise<Character[]> {
	const res = await fetch('/api/characters');
	const data = await res.json();
	return data.characters;
}

export async function getConfigConstraints(): Promise<ConfigConstraints> {
	const res = await fetch('/api/config-constraints');
	return res.json();
}

export async function getGame(gameId: string) {
	const res = await fetch(`/api/games/${gameId}`);
	if (!res.ok) throw new Error('Game not found');
	return res.json();
}

export async function getGameEvents(gameId: string) {
	const res = await fetch(`/api/games/${gameId}/events`);
	if (!res.ok) throw new Error('Failed to fetch events');
	return res.json();
}
