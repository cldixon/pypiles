import asyncio
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


class GameConfig(TypedDict):
    num_players: int
    pile_size: int
    num_piles_per_player: int
    winning_score: int | None
    player_characters: list[str]


GamePhase = Literal["configuring", "running", "completed", "error"]


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

    def ensure_ray(self) -> None:
        if not self._ray_initialized:
            if not ray.is_initialized():
                ray.init(
                    ignore_reinit_error=True,
                    _temp_dir="/tmp/ray",
                )
            self._ray_initialized = True

    def create_game(self, config: GameConfig) -> str:
        game_id = str(uuid4())
        session = GameSession(game_id=game_id, config=config)
        self.sessions[game_id] = session
        return game_id

    def _setup_and_run_game(self, game_id: str) -> None:
        """Synchronous game execution. Sets up actors, runs game, collects results."""
        self.ensure_ray()
        session = self.sessions[game_id]
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
        initial_center = ray.get(session.center_pile.get_initial_cards.remote())
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

        # Run game
        session.phase = "running"
        try:
            ray.get(
                [
                    p.play.remote(
                        center_pile=session.center_pile,
                        game_status=session.game_status,
                    )
                    for p in session.players
                ]
            )

            # Collect events and final state
            session.events = ray.get(session.event_collector.get_events.remote())
            session.final_state = {
                "game_status": ray.get(
                    session.game_status.get_game_state.remote()
                ),
                "center_pile": ray.get(
                    session.center_pile.get_center_pile_state.remote()
                ),
                "players": [
                    ray.get(p.get_player_state.remote()) for p in session.players
                ],
            }
            session.phase = "completed"

        except Exception as e:
            session.phase = "error"
            session.error = str(e)
            try:
                session.events = ray.get(
                    session.event_collector.get_events.remote()
                )
            except Exception:
                pass

    async def run_game(self, game_id: str) -> None:
        """Async wrapper that runs the game in an executor to avoid blocking."""
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
