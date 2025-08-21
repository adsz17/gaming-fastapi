import os
import sys
import time
from importlib import reload

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def create_client(exp: str, limit: int | None = None) -> TestClient:
    os.environ["JWT_EXPIRES_MIN"] = exp
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    if limit is not None:
        os.environ["RATE_LIMIT_PER_MIN"] = str(limit)
    import backend.main as main
    reload(main)
    return TestClient(main.app)


def test_jwt_expiration():
    with create_client("0") as client:
        res = client.post("/auth/register", json={"email": "a@a.com", "password": "secret"})
        token = res.json()["token"]
        time.sleep(1)
        res_me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 401


def test_rate_limit_block():
    with create_client("60", limit=2) as client:
        client.post("/auth/register", json={"email": "b@b.com", "password": "pw"})
        assert client.post("/auth/login", json={"email": "b@b.com", "password": "pw"}).status_code == 200
        res = client.post("/auth/login", json={"email": "b@b.com", "password": "pw"})
        assert res.status_code == 429
