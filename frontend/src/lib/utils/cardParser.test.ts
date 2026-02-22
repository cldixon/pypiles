import { describe, it, expect } from 'vitest';
import { parseCard, formatItemName } from './cardParser';

describe('parseCard', () => {
	it('parses a standard card id', () => {
		const result = parseCard('red::tophat');
		expect(result).toEqual({ id: 'red::tophat', color: 'red', item: 'tophat' });
	});

	it('handles hyphenated item names', () => {
		const result = parseCard('blue::argyle-sweater-vest');
		expect(result.color).toBe('blue');
		expect(result.item).toBe('argyle-sweater-vest');
		expect(result.id).toBe('blue::argyle-sweater-vest');
	});

	it('preserves the full id string', () => {
		const result = parseCard('green::flip-flops');
		expect(result.id).toBe('green::flip-flops');
	});
});

describe('formatItemName', () => {
	it('replaces hyphens with spaces', () => {
		expect(formatItemName('argyle-sweater-vest')).toBe('argyle sweater vest');
	});

	it('returns single-word items unchanged', () => {
		expect(formatItemName('tophat')).toBe('tophat');
	});
});
