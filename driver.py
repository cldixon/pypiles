import json
from typing import TypedDict
from uuid import uuid4

import ray

from pypiles.actors import (
    CenterPile,
    CenterPileState,
    GameStatus,
    GameStatusState,
    Player,
    PlayerState,
)
from pypiles.deck import prepare_game_cards
from pypiles.logger import setup_logger
from pypiles.strategies.greedy import GreedySwapper


class CompleteGameState(TypedDict):
    id: str
    game_status: GameStatusState
    center_pile: CenterPileState
    players: list[PlayerState]


def main():
    NUM_PLAYERS = 2
    PILE_SIZE = 4
    NUM_PILES_PER_PLAYERS = 6
    WINNING_SCORE = None

    game_id = str(uuid4())
    logger = setup_logger(name=__name__, log_file=f"logs/{game_id}/driver.log")

    center_pile_cards, player_cards = prepare_game_cards(
        num_players=NUM_PLAYERS,
        pile_size=PILE_SIZE,
        num_piles_per_player=NUM_PILES_PER_PLAYERS,
    )

    game_status = GameStatus.remote(
        winning_score=WINNING_SCORE
        if WINNING_SCORE is not None
        else NUM_PILES_PER_PLAYERS
    )
    center_pile = CenterPile.remote(
        cards=center_pile_cards, log_file=f"logs/{game_id}/cp.log"
    )

    players = [
        Player.remote(
            id=f"P{i+1}",
            cards=player_piles,
            strategy=GreedySwapper(),
            log_file=f"logs/{game_id}/p{i+1}.log",
        )
        for i, player_piles in enumerate(player_cards)
    ]

    try:
        results = ray.get(
            [
                p.play.remote(center_pile=center_pile, game_status=game_status)
                for p in players
            ]
        )
    except Exception as e:
        logger.info(f"!!! An error occurred during game play: {e}")

    finally:
        # collect all object states
        combined_game_state = CompleteGameState(
            id=game_id,
            game_status=ray.get(game_status.get_game_state.remote()),
            center_pile=ray.get(center_pile.get_center_pile_state.remote()),
            players=[ray.get(p.get_player_state.remote()) for p in players],
        )

        # save to file
        state_filepath = f"logs/{game_id}/state.json"
        logger.info(f"Saving final game state to {state_filepath}")

        with open(state_filepath, mode="w") as outfile:
            json.dump(combined_game_state, outfile)
            outfile.close()

        ## -- shutdown ray
        ray.shutdown()
    return


if __name__ == "__main__":
    main()
