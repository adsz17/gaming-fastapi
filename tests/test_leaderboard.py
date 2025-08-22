import os
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"

import api.main as main  # noqa: E402
from api.models import Base, User, Wallet  # noqa: E402
import api.db as db  # noqa: E402
import api.auth as auth  # noqa: E402

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


def _create_user(email: str, username: str, balance: float):
    with Session(db.engine) as s, s.begin():
        uid = str(uuid.uuid4())
        user = User(id=uid, email=email, username=username, password_hash="x")
        s.add(user)
        s.add(Wallet(user_id=uid, balance=balance))
    return uid


def test_leaderboard():
    _create_user("a@a.com", "alice", 300)
    _create_user("b@b.com", "bob", 500)
    _create_user("c@c.com", "carol", 200)
    resp = client.get("/leaderboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["username"] == "bob"
    assert data[0]["balance"] == 500.0
    assert len(data) == 3
