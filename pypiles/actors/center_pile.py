from pathlib import Path
from typing import Tuple, TypedDict

import ray

from pypiles.cards import Card
from pypiles.logger import setup_logger
from pypiles.logic import cards_are_identical


class ActivityMetrics(TypedDict):
    num_views: int
    num_requests: int
    num_swaps: int


class CenterPileState(TypedDict):
    cards: list[str]
    metrics: ActivityMetrics


def initialize_activity_metrics() -> ActivityMetrics:
    return ActivityMetrics(num_views=0, num_requests=0, num_swaps=0)


@ray.remote
class CenterPile:
    def __init__(self, cards: list[Card], log_file: Path | str | None = None):
        self.cards = [(card.id, card) for card in cards]
        self.card_id_set = {card.id for card in cards}
        self.metrics = initialize_activity_metrics()

        self.logger = setup_logger(name="(CP)", log_file=log_file)

    def view_cards(self) -> list[Card]:
        self.metrics["num_views"] += 1
        return [card for _, card in self.cards]

    def swap_card(
        self, position: int, target_card: Card, replacement_card: Card
    ) -> Tuple[bool, Card | None]:
        if replacement_card.id in self.card_id_set:
            raise ValueError(
                f"Game is in an invalid state with duplicate cards(s). A user has submitted a card to swap ({replacement_card}) which is also in center pile."
            )

        self.metrics["num_requests"] += 1

        # check if requested card is stil available in specified position
        if not cards_are_identical(self.cards[position][1], target_card):
            return False, None

        # pull out card from center pile; will return to user
        old_card_id, old_card = self.cards[position]

        # insert new card into center pile
        self.cards[position] = (replacement_card.id, replacement_card)

        # update set object (use for lookups)
        self.card_id_set.remove(old_card_id)
        self.card_id_set.add(replacement_card.id)

        self.logger.info(
            f"(CP) accepted {str(replacement_card)} @ Pos[{position}] and returned {str(old_card)} to player (P?)"
        )
        self.metrics["num_swaps"] += 1
        return True, old_card

    def get_center_pile_state(self) -> CenterPileState:
        return CenterPileState(
            cards=[card.id for card in self.view_cards()], metrics=self.metrics
        )
