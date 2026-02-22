import time
from typing import Literal, TypedDict

import ray

EventType = Literal[
    "game_started",
    "game_ended",
    "swap_requested",
    "swap_succeeded",
    "swap_failed",
    "pile_completed",
    "game_won",
    "center_pile_updated",
    "player_no_swap",
]


class GameEvent(TypedDict):
    seq: int
    timestamp: float
    event_type: EventType
    actor: str
    data: dict


@ray.remote
class EventCollector:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.events: list[GameEvent] = []
        self._seq = 0

    def push_event(self, event_type: EventType, actor: str, data: dict) -> None:
        self.events.append(
            GameEvent(
                seq=self._seq,
                timestamp=time.time(),
                event_type=event_type,
                actor=actor,
                data=data,
            )
        )
        self._seq += 1

    def get_events(self) -> list[GameEvent]:
        return self.events

    def get_event_count(self) -> int:
        return len(self.events)
