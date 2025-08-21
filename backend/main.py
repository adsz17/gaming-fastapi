import os, hmac, hashlib, json, uuid, logging, time, contextvars
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, Request, Response

import os, hmac, hashlib, json, uuid
from pathlib import Path

import hashlib
import hmac
import os
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, Header

from typing import Any, List

from pathlib import Path


from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


trace_id_ctx = contextvars.ContextVar("trace_id", default="-")


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_ctx.get()
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": record.trace_id,
        }
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "latency"):
            log_record["latency"] = record.latency
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
handler.addFilter(TraceIdFilter())

root = logging.getLogger()
root.handlers = [handler]
root.setLevel(logging.INFO)
for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    logging.getLogger(name).handlers = []
    logging.getLogger(name).propagate = True

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi.responses import FileResponse

from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    JSON,
    BigInteger,
    ForeignKey,
    Numeric,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

# ---------- Config ----------
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-please")
JWT_ALG = "HS256"
JWT_MINUTES = int(os.getenv("JWT_EXPIRES_MIN", "1440"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-token")

DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_recycle=1800,
)

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="iGaming Starter - Postgres/JWT", version="0.2.0")

ALLOWED = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in ALLOWED.split(",")] if ALLOWED else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Observability ----------
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "Request latency", ["endpoint", "method"]
)
ERROR_COUNT = Counter(
    "http_request_errors_total", "Request error count", ["endpoint", "method"]
)
RTP_GAUGE = Gauge("rtp_observed", "Observed RTP")
_total_bets = 0.0
_total_payouts = 0.0


