from pypiles.cards import Card
from pypiles.deck import StandardConfigs, prepare_game_cards


def test_prepare_game_cards():
    for i in range(
        StandardConfigs.MIN_NUM_PLAYERS, (StandardConfigs.MAX_NUM_PLAYERS + 1)
    ):
        center_pile, all_player_cards = prepare_game_cards(
            num_players=i,
            pile_size=StandardConfigs.PILE_SIZE,
            num_piles_per_player=StandardConfigs.NUM_PILES_PER_PLAYER,
        )

        ## -- test center pile
        assert isinstance(center_pile, list)
        assert len(center_pile) == StandardConfigs.PILE_SIZE
        assert all([isinstance(card, Card) for card in center_pile])

        ## -- test player cards
        assert isinstance(all_player_cards, list)
        assert len(all_player_cards) == i

        for individual_player_cards in all_player_cards:
            assert isinstance(individual_player_cards, list)
            assert len(individual_player_cards) == StandardConfigs.NUM_PILES_PER_PLAYER
            assert all([isinstance(pile, list) for pile in individual_player_cards])
            assert all(
                [
                    len(pile) == StandardConfigs.PILE_SIZE
                    for pile in individual_player_cards
                ]
            )

        ## -- test full deck
        flattened_player_cards = [i for sublist in all_player_cards for i in sublist]
        flattened_player_cards = [
            i for sublist in flattened_player_cards for i in sublist
        ]

        all_game_cards = center_pile + flattened_player_cards

        all_card_ids = [card.id for card in all_game_cards]
        assert len(set(all_card_ids)) == len(all_card_ids)
