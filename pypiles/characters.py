from dataclasses import dataclass

from pypiles.strategies.cautious import CautiousSwapper
from pypiles.strategies.greedy import GreedySwapper
from pypiles.strategies.random import RandomSwapper


@dataclass(frozen=True)
class Character:
    id: str
    name: str
    description: str
    strategy_cls: type


CHARACTER_REGISTRY: dict[str, Character] = {}

_CHARACTERS = [
    Character(
        id="greedy-nathan",
        name="Greedy Nathan",
        description="Always hunts for the best match, never backs down from a good pile",
        strategy_cls=GreedySwapper,
    ),
    Character(
        id="random-rana",
        name="Random Rana",
        description="Swaps on vibes alone — chaos is a strategy too",
        strategy_cls=RandomSwapper,
    ),
    Character(
        id="cautious-carlo",
        name="Cautious Carlo",
        description="Only makes a move when the match is guaranteed",
        strategy_cls=CautiousSwapper,
    ),
]

for _c in _CHARACTERS:
    CHARACTER_REGISTRY[_c.id] = _c

DEFAULT_CHARACTER_ID = "greedy-nathan"

_CHARACTER_IDS = list(CHARACTER_REGISTRY.keys())


def assign_default_characters(num_players: int) -> list[str]:
    """Distribute distinct characters across players, cycling if needed."""
    return [_CHARACTER_IDS[i % len(_CHARACTER_IDS)] for i in range(num_players)]


def get_character(character_id: str) -> Character:
    """Look up a character by ID. Raises KeyError if not found."""
    if character_id not in CHARACTER_REGISTRY:
        available = list(CHARACTER_REGISTRY.keys())
        raise KeyError(
            f"Unknown character '{character_id}'. Available: {available}"
        )
    return CHARACTER_REGISTRY[character_id]
