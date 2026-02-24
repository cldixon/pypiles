import pytest

from pypiles.game import GameConfig, GameManager


@pytest.fixture
def game_manager():
    return GameManager()


def test_create_game(game_manager):
    config = GameConfig(
        num_players=2,
        pile_size=4,
        num_piles_per_player=6,
        winning_score=None,
        player_characters=["greedy-nathan", "greedy-nathan"],
    )
    game_id = game_manager.create_game(config)
    assert game_id is not None

    session = game_manager.get_session(game_id)
    assert session is not None
    assert session.phase == "configuring"
    assert session.config == config


def test_run_game(game_manager):
    config = GameConfig(
        num_players=2,
        pile_size=4,
        num_piles_per_player=6,
        winning_score=None,
        player_characters=["greedy-nathan", "greedy-nathan"],
    )
    game_id = game_manager.create_game(config)

    game_manager.run_game_sync(game_id)

    session = game_manager.get_session(game_id)
    assert session.phase == "completed"

    # Verify events were collected
    assert len(session.events) > 0

    # Verify initial state
    assert session.initial_state is not None
    assert len(session.initial_state["center_pile"]) == 4
    assert len(session.initial_state["players"]) == 2

    # Verify final state
    assert session.final_state is not None
    assert session.final_state["game_status"]["active"] is False
    assert session.final_state["game_status"]["winner"] is not None

    # Verify event types include key events
    event_types = {e["event_type"] for e in session.events}
    assert "game_started" in event_types
    assert "swap_requested" in event_types
    assert "swap_succeeded" in event_types


def test_list_games(game_manager):
    config = GameConfig(
        num_players=3,
        pile_size=4,
        num_piles_per_player=6,
        winning_score=None,
        player_characters=["greedy-nathan", "greedy-nathan", "greedy-nathan"],
    )
    game_manager.create_game(config)

    games = game_manager.list_games()
    assert len(games) >= 1
    assert all("game_id" in g for g in games)
    assert all("phase" in g for g in games)


def test_run_game_custom_winning_score(game_manager):
    config = GameConfig(
        num_players=2,
        pile_size=4,
        num_piles_per_player=6,
        winning_score=1,
        player_characters=["greedy-nathan", "greedy-nathan"],
    )
    game_id = game_manager.create_game(config)

    game_manager.run_game_sync(game_id)

    session = game_manager.get_session(game_id)
    assert session.phase == "completed"
    assert session.final_state["game_status"]["winner"] is not None
