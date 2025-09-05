from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import get_current_user
from .. import db
from ..models import CrashBet, CrashRound, User
from ..services.wallet import apply_transaction
from .engine import CrashEngine, CRASH_MIN_BET

router = APIRouter(prefix="/crash", tags=["crash"])


def get_engine() -> CrashEngine:
    # Asumimos engine en app.state (configurado en main.py)
    from api.main import app
    return app.state.crash_engine  # type: ignore


@router.get("/state")
async def state(user: User = Depends(get_current_user), engine: CrashEngine = Depends(get_engine)):
    return await engine.state(user.id)

class BetIn(BaseModel):
    amount: float
    auto_cashout: float | None = Field(default=None, ge=1.01)


@router.post("/bet", status_code=201)
async def bet(
    body: BetIn,
    engine: CrashEngine = Depends(get_engine),
    user: User = Depends(get_current_user),
):
    try:
        await engine.place_bet(user.id, body.amount, body.auto_cashout)
    except ValueError as e:
        if str(e) == "MIN_BET":
            raise HTTPException(status_code=422, detail=f"amount must be >= {CRASH_MIN_BET}")
        raise
    except RuntimeError as e:
        code = 409 if str(e) in {"NOT_BETTING", "ALREADY_BET"} else 400
        raise HTTPException(status_code=code, detail=str(e))

    with Session(db.engine) as s, s.begin():
        if not s.get(CrashRound, engine.round_id):
            s.add(CrashRound(id=engine.round_id, crash_at=engine.crash_at or 0.0))
        apply_transaction(
            s,
            user.id,
            Decimal(str(-body.amount)),
            "crash_bet",
            f"crash_bet:{engine.round_id}:{user.id}",
        )
        s.add(
            CrashBet(
                round_id=engine.round_id,
                user_id=user.id,
                amount=Decimal(str(body.amount)),
            )
        )
    return {"ok": True}

@router.post("/cashout")
async def cashout(
    engine: CrashEngine = Depends(get_engine),
    user: User = Depends(get_current_user),
):
    try:
        data = await engine.cashout(user.id)
    except RuntimeError as e:
        code = 409 if str(e) in {"NOT_RUNNING", "NO_ACTIVE_BET"} else 400
        raise HTTPException(status_code=code, detail=str(e))

    with Session(db.engine) as s, s.begin():
        bet = s.execute(
            select(CrashBet).where(
                CrashBet.round_id == engine.round_id, CrashBet.user_id == user.id
            ).with_for_update()
        ).scalar_one_or_none()
        if bet and bet.status == "OPEN":
            bet.status = "CASHED"
            bet.cashout_multiplier = data["at"]
            bet.payout = Decimal(str(data["payout"]))
            apply_transaction(
                s,
                user.id,
                Decimal(str(data["payout"])),
                "crash_win",
                f"crash_cashout:{engine.round_id}:{user.id}",
            )
    return data

@router.websocket("/stream")
async def stream(ws: WebSocket, engine: CrashEngine = Depends(get_engine)):
    await engine.subscribe(ws)
    try:
        while True:
            # Sólo mantenemos viva la conexión; el engine hace broadcast
            await ws.receive_text()
    except Exception:
        pass


async def handle_crash(round_id: str, losers: list[str]):
    """Mark losing bets as lost in the database."""
    if not losers:
        return
    with Session(db.engine) as s, s.begin():
        s.execute(
            select(CrashBet)  # dummy select to ensure table exists in tests
        )
        s.query(CrashBet).filter(
            CrashBet.round_id == round_id,
            CrashBet.user_id.in_(losers),
            CrashBet.status == "OPEN",
        ).update({"status": "LOST", "payout": Decimal("0")}, synchronize_session=False)
