import ray

from pypiles.actors.event_collector import EventCollector


def test_event_collector_stores_events():
    collector = EventCollector.remote(game_id="test-game-1")

    ray.get(collector.push_event.remote(
        event_type="game_started",
        actor="GS",
        data={"game_id": "test-game-1"},
    ))
    ray.get(collector.push_event.remote(
        event_type="swap_requested",
        actor="P1",
        data={"player_id": "P1", "pile_idx": 0},
    ))
    ray.get(collector.push_event.remote(
        event_type="swap_succeeded",
        actor="P1",
        data={"player_id": "P1", "sent_card": "red::tophat"},
    ))

    events = ray.get(collector.get_events.remote())
    assert len(events) == 3
    assert ray.get(collector.get_event_count.remote()) == 3

    # verify sequence numbers
    assert events[0]["seq"] == 0
    assert events[1]["seq"] == 1
    assert events[2]["seq"] == 2

    # verify event types
    assert events[0]["event_type"] == "game_started"
    assert events[1]["event_type"] == "swap_requested"
    assert events[2]["event_type"] == "swap_succeeded"

    # verify timestamps are ordered
    assert events[0]["timestamp"] <= events[1]["timestamp"]
    assert events[1]["timestamp"] <= events[2]["timestamp"]

    # verify data payloads
    assert events[0]["data"]["game_id"] == "test-game-1"
    assert events[1]["data"]["player_id"] == "P1"
    assert events[2]["data"]["sent_card"] == "red::tophat"


def test_event_collector_empty():
    collector = EventCollector.remote(game_id="test-game-2")

    events = ray.get(collector.get_events.remote())
    assert events == []
    assert ray.get(collector.get_event_count.remote()) == 0