def _update_rtp(bet: Decimal, payout: Decimal) -> None:
    global _total_bets, _total_payouts
    _total_bets += float(bet)
    _total_payouts += float(payout)
    if _total_bets > 0:
        RTP_GAUGE.set(_total_payouts / _total_bets)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    trace_id = uuid.uuid4().hex
    token = trace_id_ctx.set(trace_id)
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
    except Exception:
        logging.getLogger("uvicorn.error").exception("request failed")
        raise
    finally:
        duration = time.perf_counter() - start
        status_code = response.status_code if response else 500
        REQUEST_LATENCY.labels(endpoint=request.url.path, method=request.method).observe(
            duration
        )
        if status_code >= 400:
            ERROR_COUNT.labels(endpoint=request.url.path, method=request.method).inc()
        logging.getLogger("uvicorn.access").info(
            "request",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "latency": duration,
            },
        )
        trace_id_ctx.reset(token)
        if response:
            response.headers["X-Trace-Id"] = trace_id
    return response


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
# ---------- Admin Auth ----------
def require_admin(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Invalid admin token")

# ---------- DB Models ----------
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    account: Mapped["Account"] = relationship(back_populates="user", uselist=False)

class Account(Base):
    __tablename__ = "accounts"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship(back_populates="account")

class Round(Base):
    __tablename__ = "rounds"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    game_code: Mapped[str] = mapped_column(String(50), default="crash_v1")
    bet: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    payout: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    server_seed_hash: Mapped[str] = mapped_column(Text)
    client_seed: Mapped[str] = mapped_column(Text)
    nonce: Mapped[int] = mapped_column(BigInteger)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

# ---------- Database ----------
# The schema is managed via Alembic migrations. Tables are not
# created automatically at runtime. Ensure `alembic upgrade head`
# has been executed before starting the application.
class Ledger(Base):
    __tablename__ = "ledger"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    meta: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

# ---------- Startup: create tables ----------
@app.on_event("startup")
def _startup():

# ---------- Provably Fair RNG (server-side) ----------
SEEDS: dict[str, Any] = {
    "server_seed": os.urandom(32).hex(),
    "server_seed_hash": "",
    "nonce": 0,
}


def _hash_seed(seed_hex: str) -> str:
    return hashlib.sha256(bytes.fromhex(seed_hex)).hexdigest()


SEEDS["server_seed_hash"] = _hash_seed(SEEDS["server_seed"])

def hmac_sha256(server_seed_hex: str, message: str) -> str:
    key = bytes.fromhex(server_seed_hex)
    return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()

def hex_to_unit(hex_str: str) -> float:
    sl = hex_str[:13]             # 52 bits
    val = int(sl, 16)
    u = val / float(16**13)       # 2**52
    return min(1.0 - 1e-12, max(0.0, u))

def crash_multiplier(server_seed_hex: str, client_seed: str, nonce: int, house_edge: float = 0.01) -> float:
    digest = hmac_sha256(server_seed_hex, f"{client_seed}:{nonce}")
    u = hex_to_unit(digest)
    m = 1.0 / max(1e-12, (1.0 - (u * (1.0 - house_edge))))
    m = min(100.0, m)
    return float(f"{m:.2f}")

# ---------- Auth / JWT ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    token: str

def create_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "email": email, "iat": int(now.timestamp()),
               "exp": int((now + timedelta(minutes=JWT_MINUTES)).timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(session: Session = Depends(lambda: Session(engine))):
    from fastapi import Request
    # Simple Bearer extractor
    def _dep(request: "Request"):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(401, "Missing Bearer token")
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        except JWTError:
            raise HTTPException(401, "Invalid or expired token")
        uid = payload.get("sub")
        user = session.get(User, uid)
        if not user:
            raise HTTPException(401, "User not found")
        return user
    return _dep

@app.post("/auth/register", response_model=TokenOut)
def register(body: RegisterIn):
    with Session(engine) as s:
        if s.scalar(select(User).where(User.email == body.email)):
            raise HTTPException(400, "Email already registered")
        u = User(id=str(uuid.uuid4()), email=body.email, password_hash=pwd.hash(body.password))
        s.add(u)
        s.flush()
        # Bienvenida: 100 fichas
        acc = Account(user_id=u.id, balance=Decimal("100.00"))
        s.add(acc)
        s.commit()
        return {"token": create_token(u.id, u.email)}

@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn):
    with Session(engine) as s:
        u = s.scalar(select(User).where(User.email == body.email))
        if not u or not pwd.verify(body.password, u.password_hash):
            raise HTTPException(401, "Invalid credentials")
        return {"token": create_token(u.id, u.email)}

@app.get("/me")
def me(user: User = Depends(get_current_user())):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}

# ---------- Game endpoints ----------
class BetRoundIn(BaseModel):
    bet: float
    client_seed: str

class RoundOut(BaseModel):
    round_id: int
    bet: float
    payout: float
    multiplier: float
    new_balance: float
    server_seed_hash: str
    client_seed: str
    nonce: int
    created_at: str

class HistoryResp(BaseModel):
    rounds: List[RoundOut]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/account")
def account(user: User = Depends(get_current_user())):
    with Session(engine) as s:
        acc = s.get(Account, user.id)
        if acc is None:
            raise HTTPException(404, "Account not found")
        return {"balance": float(acc.balance)}

