import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from pypiles.game import GameConfig, GameSession
from server import app, game_manager


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_session():
    session = GameSession(
        game_id="test-123",
        config=GameConfig(
            num_players=2,
            pile_size=4,
            num_piles_per_player=6,
            winning_score=None,
            strategy="GreedySwapper",
        ),
    )
    session.phase = "completed"
    session.events = [
        {"seq": 0, "timestamp": 1000.0, "event_type": "game_started", "actor": "GS", "data": {}},
        {"seq": 1, "timestamp": 1001.0, "event_type": "swap_succeeded", "actor": "P1", "data": {}},
    ]
    session.initial_state = {
        "config": session.config,
        "center_pile": ["red::tophat", "blue::cardigan", "green::hoody", "yellow::mittens"],
        "players": [],
    }
    session.final_state = {
        "game_status": {"active": False, "winner": "P1"},
        "center_pile": {"cards": [], "metrics": {}},
        "players": [],
    }
    # Register and clean up
    game_manager.sessions[session.game_id] = session
    yield session
    game_manager.sessions.pop(session.game_id, None)


class TestListStrategies:
    async def test_returns_strategies(self, client):
        resp = await client.get("/api/strategies")
        assert resp.status_code == 200
        data = resp.json()
        assert "strategies" in data
        assert "GreedySwapper" in data["strategies"]


class TestConfigConstraints:
    async def test_returns_constraints(self, client):
        resp = await client.get("/api/config-constraints")
        assert resp.status_code == 200
        data = resp.json()
        assert data["num_players"]["min"] == 2
        assert data["num_players"]["max"] == 8
        assert data["pile_size"]["min"] == 2
        assert data["total_items"] == 50
        assert data["total_colors"] == 10


class TestCreateGame:
    async def test_create_game_success(self, client):
        resp = await client.post(
            "/api/games",
            json={
                "num_players": 2,
                "pile_size": 4,
                "num_piles_per_player": 6,
                "strategy": "GreedySwapper",
            },
        )
        assert resp.status_code == 200
        assert "game_id" in resp.json()

    async def test_invalid_product_constraint(self, client):
        resp = await client.post(
            "/api/games",
            json={
                "num_players": 8,
                "pile_size": 4,
                "num_piles_per_player": 12,
                "strategy": "GreedySwapper",
            },
        )
        assert resp.status_code == 400

    async def test_invalid_strategy(self, client):
        resp = await client.post(
            "/api/games",
            json={
                "num_players": 2,
                "pile_size": 4,
                "num_piles_per_player": 6,
                "strategy": "NonExistent",
            },
        )
        assert resp.status_code == 400

    async def test_validation_num_players_too_low(self, client):
        resp = await client.post(
            "/api/games",
            json={
                "num_players": 1,
                "pile_size": 4,
                "num_piles_per_player": 6,
                "strategy": "GreedySwapper",
            },
        )
        assert resp.status_code == 422


class TestListGames:
    async def test_list_games(self, client):
        resp = await client.get("/api/games")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestGetGame:
    async def test_not_found(self, client):
        resp = await client.get("/api/games/nonexistent-id")
        assert resp.status_code == 404

    async def test_returns_existing_game(self, client, mock_session):
        resp = await client.get(f"/api/games/{mock_session.game_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["game_id"] == "test-123"
        assert data["phase"] == "completed"
        assert data["total_events"] == 2


class TestGetGameEvents:
    async def test_not_found(self, client):
        resp = await client.get("/api/games/nonexistent-id/events")
        assert resp.status_code == 404

    async def test_returns_events(self, client, mock_session):
        resp = await client.get(f"/api/games/{mock_session.game_id}/events")
        assert resp.status_code == 200
        assert len(resp.json()["events"]) == 2


class TestGameWebSocket:
    def test_websocket_not_found(self):
        sync_client = TestClient(app)
        with sync_client.websocket_connect("/ws/games/nonexistent-id") as ws:
            data = ws.receive_json()
            assert data["type"] == "error"
            assert "not found" in data["payload"]["message"].lower()

    def test_websocket_completed_game_replay(self, mock_session):
        sync_client = TestClient(app)
        with sync_client.websocket_connect(
            f"/ws/games/{mock_session.game_id}"
        ) as ws:
            messages = []
            # Collect all messages until game_complete
            while True:
                msg = ws.receive_json()
                messages.append(msg)
                if msg["type"] == "game_complete":
                    break

            types = [m["type"] for m in messages]
            assert types[0] == "game_setup"
            assert types[-1] == "game_complete"
            assert "event_batch" in types
