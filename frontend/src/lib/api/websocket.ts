import { get } from 'svelte/store';
import { gameStore } from '$lib/stores/gameStore';
import type {
	WSMessage,
	GameSetupPayload,
	EventBatchPayload,
	GameCompletePayload
} from './types';

export class GameWebSocket {
	private ws: WebSocket | null = null;
	private gameId: string;

	constructor(gameId: string) {
		this.gameId = gameId;
	}

	connect() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const url = `${protocol}//${window.location.host}/ws/games/${this.gameId}`;
		this.ws = new WebSocket(url);

		this.ws.onmessage = (event) => {
			const msg: WSMessage = JSON.parse(event.data);

			switch (msg.type) {
				case 'game_setup':
					gameStore.setSetup(msg.payload as GameSetupPayload);
					// Brief pause to show initial state, then start playback
					setTimeout(() => gameStore.startPlaying(), 1200);
					break;

				case 'event_batch': {
					const batch = msg.payload as EventBatchPayload;
					gameStore.addEvents(batch.events, batch.progress);
					break;
				}

				case 'game_complete':
					gameStore.setComplete(msg.payload as GameCompletePayload);
					break;

				case 'error': {
					const errPayload = msg.payload as { message: string };
					gameStore.setError(errPayload.message);
					break;
				}
			}
		};

		this.ws.onerror = () => {
			// Only set error if the game hasn't already completed
			if (get(gameStore).phase !== 'complete') {
				gameStore.setError('WebSocket connection error');
			}
		};

		this.ws.onclose = (event) => {
			// Normal closure (1000) or game already complete — no action needed
			// Unexpected closure during play is an error
			if (event.code !== 1000 && get(gameStore).phase !== 'complete') {
				gameStore.setError('WebSocket connection closed unexpectedly');
			}
		};
	}

	sendControl(action: string, value?: number) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify({ type: 'playback_control', action, value }));
		}
	}

	disconnect() {
		this.ws?.close();
		this.ws = null;
	}
}
