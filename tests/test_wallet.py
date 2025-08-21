import os
from decimal import Decimal

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

# Ensure project root on path and set dummy DATABASE_URL before importing app
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"

from backend import main  # noqa: E402
from backend.models import Base, LedgerEntry

# Configure in-memory SQLite for tests
from sqlalchemy.pool import StaticPool

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.drop_all(test_engine)
Base.metadata.create_all(test_engine)
main.engine = test_engine

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def _register_user(email: str = "a@example.com", password: str = "secret"):
    resp = client.post("/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["token"]


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
    with Session(test_engine) as s:
        count = s.scalar(select(func.count()).select_from(LedgerEntry))
        assert count == 1


def test_insufficient_funds():
    token = _register_user("b@example.com")
    headers = _auth_header(token)
    body = {"amount": -200, "reason": "wd", "idempotency_key": "w1"}
    r = client.post("/wallet/txn", json=body, headers=headers)
    assert r.status_code == 400
    with Session(test_engine) as s:
        count = s.scalar(select(func.count()).select_from(LedgerEntry))
        assert count == 0
