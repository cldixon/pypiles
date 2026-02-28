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
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 2;
	private reconnectDelay = 2000;

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
				case 'game_setup': {
					this.reconnectAttempts = 0;
					const setup = msg.payload as GameSetupPayload;
					gameStore.setSetup(setup);
					if (setup.mode === 'live') {
						// Start immediately for live games
						gameStore.startPlaying();
					} else {
						// Brief pause to show initial state, then start replay
						setTimeout(() => gameStore.startPlaying(), 1200);
					}
					break;
				}

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
				if (this.reconnectAttempts < this.maxReconnectAttempts) {
					// Will attempt reconnect in onclose handler
				} else {
					gameStore.setError('Connection to the game server failed.');
				}
			}
		};

		this.ws.onclose = (event) => {
			// Normal closure (1000) or game already complete -- no action needed
			if (event.code === 1000 || get(gameStore).phase === 'complete') {
				return;
			}
			// Unexpected closure during play -- attempt reconnect
			if (this.reconnectAttempts < this.maxReconnectAttempts) {
				this.reconnectAttempts++;
				setTimeout(() => this.connect(), this.reconnectDelay);
			} else {
				gameStore.setError(
					'Connection to the game server was lost. The server may be restarting.'
				);
			}
		};
	}

	sendControl(action: string, value?: number) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify({ type: 'playback_control', action, value }));
		}
	}

	disconnect() {
		this.reconnectAttempts = this.maxReconnectAttempts; // prevent reconnect on intentional close
		this.ws?.close();
		this.ws = null;
	}
}
