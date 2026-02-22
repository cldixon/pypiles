import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createGame, getStrategies, getConfigConstraints, getGame, getGameEvents } from './client';

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
	mockFetch.mockReset();
});

describe('createGame', () => {
	it('returns game_id on success', async () => {
		mockFetch.mockResolvedValue({
			ok: true,
			json: async () => ({ game_id: 'abc-123' })
		});
		const id = await createGame({ num_players: 2 });
		expect(id).toBe('abc-123');
		expect(mockFetch).toHaveBeenCalledWith(
			'/api/games',
			expect.objectContaining({
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			})
		);
	});

	it('throws with detail message on error', async () => {
		mockFetch.mockResolvedValue({
			ok: false,
			json: async () => ({ detail: 'Bad config' })
		});
		await expect(createGame({})).rejects.toThrow('Bad config');
	});

	it('throws fallback message when detail is missing', async () => {
		mockFetch.mockResolvedValue({
			ok: false,
			json: async () => ({})
		});
		await expect(createGame({})).rejects.toThrow('Failed to create game');
	});
});

describe('getStrategies', () => {
	it('returns strategies array', async () => {
		mockFetch.mockResolvedValue({
			ok: true,
			json: async () => ({ strategies: ['GreedySwapper'] })
		});
		const result = await getStrategies();
		expect(result).toEqual(['GreedySwapper']);
	});
});

describe('getConfigConstraints', () => {
	it('returns constraint object', async () => {
		const constraints = { num_players: { min: 2, max: 8 } };
		mockFetch.mockResolvedValue({
			ok: true,
			json: async () => constraints
		});
		const result = await getConfigConstraints();
		expect(result.num_players.min).toBe(2);
	});
});

describe('getGame', () => {
	it('returns game data on success', async () => {
		mockFetch.mockResolvedValue({
			ok: true,
			json: async () => ({ game_id: 'x', phase: 'completed' })
		});
		const result = await getGame('x');
		expect(result.phase).toBe('completed');
	});

	it('throws on 404', async () => {
		mockFetch.mockResolvedValue({ ok: false });
		await expect(getGame('missing')).rejects.toThrow('Game not found');
	});
});

describe('getGameEvents', () => {
	it('returns events on success', async () => {
		mockFetch.mockResolvedValue({
			ok: true,
			json: async () => ({ events: [{ seq: 0 }] })
		});
		const result = await getGameEvents('x');
		expect(result.events.length).toBe(1);
	});

	it('throws on error', async () => {
		mockFetch.mockResolvedValue({ ok: false });
		await expect(getGameEvents('x')).rejects.toThrow('Failed to fetch events');
	});
});
