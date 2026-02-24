<script lang="ts">
	let { onplay }: { onplay: () => void } = $props();
</script>

<div class="backdrop" role="dialog" aria-modal="true" aria-label="Welcome to PyPiles">
	<div class="modal">
		<h1 class="title">PyPiles</h1>
		<p class="subtitle">A Concurrent Card Game Simulator</p>

		<div class="content">
			<section>
				<h2>The Game</h2>
				<p>
					Players compete to complete <strong>piles</strong> — groups of cards
					that share the same item across different colors. Each turn, players
					swap cards with a shared center pile, racing to be the first to
					complete all their piles.
				</p>
			</section>

			<section>
				<h2>Powered by Ray</h2>
				<p>
					Every player runs as an independent <strong>Ray actor</strong>,
					making swaps concurrently and competing for the center pile in real
					time. This isn't turn-based — it's a true concurrent simulation
					where timing and strategy both matter.
				</p>
			</section>

			<section>
				<h2>Choose Your Characters</h2>
				<p>
					Pick from different AI characters, each with their own swap
					strategy. Mix and match to see how Greedy Nathan fares against
					Random Rana or Cautious Carlo.
				</p>
			</section>
		</div>

		<button class="play-btn" onclick={onplay}>Play</button>
	</div>
</div>

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(15, 15, 26, 0.85);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
		padding: 1.5rem;
		animation: fadeIn 0.3s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 2.5rem;
		max-width: 540px;
		width: 100%;
		text-align: center;
		animation: slideUp 0.35s ease-out;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.title {
		font-size: 2.5rem;
		font-weight: 800;
		color: var(--accent-light);
		letter-spacing: -0.03em;
		margin-bottom: 0.25rem;
	}

	.subtitle {
		font-size: 1rem;
		color: var(--text-muted);
		margin-bottom: 2rem;
	}

	.content {
		text-align: left;
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		margin-bottom: 2rem;
	}

	section h2 {
		font-size: 0.9rem;
		font-weight: 700;
		color: var(--accent-light);
		margin-bottom: 0.3rem;
	}

	section p {
		font-size: 0.85rem;
		color: var(--text-secondary);
		line-height: 1.5;
	}

	section p strong {
		color: var(--text-primary);
	}

	.play-btn {
		background: var(--accent);
		color: white;
		border: none;
		padding: 0.875rem 3rem;
		border-radius: var(--radius);
		font-size: 1.1rem;
		font-weight: 700;
		letter-spacing: 0.02em;
		transition: background 0.2s, transform 0.15s;
	}

	.play-btn:hover {
		background: var(--accent-light);
		transform: translateY(-1px);
	}
</style>
