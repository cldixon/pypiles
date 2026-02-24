import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from pypiles.characters import CHARACTER_REGISTRY, assign_default_characters
from pypiles.game import GameConfig, GameManager

# --- Pydantic models for REST API ---


class CreateGameRequest(BaseModel):
    num_players: int = Field(ge=2, le=8, default=2)
    pile_size: int = Field(ge=2, le=10, default=4)
    num_piles_per_player: int = Field(ge=1, le=12, default=6)
    winning_score: int | None = None
    player_characters: list[str] | None = None


class CreateGameResponse(BaseModel):
    game_id: str


# --- App lifecycle ---

game_manager = GameManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    game_manager.ensure_ray()
    yield


app = FastAPI(title="PyPiles", lifespan=lifespan)


# --- REST endpoints ---


@app.post("/api/games", response_model=CreateGameResponse)
async def create_game(req: CreateGameRequest):
    if req.num_players * req.num_piles_per_player > 49:
        raise HTTPException(
            status_code=400,
            detail=f"num_players * num_piles_per_player must be <= 49, got {req.num_players * req.num_piles_per_player}",
        )

    # Assign distinct characters by default, cycling through available ones
    player_characters = req.player_characters or assign_default_characters(
        req.num_players
    )

    if len(player_characters) != req.num_players:
        raise HTTPException(
            status_code=400,
            detail=f"player_characters length ({len(player_characters)}) must match num_players ({req.num_players})",
        )

    available = list(CHARACTER_REGISTRY.keys())
    for char_id in player_characters:
        if char_id not in CHARACTER_REGISTRY:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown character '{char_id}'. Available: {available}",
            )

    config = GameConfig(
        num_players=req.num_players,
        pile_size=req.pile_size,
        num_piles_per_player=req.num_piles_per_player,
        winning_score=req.winning_score,
        player_characters=player_characters,
    )
    game_id = game_manager.create_game(config)
    return CreateGameResponse(game_id=game_id)


@app.get("/api/games")
async def list_games():
    return game_manager.list_games()


@app.get("/api/games/{game_id}")
async def get_game(game_id: str):
    session = game_manager.get_session(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")
    return {
        "game_id": session.game_id,
        "phase": session.phase,
        "config": session.config,
        "total_events": len(session.events),
        "initial_state": session.initial_state,
        "final_state": session.final_state,
        "error": session.error,
    }


@app.get("/api/games/{game_id}/events")
async def get_game_events(game_id: str):
    session = game_manager.get_session(game_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"events": session.events}


@app.get("/api/characters")
async def list_characters():
    return {
        "characters": [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in CHARACTER_REGISTRY.values()
        ]
    }


@app.get("/api/config-constraints")
async def get_config_constraints():
    return {
        "num_players": {"min": 2, "max": 8},
        "pile_size": {"min": 2, "max": 10},
        "num_piles_per_player": {"min": 1, "max": 12},
        "product_constraint": "num_players * num_piles_per_player <= 49",
        "total_items": 50,
        "total_colors": 10,
    }


# --- WebSocket endpoint ---


@app.websocket("/ws/games/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str):
    await websocket.accept()

    session = game_manager.get_session(game_id)
    if not session:
        await websocket.send_json(
            {"type": "error", "game_id": game_id, "payload": {"message": "Game not found"}}
        )
        await websocket.close()
        return

    if session.phase == "configuring":
        await game_manager.run_game(game_id)
    elif session.phase == "running":
        await websocket.send_json(
            {"type": "error", "game_id": game_id, "payload": {"message": "Game is already running"}}
        )
        await websocket.close()
        return
    # "completed" is fine — we replay from stored events

    if session.phase == "error":
        await websocket.send_json(
            {"type": "error", "game_id": game_id, "payload": {"message": session.error}}
        )
        await websocket.close()
        return

    # Send setup
    await websocket.send_json(
        {
            "type": "game_setup",
            "game_id": game_id,
            "payload": {
                **(session.initial_state or {}),
                "total_events": len(session.events),
            },
        }
    )

    # Stream events in batches with pacing
    playback_speed = 1.0
    paused = False
    batch_size = 5
    base_delay = 0.1  # 100ms between batches at 1x

    events = session.events
    idx = 0

    try:
        while idx < len(events):
            # Check for control messages (non-blocking)
            try:
                msg = await asyncio.wait_for(
                    websocket.receive_json(), timeout=0.01
                )
                if msg.get("type") == "playback_control":
                    action = msg.get("action")
                    if action == "pause":
                        paused = True
                    elif action == "resume":
                        paused = False
                    elif action == "set_speed":
                        playback_speed = max(
                            0.1, min(20.0, float(msg.get("value", 1.0)))
                        )
                    elif action == "skip_to_end":
                        idx = len(events)
                        continue
            except asyncio.TimeoutError:
                pass

            if paused:
                await asyncio.sleep(0.1)
                continue

            # Send batch
            batch = events[idx : idx + batch_size]
            progress = min(1.0, (idx + len(batch)) / len(events))

            await websocket.send_json(
                {
                    "type": "event_batch",
                    "game_id": game_id,
                    "payload": {
                        "events": batch,
                        "progress": progress,
                    },
                }
            )

            idx += len(batch)
            await asyncio.sleep(base_delay / playback_speed)

        # Send completion
        await websocket.send_json(
            {
                "type": "game_complete",
                "game_id": game_id,
                "payload": {
                    **(session.final_state or {}),
                    "duration_ms": _calc_duration(session),
                    "total_events": len(session.events),
                },
            }
        )

        # Gracefully close the WebSocket with normal closure code
        await websocket.close(code=1000)

    except WebSocketDisconnect:
        pass


def _calc_duration(session) -> float:
    if session.events and len(session.events) >= 2:
        return (
            session.events[-1]["timestamp"] - session.events[0]["timestamp"]
        ) * 1000
    return 0.0
