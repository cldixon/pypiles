from typing import Tuple, TypedDict

from pypiles.cards import Card


class SwapRequest(TypedDict):
    target: Tuple[int, Card]
    swap: Tuple[int, int, Card]

class SwapResponse(TypedDict):
    completed: bool
    return_card: Card | None
