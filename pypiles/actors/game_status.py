import time
from datetime import datetime
from typing import TypedDict

import ray

from pypiles.cards import Card


class GameStatusState(TypedDict):
    active: bool
    start_time: str
    end_time: str | None
    winner: str | None


@ray.remote
class GameStatus:
    def __init__(self, winning_score: int):
        self.winning_score = winning_score
        self.active = True
        self.start_time = time.time()
        self.end_time = None
        self.winner = None

    def is_active(self) -> bool:
        return self.active

    def end_game(self) -> None:
        self.active = False

    def submit_for_win(self, player_id: str, completed: list[list[Card]]) -> bool:
        if len(completed) >= self.winning_score:
            self.active = False
            self.end_time = time.time()
            self.winner = player_id
            return True

        return False

    def get_game_state(self) -> GameStatusState:
        return GameStatusState(
            active=self.active,
            start_time=datetime.utcfromtimestamp(self.start_time).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
            end_time=datetime.utcfromtimestamp(self.end_time).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            if self.end_time is not None
            else None,
            winner=self.winner,
        )
