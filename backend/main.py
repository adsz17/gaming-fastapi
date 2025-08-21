import os
from decimal import Decimal
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    generate_latest,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import engine
from .middleware.ratelimit import RateLimitMiddleware
from .models import Base, Round, User
from .services.wallet import apply_transaction
from .settings import settings
from .routes.auth import router as auth_router

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-please")
JWT_ALG = "HS256"

app = FastAPI()

ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

registry = CollectorRegistry()
rtp_observed = Counter(
    "rtp_observed", "Observed Return To Player", registry=registry
)

WALLET_URL = os.getenv("WALLET_URL", "http://localhost:8000")
RNG_URL = os.getenv("RNG_URL", "http://localhost:8001")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])


class TxnReq(BaseModel):
    amount: Decimal
    reason: str
    idempotency_key: str


class RoundReq(BaseModel):
    bet: Decimal
    client_seed: str
    idem: str


def get_current_user(request: Request) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc:  # pragma: no cover - security check
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    uid = payload.get("sub")
    with Session(engine) as s:
        user = s.get(User, uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


@app.get("/me")
def me(user: User = Depends(get_current_user)) -> dict[str, Any]:
    return {"id": user.id, "email": user.email}


@app.post("/wallet/txn")
def wallet_txn(body: TxnReq, user: User = Depends(get_current_user)) -> dict[str, Any]:
    with Session(engine) as s, s.begin():
        entry = apply_transaction(s, user.id, body.amount, body.reason, body.idempotency_key)
        balance = float(entry.balance_after)
    return {"balance": balance}


@app.post("/crash/round")
def crash_round(body: RoundReq, user: User = Depends(get_current_user)) -> dict[str, Any]:
    with Session(engine) as s:
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
    with Session(engine) as s, s.begin():
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


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
