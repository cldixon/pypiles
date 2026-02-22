<script>
	import '../app.css';

	let { children } = $props();
</script>

<div class="app">
	<header>
		<div class="header-inner">
			<a href="/" class="logo">PyPiles</a>
			<span class="tagline">Concurrent Card Game Simulator</span>
		</div>
	</header>
	<main>
		{@render children()}
	</main>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	header {
		background: var(--bg-secondary);
		border-bottom: 1px solid var(--border);
		padding: 0.75rem 1.5rem;
	}

	.header-inner {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.logo {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--accent-light);
		letter-spacing: -0.02em;
	}

	.logo:hover {
		text-decoration: none;
		color: var(--accent);
	}

	.tagline {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	main {
		flex: 1;
		max-width: 1200px;
		width: 100%;
		margin: 0 auto;
		padding: 2rem 1.5rem;
	}
</style>
