from itertools import combinations

from pypiles.cards import Card


def cards_are_identical(a: Card, b: Card) -> bool:
    return (a.color == b.color) and (a.item == b.item)

def cards_have_matching_item(a: Card, b: Card) -> bool:
    assert not cards_are_identical(a, b), f"Two provided cards ({str(a)} and {str(b)}) are identical. This is an invalid state."

    return a.item == b.item


def center_pile_in_valid_state(cards: list[Card]) -> bool:
    return all([not cards_are_identical(a, b) for a, b in combinations(cards, r=2)])
