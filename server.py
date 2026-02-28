import asyncio
from contextlib import asynccontextmanager

import ray
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from pypiles.characters import CHARACTER_REGISTRY, assign_default_characters
from pypiles.db import close_db, init_db, log_game_created, log_game_completed
from pypiles.game import GameConfig, GameManager

# --- Pydantic models for REST API ---


class CreateGameRequest(BaseModel):
    num_players: int = Field(ge=2, le=4, default=2)
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
    await init_db()
    yield
    await close_db()


app = FastAPI(title="PyPiles", lifespan=lifespan)


# --- REST endpoints ---


@app.post("/api/games", response_model=CreateGameResponse)
async def create_game(req: CreateGameRequest, request: Request):
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
    await log_game_created(
        game_id=game_id,
        config=config,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
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
        "num_players": {"min": 2, "max": 4},
        "pile_size": {"min": 2, "max": 10},
        "num_piles_per_player": {"min": 1, "max": 12},
        "product_constraint": "num_players * num_piles_per_player <= 49",
        "total_items": 50,
        "total_colors": 10,
    }


# --- WebSocket endpoint ---


async def _poll_events(session, cursor: int) -> list:
    """Poll EventCollector for new events (runs ray.get in executor)."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(
            None,
            ray.get,
            session.event_collector.get_events_since.remote(cursor),
        )
    except Exception:
        return []


async def _recv_control(websocket: WebSocket) -> dict | None:
    """Non-blocking read of a client control message."""
    try:
        msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.01)
        if msg.get("type") == "playback_control":
            return msg
    except asyncio.TimeoutError:
        pass
    return None


async def _stream_live(websocket: WebSocket, game_id: str, session) -> None:
    """Stream events in real time as the game plays."""
    cursor = 0
    paused = False
    skip_requested = False

    while True:
        msg = await _recv_control(websocket)
        if msg:
            action = msg.get("action")
            if action == "pause":
                paused = True
            elif action == "resume":
                paused = False
            elif action == "skip_to_end":
                skip_requested = True

        if paused and not skip_requested:
            await asyncio.sleep(0.1)
            continue

        # Check if game finished (phase set by background thread)
        game_done = session.phase in ("completed", "error")

        if game_done:
            # Game thread already collected all events into session.events.
            # Send any remaining events from the finalized list.
            remaining = session.events[cursor:]
            if remaining:
                await websocket.send_json(
                    {
                        "type": "event_batch",
                        "game_id": game_id,
                        "payload": {"events": remaining, "progress": 1.0},
                    }
                )
            break

        # Game still running -- poll the EventCollector actor
        new_events = await _poll_events(session, cursor)
        if new_events:
            await websocket.send_json(
                {
                    "type": "event_batch",
                    "game_id": game_id,
                    "payload": {"events": new_events, "progress": None},
                }
            )
            cursor += len(new_events)

        await asyncio.sleep(0.05)  # 50ms polling interval


async def _stream_replay(websocket: WebSocket, game_id: str, session) -> None:
    """Replay stored events with pacing (for completed games)."""
    playback_speed = 1.0
    paused = False
    batch_size = 5
    base_delay = 0.1  # 100ms between batches at 1x

    events = session.events
    idx = 0

    while idx < len(events):
        msg = await _recv_control(websocket)
        if msg:
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

        if paused:
            await asyncio.sleep(0.1)
            continue

        batch = events[idx : idx + batch_size]
        progress = min(1.0, (idx + len(batch)) / len(events))

        await websocket.send_json(
            {
                "type": "event_batch",
                "game_id": game_id,
                "payload": {"events": batch, "progress": progress},
            }
        )

        idx += len(batch)
        await asyncio.sleep(base_delay / playback_speed)


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

    # Determine mode: live streaming vs replay
    live_mode = False

    if session.phase == "configuring":
        # Setup actors and initial state, then stream live
        try:
            await asyncio.wait_for(game_manager.setup_game(game_id), timeout=30)
            live_mode = True
        except asyncio.TimeoutError:
            session.phase = "error"
            session.error = "Game setup timed out. The server may be busy."
        except Exception as e:
            session.phase = "error"
            session.error = f"Game setup failed: {e}"
    elif session.phase == "running":
        # Join an already-running game -- stream live from where we are
        live_mode = True
    # "completed" -> replay mode (live_mode stays False)

    if session.phase == "error":
        await websocket.send_json(
            {"type": "error", "game_id": game_id, "payload": {"message": session.error}}
        )
        await websocket.close()
        return

    # Send setup message
    await websocket.send_json(
        {
            "type": "game_setup",
            "game_id": game_id,
            "payload": {
                **(session.initial_state or {}),
                "total_events": len(session.events),
                "mode": "live" if live_mode else "replay",
            },
        }
    )

    game_task = None
    try:
        if live_mode:
            # Start gameplay in background, stream events as they happen
            game_task = asyncio.create_task(game_manager.run_players(game_id))
            await _stream_live(websocket, game_id, session)
        else:
            # Replay stored events with pacing
            await _stream_replay(websocket, game_id, session)

        # Log completion to database
        if session.final_state:
            await log_game_completed(
                game_id=game_id,
                phase=session.phase,
                duration_ms=session.final_state.get("duration_ms", 0),
                total_events=session.final_state.get("total_events", 0),
                winner=session.final_state.get("game_status", {}).get("winner"),
                error=session.error,
                players=session.final_state.get("players", []),
            )

        # Send completion
        await websocket.send_json(
            {
                "type": "game_complete",
                "game_id": game_id,
                "payload": session.final_state or {},
            }
        )

        await websocket.close(code=1000)

    except WebSocketDisconnect:
        pass
    finally:
        # Ensure the background game task completes even if the client disconnects
        if game_task and not game_task.done():
            try:
                await game_task
            except Exception:
                pass
