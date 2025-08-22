import os
import os
import sys
import types
from pathlib import Path

os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/db"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from api.auth import _create_token

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "backend"))

import api.main as main
from api.models import Base, Round
import api.db as db
import api.routers.crash as crash_router
import api.auth as auth


def test_round_idempotency(monkeypatch):
    if os.path.exists("test.db"):
        os.remove("test.db")
    engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
    db.engine = engine
    auth.engine = engine
    db.SessionLocal.configure(bind=engine)
    Base.metadata.create_all(engine)

    # dummy user
    user = types.SimpleNamespace(id="u1", email="u@example.com")
    dep = None
    for route in main.app.routes:
        if getattr(route, "path", None) == "/crash/round":
            dep = route.dependant.dependencies[0].call
            break
    assert dep is not None
    main.app.dependency_overrides[dep] = lambda: user

    calls = []
    balance = 100.0

    def fake_post(url, json=None, headers=None):
        nonlocal balance
        key = json.get("idempotency_key")
        if key:
            calls.append((url, key))
        if "wallet" in url:
            balance += json["amount"]
            class Resp:
                def json(self):
                    return {"balance": balance}
                def raise_for_status(self):
                    pass
            return Resp()
        elif "rng" in url:
            class Resp:
                def json(self):
                    return {"multiplier": 2.0, "nonce": 1, "server_seed_hash": "hash"}
                def raise_for_status(self):
                    pass
            return Resp()
        raise AssertionError("unexpected url")

    monkeypatch.setattr(crash_router.httpx, "post", fake_post)
    crash_router.WALLET_URL = "http://wallet"
    crash_router.RNG_URL = "http://rng"

    client = TestClient(main.app)
    body = {"bet": 10, "client_seed": "cs", "idem": "abc"}
    token1 = _create_token("rate1")
    token2 = _create_token("rate2")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    r1 = client.post("/crash/round", json=body, headers=headers1)
    assert r1.status_code == 200
    r2 = client.post("/crash/round", json=body, headers=headers2)
    assert r2.status_code == 200
    assert r1.json()["round_id"] == r2.json()["round_id"]
    assert len(calls) == 2

    with Session(engine) as s:
        count = s.scalar(select(func.count()).select_from(Round))
        assert count == 1

