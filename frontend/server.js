import { createServer } from 'node:http';
import { WebSocket, WebSocketServer } from 'ws';
import { handler } from './build/handler.js';

const API_INTERNAL_URL = (process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000').trim().replace(/\/+$/, '');
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

const server = createServer(handler);
const wss = new WebSocketServer({ noServer: true });

server.on('upgrade', (req, socket, head) => {
	const pathname = new URL(req.url, `http://${req.headers.host}`).pathname;

	if (!pathname.startsWith('/ws/')) {
		socket.destroy();
		return;
	}

	const backendWsUrl = API_INTERNAL_URL.replace(/^http/, 'ws') + pathname;
	const backendWs = new WebSocket(backendWsUrl);

	backendWs.on('open', () => {
		wss.handleUpgrade(req, socket, head, (clientWs) => {
			// Relay: client -> backend
			clientWs.on('message', (data, isBinary) => {
				if (backendWs.readyState === WebSocket.OPEN) {
					backendWs.send(data, { binary: isBinary });
				}
			});

			// Relay: backend -> client
			backendWs.on('message', (data, isBinary) => {
				if (clientWs.readyState === WebSocket.OPEN) {
					clientWs.send(data, { binary: isBinary });
				}
			});

			// Close propagation
			clientWs.on('close', (code, reason) => {
				backendWs.close(code, reason);
			});

			backendWs.on('close', (code, reason) => {
				clientWs.close(code, reason);
			});

			// Error handling
			clientWs.on('error', () => backendWs.close());
			backendWs.on('error', () => clientWs.close());
		});
	});

	backendWs.on('error', () => {
		socket.destroy();
	});
});

server.listen(PORT, HOST, () => {
	console.log(`Server listening on ${HOST}:${PORT}`);
});
