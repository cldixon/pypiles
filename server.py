import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pypiles.game import STRATEGY_REGISTRY, GameConfig, GameManager

# --- Pydantic models for REST API ---


class CreateGameRequest(BaseModel):
    num_players: int = Field(ge=2, le=8, default=2)
    pile_size: int = Field(ge=2, le=10, default=4)
    num_piles_per_player: int = Field(ge=1, le=12, default=6)
    winning_score: int | None = None
    strategy: str = "GreedySwapper"


class CreateGameResponse(BaseModel):
    game_id: str


# --- App lifecycle ---

game_manager = GameManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    game_manager.ensure_ray()
    yield


app = FastAPI(title="PyPiles", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REST endpoints ---


@app.post("/api/games", response_model=CreateGameResponse)
async def create_game(req: CreateGameRequest):
    if req.num_players * req.num_piles_per_player > 49:
        raise HTTPException(
            status_code=400,
            detail=f"num_players * num_piles_per_player must be <= 49, got {req.num_players * req.num_piles_per_player}",
        )

    if req.strategy not in STRATEGY_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy '{req.strategy}'. Available: {list(STRATEGY_REGISTRY.keys())}",
        )

    config = GameConfig(
        num_players=req.num_players,
        pile_size=req.pile_size,
        num_piles_per_player=req.num_piles_per_player,
        winning_score=req.winning_score,
        strategy=req.strategy,
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


@app.get("/api/strategies")
async def list_strategies():
    return {"strategies": list(STRATEGY_REGISTRY.keys())}


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


# --- Static file serving (SvelteKit build) ---

frontend_build_dir = Path(__file__).parent / "frontend" / "build"
if frontend_build_dir.exists():
    # Serve static assets (JS, CSS, etc.)
    static_dir = frontend_build_dir / "_app"
    if static_dir.exists():
        app.mount(
            "/_app",
            StaticFiles(directory=str(static_dir)),
            name="svelte_app",
        )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve SvelteKit SPA for all non-API routes."""
        file_path = frontend_build_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # SPA fallback
        index = frontend_build_dir / "index.html"
        if index.exists():
            return FileResponse(str(index))
        raise HTTPException(status_code=404, detail="Not found")
