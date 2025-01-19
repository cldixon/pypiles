import random
from typing import Tuple

from pypiles.cards import Card, create_card
from pypiles.colors import get_colors
from pypiles.items import get_items


class StandardConfigs:
    MIN_NUM_PLAYERS = 2
    MAX_NUM_PLAYERS = 8
    NUM_PILES_PER_PLAYER = 6
    PILE_SIZE = 4


def _batch_cards(cards: list, batch_size: int):
    for i in range(0, len(cards), batch_size):
        yield cards[i : (i + batch_size)]


def batch_cards(cards: list, batch_size: int) -> list:
    return list(_batch_cards(cards, batch_size))


def prepare_game_cards(
    num_players: int,
    num_piles_per_player: int = StandardConfigs.NUM_PILES_PER_PLAYER,
    pile_size: int = StandardConfigs.PILE_SIZE,
) -> Tuple[list[Card], list[list[list[Card]]]]:
    assert (
        StandardConfigs.MIN_NUM_PLAYERS
        <= num_players
        <= StandardConfigs.MAX_NUM_PLAYERS
    ), f"Selected number of player {num_players} is not valid. Game allows 2-8 players."

    # determine number of items needed based on game configs
    num_items_required = (
        num_players * num_piles_per_player
    ) + 1  # +1 is for center pile

    # create game cards with number of item sets
    game_cards = [
        [
            create_card(color=color, item=item)
            for color in random.sample(get_colors(), k=pile_size)
        ]
        for item in random.sample(get_items(), k=num_items_required)
    ]

    # flatten nested list, then shuffle
    game_cards = [i for sublist in game_cards for i in sublist]
    game_cards = random.sample(game_cards, k=len(game_cards))

    # check total number of game cards is correct
    assert len(game_cards) == (num_players * num_piles_per_player * pile_size) + (
        1 * pile_size
    )

    # separate center pile
    center_pile = game_cards[:pile_size]
    remaining_cards = game_cards[pile_size:]

    # separate individual players' cards (players are allotted n piles of x size)
    player_cards = batch_cards(
        remaining_cards, batch_size=(num_piles_per_player * pile_size)
    )
    assert len(player_cards) == num_players

    # organize player cards into piles
    player_card_piles = [
        batch_cards(player_batch, batch_size=pile_size) for player_batch in player_cards
    ]

    assert all(
        [
            len(player_batch) == num_piles_per_player
            for player_batch in player_card_piles
        ]
    )

    return center_pile, player_card_piles
