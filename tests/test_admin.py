import os
import sys
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# Ensure project backend on path and set dummy DATABASE_URL before importing app
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"

import api.main as main  # noqa: E402
from api.models import Base, User, Wallet  # noqa: E402
import api.db as db  # noqa: E402
import api.security as security  # noqa: E402


# Configure in-memory database
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db.engine = engine
db.SessionLocal.configure(bind=engine, expire_on_commit=False)
Base.metadata.drop_all(db.engine)
Base.metadata.create_all(db.engine)

client = TestClient(main.app)


def _create_user(email: str, is_admin: bool = False, balance: Decimal = Decimal("0")) -> User:
    uid = str(uuid.uuid4())
    user = User(
        id=uid,
        email=email,
        username=email.split("@")[0],
        password_hash="x",
        is_admin=is_admin,
    )
    with Session(db.engine) as s, s.begin():
        s.add(user)
        s.add(Wallet(user_id=user.id, balance=balance))
    class Dummy:
        def __init__(self, id, is_admin):
            self.id = id
            self.is_admin = is_admin
    return Dummy(uid, is_admin)


def test_list_users():
    admin = _create_user("admin@example.com", is_admin=True)
    _create_user("alice@example.com", balance=Decimal("5"))
    token = security.create_token(admin)
    resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    users = resp.json()
    assert any(u["email"] == "alice@example.com" and float(u["balance"]) == 5 for u in users)
