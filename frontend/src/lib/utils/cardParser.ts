import type { CardInfo } from '$lib/api/types';

export function parseCard(cardId: string): CardInfo {
	const [color, item] = cardId.split('::');
	return { id: cardId, color, item };
}

export function formatItemName(item: string): string {
	return item.replace(/-/g, ' ');
}
