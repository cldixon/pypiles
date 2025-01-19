from typing import Literal, Tuple, TypedDict

from pypiles.cards import Card

ItemGroups = dict[str, list[Tuple[int, Card]]]


def group_cards_by_item(cards: list[Card]) -> ItemGroups:
    item_count = {}
    for idx, card in enumerate(cards):
        if card.item in item_count:
            item_count[card.item].append((idx, card))
        else:
            item_count[card.item] = [(idx, card)]
    return item_count


## -- all possible states a card pile can be in when grouped by item
PileState = Literal["1-1-1-1", "2-1-1", "2-2", "3-1", "4*"]


class PileStatus(TypedDict):
    groups: ItemGroups
    items: set
    max_count: int
    max_item: str | list[str] | None
    state: PileState
    complete: bool


def get_pile_status(cards: list[Card]) -> PileStatus:
    item_groups = group_cards_by_item(cards)
    item_set = set(item_groups.keys())
    max_count = max([len(cards) for cards in item_groups.values()])

    if max_count == 1:
        max_item = None
    elif max_count == 2 and len(item_groups) == 2:
        max_item = list(item_groups.keys())
    else:
        max_item = max(item_groups, key=lambda x: len(item_groups[x]))

    # determine pile state for strategy algorithms and scoring
    if max_count == 1:
        state = "1-1-1-1"
    elif max_count == 2 and len(item_groups) == 3:
        state = "2-1-1"
    elif max_count == 2 and len(item_groups) == 2:
        state = "2-2"
    elif max_count == 3:
        state = "3-1"
    elif max_count == 4:
        state = "4*"
    else:
        raise ValueError(
            f"Max count of {max_count} and number of item groups {len(item_groups)} is an unexpected state."
        )

    return PileStatus(
        groups=item_groups,
        items=item_set,
        max_count=max_count,
        max_item=max_item,
        state=state,
        complete=True if state == "4*" else False,
    )
