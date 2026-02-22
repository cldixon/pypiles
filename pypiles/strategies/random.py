import random

from pypiles.cards import Card
from pypiles.swap import SwapRequest


class RandomSwapper:
    """Swaps on vibes alone — picks a random card from a random pile
    and targets a random card in the center pile."""

    def find_swap(
        self, player_cards: list[list[Card]], center_pile: list[Card]
    ) -> SwapRequest | None:
        if not player_cards or not center_pile:
            return None

        # Pick a random pile that still has cards
        valid_piles = [(i, pile) for i, pile in enumerate(player_cards) if pile]
        if not valid_piles:
            return None

        pile_idx, pile = random.choice(valid_piles)
        swap_idx = random.randint(0, len(pile) - 1)
        swap_card = pile[swap_idx]

        position = random.randint(0, len(center_pile) - 1)
        target_card = center_pile[position]

        return SwapRequest(
            target=(position, target_card),
            swap=(pile_idx, swap_idx, swap_card),
        )
