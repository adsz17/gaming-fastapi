import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# Ensure project backend on path and set dummy DATABASE_URL before importing app
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"

import api.main as main  # noqa: E402
from api.models import Base, LedgerEntry  # noqa: E402
import api.db as db  # noqa: E402


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db.engine = test_engine
db.SessionLocal.configure(bind=test_engine)
Base.metadata.drop_all(db.engine)
Base.metadata.create_all(db.engine)

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(db.engine)
    Base.metadata.create_all(db.engine)
    yield


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def _register_user(email: str = "a@example.com", password: str = "secret"):
    resp = client.post("/api/auth/register", json={"email": email, "username": "u", "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_idempotent_txn():
    token = _register_user()
    headers = _auth_header(token)
    body = {"amount": 10, "reason": "dep", "idempotency_key": "abc"}
    r1 = client.post("/wallet/txn", json=body, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["balance"] == 110.0
    r2 = client.post("/wallet/txn", json=body, headers=headers)
    assert r2.status_code == 200
    assert r2.json() == r1.json()
    with Session(db.engine) as s:
        count = s.scalar(select(func.count()).select_from(LedgerEntry))
        assert count == 1


def test_insufficient_funds():
    token = _register_user("b@example.com")
    headers = _auth_header(token)
    body = {"amount": -200, "reason": "wd", "idempotency_key": "w1"}
    r = client.post("/wallet/txn", json=body, headers=headers)
    assert r.status_code == 400
    with Session(db.engine) as s:
        count = s.scalar(select(func.count()).select_from(LedgerEntry))
        assert count == 0
