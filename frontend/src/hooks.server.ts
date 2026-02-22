import type { Handle } from '@sveltejs/kit';

const API_INTERNAL_URL = (process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000').trim();

export const handle: Handle = async ({ event, resolve }) => {
	const { pathname, search } = event.url;

	if (pathname.startsWith('/api/')) {
		const targetUrl = `${API_INTERNAL_URL}${pathname}${search}`;

		const headers = new Headers(event.request.headers);
		headers.delete('host');

		try {
			const response = await fetch(targetUrl, {
				method: event.request.method,
				headers,
				body:
					event.request.method !== 'GET' && event.request.method !== 'HEAD'
						? event.request.body
						: undefined,
				// @ts-expect-error Node fetch supports duplex for streaming bodies
				duplex: 'half'
			});

			return new Response(response.body, {
				status: response.status,
				statusText: response.statusText,
				headers: response.headers
			});
		} catch (err) {
			const message = err instanceof Error ? err.message : 'Unknown error';
			console.error(`API proxy error for ${targetUrl}: ${message}`);
			return new Response(
				JSON.stringify({
					detail: `Backend unavailable: ${message}. Ensure the API service is running and API_INTERNAL_URL is set correctly (current: ${API_INTERNAL_URL}).`
				}),
				{
					status: 502,
					headers: { 'Content-Type': 'application/json' }
				}
			);
		}
	}

	return resolve(event);
};