@app.post("/round", response_model=RoundOut)
def play_round(body: BetRoundIn, user: User = Depends(get_current_user())):
    if body.bet <= 0:
        raise HTTPException(400, "Bet must be > 0")

    with Session(engine) as s:
        acc = s.get(Account, user.id)
        if not acc:
            acc = Account(user_id=user.id, balance=Decimal("0"))
            s.add(acc)
            s.flush()
        bet_dec = Decimal(str(round(body.bet, 6)))
        if acc.balance < bet_dec:
            raise HTTPException(400, "Insufficient balance")

        SEEDS["nonce"] += 1
        nonce = SEEDS["nonce"]
        mult = crash_multiplier(SEEDS["server_seed"], body.client_seed, nonce)
        payout = Decimal(str(round(body.bet * mult, 2)))

        row = Round(
            user_id=user.id,
            bet=bet_dec,
            payout=payout,
            server_seed_hash=SEEDS["server_seed_hash"],
            client_seed=body.client_seed,
            nonce=nonce,
            result_json={"multiplier": mult},
        )
        s.add(row)
        s.flush()

        acc.balance -= bet_dec
        s.add(Ledger(user_id=user.id, amount=-bet_dec, balance=acc.balance, meta={"type": "bet", "round_id": row.id}))

        acc.balance += payout
        s.add(Ledger(user_id=user.id, amount=payout, balance=acc.balance, meta={"type": "payout", "round_id": row.id}))

        s.commit()
        s.refresh(row)
        _update_rtp(row.bet, row.payout)
        return RoundOut(
            round_id=row.id,
            bet=float(row.bet),
            payout=float(row.payout),
            multiplier=float(mult),
            new_balance=float(acc.balance),
            server_seed_hash=row.server_seed_hash,
            client_seed=row.client_seed,
            nonce=row.nonce,
            created_at=row.created_at.isoformat()
        )

@app.post("/crash/round", response_model=RoundOut)
def play_round_alias(body: BetRoundIn, user: User = Depends(get_current_user())):
    return play_round(body, user)

@app.get("/history", response_model=HistoryResp)
def history(limit: int = 20, user: User = Depends(get_current_user())):
    with Session(engine) as s:
        q = (
            select(Round)
            .where(Round.user_id == user.id)
            .order_by(Round.id.desc())
            .limit(limit)
        )
        items = s.scalars(q).all()
        out = []
        for r in items:
            out.append(RoundOut(
                round_id=r.id,
                bet=float(r.bet),
                payout=float(r.payout),
                multiplier=float(r.result_json.get("multiplier", 0)),
                new_balance=-1.0,  # no recalculamos aquí
                server_seed_hash=r.server_seed_hash,
                client_seed=r.client_seed,
                nonce=r.nonce,
                created_at=r.created_at.isoformat()
            ))
        return {"rounds": out}

@app.post("/seeds/rotate")
def rotate_seed():
    old_hash = SEEDS["server_seed_hash"]
    SEEDS["server_seed"] = os.urandom(32).hex()
    SEEDS["server_seed_hash"] = _hash_seed(SEEDS["server_seed"])
    SEEDS["nonce"] = 0
    return {"ok": True, "old_server_seed_hash": old_hash, "new_server_seed_hash": SEEDS["server_seed_hash"]}


BASE_DIR = Path(__file__).resolve().parent
app.mount("/", StaticFiles(directory=BASE_DIR / "public", html=True), name="public")

# ---------- Admin Endpoints ----------
@app.get("/admin/rounds")
def admin_rounds(limit: int = 100, _: str = Depends(require_admin)):
    with Session(engine) as s:
        q = select(Round).order_by(Round.id.desc()).limit(limit)
        items = s.scalars(q).all()
        out = []
        for r in items:
            out.append({
                "id": r.id,
                "user_id": r.user_id,
                "bet": float(r.bet),
                "payout": float(r.payout),
                "created_at": r.created_at.isoformat(),
            })
        return {"rounds": out}

@app.get("/admin/ledger")
def admin_ledger(user_id: Optional[str] = None, limit: int = 100, _: str = Depends(require_admin)):
    with Session(engine) as s:
        q = select(Ledger)
        if user_id:
            q = q.where(Ledger.user_id == user_id)
        q = q.order_by(Ledger.id.desc()).limit(limit)
        items = s.scalars(q).all()
        out = []
        for l in items:
            out.append({
                "id": l.id,
                "user_id": l.user_id,
                "amount": float(l.amount),
                "balance": float(l.balance),
                "meta": l.meta,
                "created_at": l.created_at.isoformat(),
            })
        return {"ledger": out}

@app.post("/admin/rng/rotate")
def admin_rotate_rng(_: str = Depends(require_admin)):
    return rotate_seed()

# ---------- Static Files ----------
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="public", html=True), name="public")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "public" / "index.html")
