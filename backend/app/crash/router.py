import asyncio
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, WebSocket
from pydantic import BaseModel

from .engine import engine

router = APIRouter(prefix="/crash")

def get_player_id(request: Request, response: Response) -> str:
    pid = request.cookies.get("player_id")
    if not pid:
        pid = str(uuid4())
        response.set_cookie("player_id", pid, httponly=True)
    return pid


class BetReq(BaseModel):
    amount: float
    auto_cashout: Optional[float] = None


@router.post("/bet")
async def post_bet(body: BetReq, response: Response, player_id: str = Depends(get_player_id)):
    try:
        await engine.place_bet(player_id, float(body.amount), body.auto_cashout)
    except ValueError:
        raise HTTPException(status_code=422, detail="invalid_amount") from None
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return {"ok": True}


@router.post("/cashout")
async def post_cashout(response: Response, player_id: str = Depends(get_player_id)):
    try:
        data = await engine.cashout(player_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return data


@router.get("/state")
async def get_state(request: Request, response: Response):
    pid = request.cookies.get("player_id")
    if not pid:
        pid = str(uuid4())
        response.set_cookie("player_id", pid, httponly=True)
    return engine.get_state(pid)


@router.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()
    engine.websockets.add(ws)
    try:
        while True:
            await asyncio.sleep(60)
    finally:
        engine.websockets.discard(ws)
