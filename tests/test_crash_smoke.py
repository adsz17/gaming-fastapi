import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from api.crash.engine import CrashEngine

# Ensure project backend on path and set dummy DATABASE_URL before importing app
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"

import api.main as main  # noqa: E402
from api.models import Base  # noqa: E402
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
    main.app.state.crash_engine = CrashEngine()
    yield


def test_bet_amount_zero():
    r = client.post("/crash/bet", json={"amount": 0})
    assert r.status_code == 422


def test_cashout_in_betting_phase():
    r = client.post("/crash/cashout", json={})
    assert r.status_code == 409


def test_cashout_is_idempotent():
    pid = "pid1"
    engine = main.app.state.crash_engine
    engine.phase = "RUNNING"
    engine.multiplier = 2.0
    engine.bets[pid] = {
        "amount": 10.0,
        "auto": None,
        "cashed": False,
        "payout": None,
        "cash_at": None,
    }
    r1 = client.post("/crash/cashout", cookies={"player_id": pid})
    assert r1.status_code == 200
    data1 = r1.json()
    r2 = client.post("/crash/cashout", cookies={"player_id": pid})
    assert r2.status_code == 200
    assert r2.json() == data1
