import asyncio
import logging
import os
import threading
from typing import Literal, TypedDict
from uuid import uuid4

import ray

from pypiles.actors import (
    CenterPile,
    CenterPileState,
    EventCollector,
    GameEvent,
    GameStatus,
    GameStatusState,
    Player,
    PlayerState,
)
from pypiles.characters import CHARACTER_REGISTRY, get_character
from pypiles.deck import prepare_game_cards

logger = logging.getLogger(__name__)


class GameConfig(TypedDict):
    num_players: int
    pile_size: int
    num_piles_per_player: int
    winning_score: int | None
    player_characters: list[str]


GamePhase = Literal["configuring", "running", "completed", "error"]

_MAX_SESSIONS = 50


class GameSession:
    """Holds all state for a single game instance."""

    def __init__(self, game_id: str, config: GameConfig):
        self.game_id = game_id
        self.config = config
        self.phase: GamePhase = "configuring"
        self.event_collector: ray.actor.ActorHandle | None = None
        self.players: list[ray.actor.ActorHandle] = []
        self.center_pile: ray.actor.ActorHandle | None = None
        self.game_status: ray.actor.ActorHandle | None = None
        self.events: list[GameEvent] = []
        self.initial_state: dict | None = None
        self.final_state: dict | None = None
        self.error: str | None = None


