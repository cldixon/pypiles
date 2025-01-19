import random

from pypiles.cards import Card
from pypiles.scoring import get_pile_status
from pypiles.swap import SwapRequest

## NOTE: This algorithm is complete improv; lol.
## Main Strategy: once a pile count reaches 2-2 or 3-1
## the strategy won't allow to go backward


class GreedySwapper:
    def __init__(self):
        self.whatami = "I am the Greedy Swapper"

    def find_swap(
        self, player_cards: list[list[Card]], center_pile: list[Card]
    ) -> SwapRequest | None:
        center_pile_status = get_pile_status(center_pile)

        # FIXME: create order based on scores
        index_order = random.sample(range(len(player_cards)), k=len(player_cards))

        for pile_idx in index_order:
            card_pile = player_cards[pile_idx]

            # get breakdown of pile by items
            player_pile_status = get_pile_status(card_pile)

            # saerch for swap candidates by item count criteria...
            if (
                player_pile_status["state"] == "1-1-1-1"
                or player_pile_status["state"] == "2-2"
            ):
                # no advantage either way, look for match in center pile
                for item_match, group_cards in player_pile_status["groups"].items():
                    if item_match in center_pile_status["groups"]:
                        # identify center pile position/card to target
                        position, target_card = center_pile_status["groups"][
                            item_match
                        ][0]

                        # determine which current pile card to send as swap
                        other_item_groups = [
                            group_cards
                            for other_item, group_cards in player_pile_status[
                                "groups"
                            ].items()
                            if other_item != item_match
                        ]
                        other_cards = [
                            i for sublist in other_item_groups for i in sublist
                        ]
                        # take random card from one of the other item groups
                        swap_idx, swap_card = random.choice(other_cards)
                        return SwapRequest(
                            target=(position, target_card),
                            swap=(pile_idx, swap_idx, swap_card),
                        )

                # take random card and make swap request
                swap_idx = random.randint(0, (len(card_pile) - 1))
                swap_card = card_pile[swap_idx]

                # choose random card in center pile to target
                if center_pile_status["state"] == "1-1-1-1":
                    position = random.randint(0, (len(center_pile) - 1))
                    target_card = center_pile[position]
                elif center_pile_status["state"] == "2-2":
                    # select either of 2-count items
                    assert isinstance(center_pile_status["max_item"], list)
                    selected_item = random.choice(center_pile_status["max_item"])
                    random_idx = random.randint(
                        0, (len(center_pile_status["groups"][selected_item]) - 1)
                    )
                    position, target_card = center_pile_status["groups"][selected_item][
                        random_idx
                    ]
                else:
                    # center pile either in state '2-1-1', '3-1', or '4*', so take max item
                    max_item = center_pile_status["max_item"]
                    assert isinstance(max_item, str)
                    position, target_card = center_pile_status["groups"][max_item][0]

                return SwapRequest(
                    target=(position, target_card), swap=(pile_idx, swap_idx, swap_card)
                )

            elif player_pile_status["state"] == "2-1-1":
                # see if max item in center pile; if not, check for either of count-1 cards

                # check for max, count-1 card match in center pile
                if player_pile_status["max_item"] in center_pile_status["groups"]:
                    item_match = player_pile_status["max_item"]
                    position, target_card = center_pile_status["groups"][item_match][0]

                    # determine which current pile card to send as swap
                    other_item_groups = [
                        group_cards
                        for other_item, group_cards in player_pile_status[
                            "groups"
                        ].items()
                        if other_item != item_match
                    ]
                    other_cards = [i for sublist in other_item_groups for i in sublist]
                    # take random card from one of the other item groups
                    swap_idx, swap_card = random.choice(other_cards)
                    return SwapRequest(
                        target=(position, target_card),
                        swap=(pile_idx, swap_idx, swap_card),
                    )
                else:
                    # look for item match for either of count-1 item cards
                    for item in list(player_pile_status["groups"].keys())[1:]:
                        if item in center_pile_status["groups"]:
                            position, target_card = center_pile_status["groups"][item][
                                0
                            ]

                            # find the _other_ item left to swap
                            assert isinstance(player_pile_status["max_item"], str)
                            other_item = list(
                                player_pile_status["items"].difference(
                                    {player_pile_status["max_item"], item}
                                )
                            )[0]
                            swap_idx, swap_card = player_pile_status["groups"][
                                other_item
                            ][0]
                            return SwapRequest(
                                target=(position, target_card),
                                swap=(pile_idx, swap_idx, swap_card),
                            )

            elif player_pile_status["state"] == "3-1":
                # then pile item counts are like 2, 1, 1
                # get singular item with count of 2 and look for match in pile
                if player_pile_status["max_item"] in center_pile_status["groups"]:
                    # identify center pile position/card to target
                    item_match = player_pile_status["max_item"]
                    position, target_card = center_pile_status["groups"][item_match][0]

                    # determine which current pile card to send as swap
                    other_item_groups = [
                        group_cards
                        for other_item, group_cards in player_pile_status[
                            "groups"
                        ].items()
                        if other_item != item_match
                    ]
                    other_cards = [i for sublist in other_item_groups for i in sublist]
                    # take random card from one of the other item groups
                    swap_idx, swap_card = random.choice(other_cards)
                    return SwapRequest(
                        target=(position, target_card),
                        swap=(pile_idx, swap_idx, swap_card),
                    )

            else:
                # probably an invalid state, max == 4 !!
                # but maybe account for it here???
                # no, just pass on this pile and it will get counted at end of turn loop
                raise AssertionError(
                    "Pile has complete set of items yet reached this point. This should be an invalid state."
                )

        return
