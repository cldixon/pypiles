# PyPiles

**Play it now: [pypiles.cldixon.com](https://pypiles.cldixon.com)**

PyPiles is a real-time card game built entirely on [Ray](https://www.ray.io/) actors. Players race to complete piles of matching cards by swapping with a shared center pile — and every player - even the center pile - runs as an independent, concurrent actor in a distributed system.

---

## Why Ray?

Ray is a distributed computing framework typically used for ML workloads, data pipelines, and scaling Python across clusters. But its actor model is a clean fit for any system where independent agents need to coordinate over shared state — like a multiplayer card game.

PyPiles uses Ray to model each player, the center pile, game status tracking, and event collection as isolated actors that communicate through remote method calls. There are no locks, no shared memory, and no threading primitives. Instead, concurrency emerges naturally from Ray's actor isolation and message-passing semantics.

### The Actor Architecture

Every game spawns a set of Ray actors that run concurrently:

```
Player 1  ──┐
Player 2  ──┤──▶  CenterPile  ──▶  GameStatus
Player 3  ──┤        ▲
Player 4  ──┘        │
                EventCollector
```

- **`Player`** — One actor per player. Runs a continuous game loop: view the center pile, compute a swap using its assigned strategy, submit the swap request, update local state. Each player operates independently and in parallel.
- **`CenterPile`** — The single shared resource. Validates swap requests using optimistic concurrency — if the target card has already been swapped by another player, the request fails. No locks involved; just position-based validation.
- **`GameStatus`** — Tracks whether the game is still active and determines the winner when a player completes enough piles.
- **`EventCollector`** — Aggregates all game events (swap requests, successes, failures, pile completions) into a single ordered stream for the frontend to consume.

### Optimistic Concurrency (No Locks)

When a player wants to swap a card, they specify both the *position* and the *exact card* they expect to find there. If another player swapped that card out first, the request simply fails — no blocking, no retries at the actor level. The player loops back, views the updated center pile, and tries again. This creates natural race conditions that make every game play out differently.

### Pluggable Strategies

Each player actor is assigned a `SwapStrategy` — a Python Protocol that determines how the player decides which card to swap. Three strategies ship with the game:

| Character | Strategy | Behavior |
|---|---|---|
| **Greedy Nathan** | `GreedySwapper` | Always hunts for the best match, never backs down from a good pile |
| **Random Rana** | `RandomSwapper` | Swaps on vibes alone — chaos is a strategy too |
| **Cautious Carlo** | `CautiousSwapper` | Only makes a move when the match is guaranteed |

The strategy protocol is simple to implement, making it easy to experiment with new approaches:

```python
class SwapStrategy(Protocol):
    def find_swap(
        self, player_cards: list[list[Card]], center_pile: list[Card]
    ) -> SwapRequest | None: ...
```

### Event Sourcing for the Frontend

The entire game state is reconstructable from events. The `EventCollector` actor records every swap request, success, failure, and pile completion. The frontend doesn't poll for state snapshots — it derives the full game board from the event stream in real time. This same mechanism powers both live game streaming and post-game replay.

---

## The Game

**Cards** are defined by a color and a clothing item (e.g. `red::hoody`, `blue::cargo-pants`). Each item exists in 4 colors, and there are 50 items in the deck.

**Setup**: Each player receives a configurable number of piles, each containing 4 cards. One center pile is placed in the middle as the shared swap source.

**Goal**: Complete your piles. A pile is complete when all 4 cards are the same item (one per color). First player to finish all their piles wins.

**Gameplay**: All players act simultaneously. On each turn a player views the center pile, picks a card they want, and offers one of their own in exchange. If the center pile card hasn't been taken by someone else, the swap succeeds. If it has — tough luck, try again.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Concurrency | Ray (distributed actor framework) |
| Backend API | FastAPI + Uvicorn |
| Real-time | WebSockets |
| Frontend | SvelteKit (Svelte 5) |
| Database | PostgreSQL via asyncpg (optional, for game logging) |
| Package management | uv |
| Deployment | Docker on Railway |

---

## Local Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Install dependencies

```bash
uv sync
```

### Run the game from the CLI

The simplest way to run a game locally — no server, no frontend. Spins up Ray actors, plays a full game, and saves the final state to `logs/`.

```bash
uv run python driver.py
```

### Run the server

```bash
uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Run tests

```bash
uv run pytest tests/
```
