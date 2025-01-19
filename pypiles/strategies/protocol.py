from typing import Protocol

from pypiles.cards import Card
from pypiles.swap import SwapRequest


class SwapStrategy(Protocol):
    def find_swap(
        self, player_cards: list[list[Card]], center_pile: list[Card]
    ) -> SwapRequest | None: ...
