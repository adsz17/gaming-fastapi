import os
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    generate_latest,
)
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from .middleware.ratelimit import RateLimitMiddleware
from .models import Base, Round, User
from .services.wallet import apply_transaction

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-please")
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
_engine_args: dict[str, Any] = {"future": True}
if DATABASE_URL.startswith("sqlite") and ":memory:" in DATABASE_URL:
    _engine_args.update(
        connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
if os.getenv("SERVERLESS_DB") == "true":
    _engine_args.update(pool_size=3, max_overflow=3, pool_recycle=900)
engine = create_engine(DATABASE_URL, **_engine_args)

try:  # best effort; tests may override engine
    Base.metadata.create_all(engine)
except Exception:  # pragma: no cover - ignore DB issues during import
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(RateLimitMiddleware)

registry = CollectorRegistry()
rtp_observed = Counter(
    "rtp_observed", "Observed Return To Player", registry=registry
)

WALLET_URL = os.getenv("WALLET_URL", "http://localhost:8000")
RNG_URL = os.getenv("RNG_URL", "http://localhost:8001")


class AuthBody(BaseModel):
    email: EmailStr
    password: str


class TokenResp(BaseModel):
    token: str


class TxnReq(BaseModel):
    amount: Decimal
    reason: str
    idempotency_key: str


class RoundReq(BaseModel):
    bet: Decimal
    client_seed: str
    idem: str


def _create_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MIN)
    return jwt.encode({"sub": uid, "exp": exp}, JWT_SECRET, algorithm=JWT_ALG)


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


@app.post("/auth/register", response_model=TokenResp)
def register(body: AuthBody) -> TokenResp:
    with Session(engine) as s, s.begin():
        if s.scalar(select(User).where(User.email == body.email)):
            raise HTTPException(status_code=400, detail="Email exists")
        user = User(
            id=str(uuid.uuid4()),
            email=body.email,
            password_hash=pwd_context.hash(body.password),
        )
        s.add(user)
        user_id = user.id
    return TokenResp(token=_create_token(user_id))


@app.post("/auth/login", response_model=TokenResp)
def login(body: AuthBody) -> TokenResp:
    with Session(engine) as s:
        user = s.scalar(select(User).where(User.email == body.email))
        if not user or not pwd_context.verify(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.id
    return TokenResp(token=_create_token(user_id))


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
    # debit via wallet service
    httpx.post(
        f"{WALLET_URL}/wallet/txn",
        json={
            "amount": float(-body.bet),
            "reason": "crash_bet",
            "idempotency_key": body.idem,
        },
    ).raise_for_status()
    # rng service
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

