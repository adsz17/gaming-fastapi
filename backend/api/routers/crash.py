import os
from decimal import Decimal
from typing import Any

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import get_current_user
from .. import db
from ..models import Round, User
from .metrics import rtp_observed

router = APIRouter(prefix="/crash")

WALLET_URL = os.getenv("WALLET_URL", "http://localhost:8000")
RNG_URL = os.getenv("RNG_URL", "http://localhost:8001")


class RoundReq(BaseModel):
    bet: Decimal
    client_seed: str
    idem: str


@router.post("/round")
def crash_round(body: RoundReq, user: User = Depends(get_current_user)) -> dict[str, Any]:
    with Session(db.engine) as s:
        existing = s.scalar(select(Round).where(Round.idempotency_key == body.idem))
        if existing:
            return {"round_id": existing.id, "payout": float(existing.payout)}
    httpx.post(
        f"{WALLET_URL}/wallet/txn",
        json={
            "amount": float(-body.bet),
            "reason": "crash_bet",
            "idempotency_key": body.idem,
        },
    ).raise_for_status()
    rng = httpx.post(
        f"{RNG_URL}/rng/crash",
        json={"client_seed": body.client_seed, "idempotency_key": body.idem},
    )
    rng.raise_for_status()
    data = rng.json()
    payout = body.bet * Decimal(str(data["multiplier"]))
    with Session(db.engine) as s, s.begin():
        round_obj = Round(
            user_id=user.id,
            bet=body.bet,
            payout=payout,
            server_seed_hash=data["server_seed_hash"],
            client_seed=body.client_seed,
            nonce=data["nonce"],
            result_json=data,
            idempotency_key=body.idem,
        )
        s.add(round_obj)
        s.flush()
        round_id = round_obj.id
    rtp_observed.inc(float(payout))
    return {"round_id": round_id, "payout": float(payout)}
