import random

from pypiles.cards import Card
from pypiles.scoring import get_pile_status
from pypiles.swap import SwapRequest


# After this many consecutive "no match" rounds, fall back to a random swap
# to break potential deadlocks (e.g. two cautious players facing each other).
_PATIENCE = 5


class CautiousSwapper:
    """Only makes a move when there's a guaranteed item match
    in the center pile. Falls back to a random swap after several
    consecutive failures to avoid deadlocks."""

    def __init__(self):
        self._misses = 0

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
                    self._misses = 0
                    return SwapRequest(
                        target=(position, target_card),
                        swap=(pile_idx, swap_idx, swap_card),
                    )

        # No guaranteed match found
        self._misses += 1

        if self._misses >= _PATIENCE:
            # Deadlock breaker: send a minority card to shake up the center pile
            self._misses = 0
            return self._fallback_swap(player_cards, center_pile, index_order)

        return None

    @staticmethod
    def _fallback_swap(
        player_cards: list[list[Card]],
        center_pile: list[Card],
        index_order: list[int],
    ) -> SwapRequest | None:
        """Pick a random minority card from a random pile and swap it with
        a random center-pile card. This changes the center-pile composition
        so future cautious scans can find matches again."""
        for pile_idx in index_order:
            pile = player_cards[pile_idx]
            status = get_pile_status(pile)

            if status["state"] == "4*":
                continue

            # Prefer sending a minority-item card (least useful to us)
            minority_cards = []
            if status["max_item"] and isinstance(status["max_item"], str):
                for other_item, cards in status["groups"].items():
                    if other_item != status["max_item"]:
                        minority_cards.extend(cards)
            if not minority_cards:
                # 2-2 or 1-1-1-1 — just pick any card
                minority_cards = [
                    (idx, card) for idx, card in enumerate(pile)
                ]

            swap_idx, swap_card = random.choice(minority_cards)
            position = random.randint(0, len(center_pile) - 1)
            target_card = center_pile[position]
            return SwapRequest(
                target=(position, target_card),
                swap=(pile_idx, swap_idx, swap_card),
            )

        return None
