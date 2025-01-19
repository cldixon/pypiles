import random
import time
from pathlib import Path
from typing import TypedDict

import ray

from pypiles.cards import Card
from pypiles.logger import setup_logger
from pypiles.scoring import get_pile_status
from pypiles.strategies.protocol import SwapStrategy


class ActivityMetrics(TypedDict):
    num_requests: int
    num_swaps: int


def initialize_activity_metrics() -> ActivityMetrics:
    return ActivityMetrics(num_requests=0, num_swaps=0)


class PlayerState(TypedDict):
    id: str
    remaining: list[list[str]]
    completed: list[list[str]]
    metrics: ActivityMetrics
    score: int


@ray.remote
class Player:
    def __init__(
        self,
        cards: list[list[Card]],
        strategy: SwapStrategy,
        id: str | None = None,
        log_file: Path | str | None = None,
    ):
        self.cards = cards
        self.completed = []
        self.strategy = strategy
        self.metrics = initialize_activity_metrics()
        self.id = id if id is not None else "P0"

        self.logger = setup_logger(name=f"({self.id})", log_file=log_file)

    def __repr__(self) -> str:
        score = len(self.completed)
        return f"{self.__class__.__name__}(id={self.id}, score={score})"

    def view_cards(self) -> list[list[Card]]:
        return self.cards

    def view_completed(self) -> list[list[Card]]:
        return self.completed

    def update_card(self, pile_idx: int, card_idx: int, card: Card) -> None:
        self.cards[pile_idx][card_idx] = card

    def play(
        self,
        center_pile: ray.actor.ActorHandle,
        game_status: ray.actor.ActorHandle,
        add_time_delay: bool = False,
    ):
        while True:
            if add_time_delay:
                time.sleep(random.uniform(0.5, 0.99))

            center_pile_cards = ray.get(center_pile.view_cards.remote())

            swap_request = self.strategy.find_swap(
                player_cards=self.cards, center_pile=center_pile_cards
            )

            # check game is still active before submitting swap request to center pile
            if not ray.get(game_status.is_active.remote()):
                return

            if swap_request:
                self.logger.info(
                    f"REQUEST | player card {str(swap_request['swap'][2])} for (CP) card {str(swap_request['target'][1])}"
                )

                success, new_card = ray.get(
                    center_pile.swap_card.remote(
                        position=swap_request["target"][0],
                        target_card=swap_request["target"][1],
                        replacement_card=swap_request["swap"][2],
                    )
                )

                self.metrics["num_requests"] += 1

                if success:
                    self.logger.info(
                        f"SWAP | added {str(new_card)} @ Pos[{swap_request['swap'][0]}, {swap_request['swap'][1]}] and sent {str(swap_request['swap'][2])} to (CP)"
                    )
                    self.metrics["num_swaps"] += 1
                    self.update_card(
                        pile_idx=swap_request["swap"][0],
                        card_idx=swap_request["swap"][1],
                        card=new_card,
                    )

                    # check if pile is completed after swap
                    pile_cards = self.cards[swap_request["swap"][0]]

                    pile_status = get_pile_status(pile_cards)
                    if pile_status["complete"]:
                        self.logger.info(
                            f"({self.id}) completed pile @ Pos[{swap_request['swap'][0]}]"
                        )
                        self.completed.append(pile_cards)
                        self.cards.pop(swap_request["swap"][0])
            else:
                self.logger.info(f"({self.id}) did not generate a swap request")

            if len(self.completed) >= 1:
                victory = ray.get(
                    game_status.submit_for_win.remote(self.id, self.completed)
                )
                if victory:
                    self.logger.info(f"{self.id}: Yay! We have won!")
                    return

    def get_player_state(self) -> PlayerState:
        return PlayerState(
            id=self.id,
            remaining=[[card.id for card in pile] for pile in self.cards],
            completed=[[card.id for card in pile] for pile in self.completed],
            metrics=self.metrics,
            score=len(self.completed),
        )
