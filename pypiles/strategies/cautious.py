import random

from pypiles.cards import Card
from pypiles.scoring import get_pile_status
from pypiles.swap import SwapRequest


class CautiousSwapper:
    """Only makes a move when there's a guaranteed item match
    in the center pile. Never speculates or does random swaps."""

    def find_swap(
        self, player_cards: list[list[Card]], center_pile: list[Card]
    ) -> SwapRequest | None:
        center_pile_status = get_pile_status(center_pile)

        # Shuffle pile order so we don't always favor the first pile
        index_order = random.sample(range(len(player_cards)), k=len(player_cards))

        for pile_idx in index_order:
            card_pile = player_cards[pile_idx]
            player_pile_status = get_pile_status(card_pile)

            if player_pile_status["state"] == "4*":
                continue

            # Only swap if we find an exact item match in the center pile
            for item, group_cards in player_pile_status["groups"].items():
                if item in center_pile_status["groups"]:
                    # Found a match — take it
                    position, target_card = center_pile_status["groups"][item][0]

                    # Send a card from a different item group
                    other_cards = [
                        (idx, card)
                        for other_item, cards in player_pile_status["groups"].items()
                        if other_item != item
                        for idx, card in cards
                    ]
                    if not other_cards:
                        continue

                    swap_idx, swap_card = random.choice(other_cards)
                    return SwapRequest(
                        target=(position, target_card),
                        swap=(pile_idx, swap_idx, swap_card),
                    )

        # No guaranteed match found — do nothing
        return None