class GameManager:
    """Manages game lifecycle. One instance per application."""

    def __init__(self):
        self.sessions: dict[str, GameSession] = {}
        self._ray_initialized = False
        self._game_lock = threading.Lock()

    def ensure_ray(self) -> None:
        """Initialize Ray if needed, or reinitialize if it has crashed."""
        if self._ray_initialized and ray.is_initialized():
            return

        # Ray was initialized but is no longer running -- clean up
        if self._ray_initialized and not ray.is_initialized():
            try:
                ray.shutdown()
            except Exception:
                pass
            self._ray_initialized = False

        if not ray.is_initialized():
            num_cpus = int(os.environ.get("RAY_NUM_CPUS", 2))
            object_store_memory = int(
                os.environ.get("RAY_OBJECT_STORE_MEMORY", 100_000_000)
            )
            ray.init(
                num_cpus=num_cpus,
                ignore_reinit_error=True,
                _temp_dir="/tmp/ray",
                include_dashboard=False,
                object_store_memory=object_store_memory,
            )
        self._ray_initialized = True

    def create_game(self, config: GameConfig) -> str:
        self._prune_old_sessions()
        game_id = str(uuid4())
        session = GameSession(game_id=game_id, config=config)
        self.sessions[game_id] = session
        return game_id

    def _prune_old_sessions(self) -> None:
        """Remove oldest completed/error sessions if over the limit."""
        if len(self.sessions) <= _MAX_SESSIONS:
            return
        removable = [
            gid
            for gid, s in self.sessions.items()
            if s.phase in ("completed", "error")
        ]
        to_remove = len(self.sessions) - _MAX_SESSIONS
        for gid in removable[:to_remove]:
            del self.sessions[gid]

    def _cleanup_actors(self, session: GameSession) -> None:
        """Kill all Ray actors for a game session to free resources."""
        actors = [session.event_collector, session.game_status, session.center_pile]
        actors.extend(session.players)
        for handle in actors:
            if handle is not None:
                try:
                    ray.kill(handle)
                except Exception:
                    pass
        session.event_collector = None
        session.game_status = None
        session.center_pile = None
        session.players = []

    def _setup_game(self, game_id: str) -> None:
        """Create actors and capture initial state. Sets phase to 'running'."""
        session = self.sessions[game_id]

        with self._game_lock:
            self.ensure_ray()
            config = session.config

            num_piles = config["num_piles_per_player"]
            winning_score = (
                config["winning_score"] if config["winning_score"] else num_piles
            )

            center_pile_cards, player_cards = prepare_game_cards(
                num_players=config["num_players"],
                pile_size=config["pile_size"],
                num_piles_per_player=num_piles,
            )

            # Create event collector
            session.event_collector = EventCollector.remote(game_id=game_id)

            # Create actors with event_collector
            session.game_status = GameStatus.remote(
                winning_score=winning_score,
                event_collector=session.event_collector,
            )
            session.center_pile = CenterPile.remote(
                cards=center_pile_cards,
                event_collector=session.event_collector,
            )

            session.players = [
                Player.remote(
                    id=f"P{i+1}",
                    cards=player_piles,
                    strategy=get_character(char_id).strategy_cls(),
                    event_collector=session.event_collector,
                )
                for i, (player_piles, char_id) in enumerate(
                    zip(player_cards, config["player_characters"])
                )
            ]

            # Capture initial state
            initial_center = ray.get(
                session.center_pile.get_initial_cards.remote()
            )
            initial_players = [
                ray.get(p.get_initial_state.remote()) for p in session.players
            ]

            session.initial_state = {
                "config": config,
                "center_pile": initial_center,
                "players": initial_players,
            }

            # Emit game_started event
            ray.get(
                session.event_collector.push_event.remote(
                    event_type="game_started",
                    actor="GS",
                    data={"game_id": game_id, "config": config},
                )
            )

            session.phase = "running"

    def _run_players(self, game_id: str) -> None:
        """Start player gameplay, wait for completion, collect results.

        Must be called after _setup_game. Sets phase to 'completed' or 'error'.
        """
        session = self.sessions[game_id]
        config = session.config

        try:
            # Scale timeout with player count: 60s base + 15s per player beyond 2
            num_players = config["num_players"]
            game_timeout = 60 + max(0, num_players - 2) * 15

            ray.get(
                [
                    p.play.remote(
                        center_pile=session.center_pile,
                        game_status=session.game_status,
                    )
                    for p in session.players
                ],
                timeout=game_timeout,
            )

            # Collect events and final state
            session.events = ray.get(
                session.event_collector.get_events.remote()
            )
            duration_ms = 0.0
            if len(session.events) >= 2:
                duration_ms = (
                    session.events[-1]["timestamp"]
                    - session.events[0]["timestamp"]
                ) * 1000
            session.final_state = {
                "game_status": ray.get(
                    session.game_status.get_game_state.remote()
                ),
                "center_pile": ray.get(
                    session.center_pile.get_center_pile_state.remote()
                ),
                "players": [
                    ray.get(p.get_player_state.remote())
                    for p in session.players
                ],
                "duration_ms": duration_ms,
                "total_events": len(session.events),
            }
            session.phase = "completed"

        except ray.exceptions.GetTimeoutError:
            # Game exceeded time limit -- force stop and collect what we have
            try:
                ray.get(session.game_status.end_game.remote())
            except Exception:
                pass
            session.phase = "error"
            session.error = f"Game timed out (exceeded {game_timeout}s). This can happen when player strategies deadlock."
            try:
                session.events = ray.get(
                    session.event_collector.get_events.remote()
                )
            except Exception:
                pass

        except Exception as e:
            session.phase = "error"
            session.error = str(e)
            if not ray.is_initialized():
                self._ray_initialized = False
            try:
                session.events = ray.get(
                    session.event_collector.get_events.remote()
                )
            except Exception:
                pass

        finally:
            self._cleanup_actors(session)

    def _setup_and_run_game(self, game_id: str) -> None:
        """Synchronous game execution. Sets up actors, runs game, collects results."""
        self._setup_game(game_id)
        self._run_players(game_id)

    async def setup_game(self, game_id: str) -> None:
        """Async: create actors and initial state (runs in executor)."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._setup_game, game_id)

    async def run_players(self, game_id: str) -> None:
        """Async: start gameplay and wait for completion (runs in executor)."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._run_players, game_id)

    async def run_game(self, game_id: str) -> None:
        """Async wrapper that runs setup + gameplay in an executor."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._setup_and_run_game, game_id)

    def run_game_sync(self, game_id: str) -> None:
        """Synchronous version for CLI/testing use."""
        self._setup_and_run_game(game_id)

    def get_session(self, game_id: str) -> GameSession | None:
        return self.sessions.get(game_id)

    def list_games(self) -> list[dict]:
        return [
            {"game_id": s.game_id, "phase": s.phase, "config": s.config}
            for s in self.sessions.values()
        ]
