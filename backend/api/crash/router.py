from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, WebSocket
from .engine import CrashEngine, CRASH_MIN_BET
import uuid

router = APIRouter(prefix="/crash", tags=["crash"])

def get_engine() -> CrashEngine:
    # Asumimos engine en app.state (configurado en main.py)
    from api.main import app
    return app.state.crash_engine  # type: ignore

def ensure_player_id(player_id: str | None, response: Response) -> str:
    if player_id:
        return player_id
    pid = str(uuid.uuid4())
    # cookie simple; si tu auth usa cookies httpOnly, podés migrar esto a esa identidad
    response.set_cookie("player_id", pid, httponly=False, samesite="Lax")
    return pid

@router.get("/state")
async def state(response: Response, player_id: str | None = Cookie(default=None), engine: CrashEngine = Depends(get_engine)):
    pid = ensure_player_id(player_id, response)
    return await engine.state(pid)

@router.post("/bet")
async def bet(
    response: Response,
    amount: float,
    auto_cashout: float | None = None,
    player_id: str | None = Cookie(default=None),
    engine: CrashEngine = Depends(get_engine),
):
    pid = ensure_player_id(player_id, response)
    try:
        await engine.place_bet(pid, float(amount), auto_cashout)
        return {"ok": True}
    except ValueError as e:
        if str(e) == "MIN_BET":
            raise HTTPException(status_code=422, detail=f"amount must be >= {CRASH_MIN_BET}")
        raise
    except RuntimeError as e:
        code = 409 if str(e) in {"NOT_BETTING", "ALREADY_BET"} else 400
        raise HTTPException(status_code=code, detail=str(e))

@router.post("/cashout")
async def cashout(
    response: Response,
    player_id: str | None = Cookie(default=None),
    engine: CrashEngine = Depends(get_engine),
):
    pid = ensure_player_id(player_id, response)
    try:
        return await engine.cashout(pid)
    except RuntimeError as e:
        code = 409 if str(e) in {"NOT_RUNNING", "NO_ACTIVE_BET"} else 400
        raise HTTPException(status_code=code, detail=str(e))

@router.websocket("/stream")
async def stream(ws: WebSocket, engine: CrashEngine = Depends(get_engine)):
    await engine.subscribe(ws)
    try:
        while True:
            # Sólo mantenemos viva la conexión; el engine hace broadcast
            await ws.receive_text()
    except Exception:
        pass
