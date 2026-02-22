import { describe, it, expect } from 'vitest';
import { CARD_COLORS, CARD_TEXT_COLORS, PLAYER_COLORS } from './colors';

describe('CARD_COLORS', () => {
	it('contains all 10 expected colors', () => {
		const expectedColors = [
			'black', 'blue', 'gray', 'green', 'orange',
			'pink', 'purple', 'red', 'white', 'yellow'
		];
		expect(Object.keys(CARD_COLORS).sort()).toEqual(expectedColors);
	});

	it('all values are valid hex color strings', () => {
		for (const hex of Object.values(CARD_COLORS)) {
			expect(hex).toMatch(/^#[0-9a-fA-F]{6}$/);
		}
	});
});

describe('CARD_TEXT_COLORS', () => {
	it('has the same keys as CARD_COLORS', () => {
		expect(Object.keys(CARD_TEXT_COLORS).sort())
			.toEqual(Object.keys(CARD_COLORS).sort());
	});

	it('light cards have dark text for contrast', () => {
		expect(CARD_TEXT_COLORS['white']).toBe('#1a1a2e');
		expect(CARD_TEXT_COLORS['yellow']).toBe('#1a1a2e');
	});

	it('dark cards have light text', () => {
		expect(CARD_TEXT_COLORS['black']).toBe('#ffffff');
		expect(CARD_TEXT_COLORS['blue']).toBe('#ffffff');
	});
});

describe('PLAYER_COLORS', () => {
	it('provides 8 player colors', () => {
		expect(PLAYER_COLORS).toHaveLength(8);
	});

	it('all values are valid hex color strings', () => {
		for (const hex of PLAYER_COLORS) {
			expect(hex).toMatch(/^#[0-9a-fA-F]{6}$/);
		}
	});

	it('all player colors are unique', () => {
		const unique = new Set(PLAYER_COLORS);
		expect(unique.size).toBe(PLAYER_COLORS.length);
	});
});
