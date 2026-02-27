"""Database logging for game usage metrics.

Uses Neon DB (serverless Postgres) via asyncpg. All operations are no-ops
when DATABASE_URL is not set, allowing the app to run without a database.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

_pool = None

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    config JSONB NOT NULL,
    phase TEXT NOT NULL DEFAULT 'configuring',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms DOUBLE PRECISION,
    total_events INTEGER DEFAULT 0,
    winner TEXT,
    error TEXT
);

CREATE TABLE IF NOT EXISTS game_player_results (
    id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL REFERENCES games(id),
    player_id TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    num_requests INTEGER NOT NULL DEFAULT 0,
    num_swaps INTEGER NOT NULL DEFAULT 0,
    remaining_piles INTEGER NOT NULL DEFAULT 0,
    completed_piles INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS request_log (
    id SERIAL PRIMARY KEY,
    game_id TEXT,
    action TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


async def init_db() -> None:
    """Initialize the connection pool and create tables if needed."""
    global _pool
    if not DATABASE_URL:
        logger.info("DATABASE_URL not set — database logging disabled")
        return

    import asyncpg

    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with _pool.acquire() as conn:
        await conn.execute(SCHEMA_SQL)
    logger.info("Database initialized")


async def close_db() -> None:
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def log_game_created(
    game_id: str,
    config: dict,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Log a new game creation."""
    if not _pool:
        return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO games (id, config) VALUES ($1, $2)",
                game_id,
                json.dumps(config),
            )
            await conn.execute(
                "INSERT INTO request_log (game_id, action, user_agent, ip_address) VALUES ($1, $2, $3, $4)",
                game_id,
                "game_created",
                user_agent,
                ip_address,
            )
    except Exception:
        logger.exception("Failed to log game creation for %s", game_id)


async def log_game_completed(
    game_id: str,
    phase: str,
    duration_ms: float,
    total_events: int,
    winner: str | None,
    error: str | None,
    players: list[dict],
) -> None:
    """Log game completion with final results."""
    if not _pool:
        return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """UPDATE games
                   SET phase = $2, completed_at = NOW(), duration_ms = $3,
                       total_events = $4, winner = $5, error = $6
                   WHERE id = $1""",
                game_id,
                phase,
                duration_ms,
                total_events,
                winner,
                error,
            )
            for p in players:
                await conn.execute(
                    """INSERT INTO game_player_results
                       (game_id, player_id, score, num_requests, num_swaps,
                        remaining_piles, completed_piles)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    game_id,
                    p["id"],
                    p["score"],
                    p["metrics"]["num_requests"],
                    p["metrics"]["num_swaps"],
                    len(p["remaining"]),
                    len(p["completed"]),
                )
    except Exception:
        logger.exception("Failed to log game completion for %s", game_id)
