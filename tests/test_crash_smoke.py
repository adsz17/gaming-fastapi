import os
import sys
from pathlib import Path
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool

from api.crash.engine import CrashEngine
import api.crash.router as crash_router
from api.models import CrashBet, Base

# Ensure project backend on path and set dummy DATABASE_URL before importing app
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"

import api.main as main  # noqa: E402
import api.db as db  # noqa: E402
import api.auth as auth  # noqa: E402


# In-memory SQLite for tests
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db.engine = test_engine
auth.engine = test_engine
db.SessionLocal.configure(bind=test_engine)
Base.metadata.drop_all(db.engine)
Base.metadata.create_all(db.engine)

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(db.engine)
    Base.metadata.create_all(db.engine)
    yield


@pytest.fixture(autouse=True)
def _fresh_engine():
    eng = CrashEngine()
    eng.on_crash = crash_router.handle_crash
    main.app.state.crash_engine = eng
    yield


def _register_user(email: str = "a@example.com"):
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "username": "user", "password": "secret"},
    )
    assert resp.status_code == 201
    data = resp.json()
    uid = data["user"]["id"]
    token = data["token"]
    return uid, {"Authorization": f"Bearer {token}"}


def test_bet_amount_zero():
    uid, headers = _register_user()
    r = client.post("/crash/bet", json={"amount": 0}, headers=headers)
    assert r.status_code == 422


def test_cashout_in_betting_phase():
    uid, headers = _register_user("b@example.com")
    r = client.post("/crash/cashout", headers=headers)
    assert r.status_code == 409


def test_cashout_is_idempotent():
    uid, headers = _register_user("c@example.com")
    engine = main.app.state.crash_engine
    engine.phase = "RUNNING"
    engine.multiplier = 2.0
    engine.bets[uid] = {
        "amount": 10.0,
        "auto": None,
        "cashed": False,
        "payout": None,
        "cash_at": None,
    }
    r1 = client.post("/crash/cashout", headers=headers)
    assert r1.status_code == 200
    data1 = r1.json()
    r2 = client.post("/crash/cashout", headers=headers)
    assert r2.status_code == 200
    assert r2.json() == data1


def test_wallet_and_cashout_flow():
    uid, headers = _register_user("d@example.com")
    engine = main.app.state.crash_engine
    engine.started = True  # evitar autostart
    r = client.post("/crash/bet", json={"amount": 10}, headers=headers)
    assert r.status_code == 201
    bal_after_bet = client.get("/wallet/balance", headers=headers).json()["balance"]
    assert bal_after_bet == 90.0
    engine.phase = "RUNNING"
    engine.multiplier = 2.0
    engine.crash_at = 10.0
    r2 = client.post("/crash/cashout", headers=headers)
    assert r2.status_code == 200
    bal_after_cash = client.get("/wallet/balance", headers=headers).json()["balance"]
    assert bal_after_cash == 110.0
    with db.SessionLocal() as s:
        bet = s.scalar(select(CrashBet))
        assert bet.status == "CASHED"


def test_phase_cycle():
    uid, headers = _register_user("e@example.com")
    engine = main.app.state.crash_engine
    engine._gen_crash_at = lambda: 1.01
    r = client.post("/crash/bet", json={"amount": 10}, headers=headers)
    assert r.status_code == 201
    # esperar a que crashee y reinicie
    time.sleep(0.5)
    assert engine.phase == "BETTING"
