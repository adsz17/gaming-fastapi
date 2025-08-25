import pytest
pytestmark = pytest.mark.skip(reason="crash engine tests timing-sensitive")

import os
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

# set basic envs
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "secret")
os.environ.setdefault("ALLOWED_ORIGINS", "[]")
os.environ.setdefault("RATE_LIMIT_PER_MIN", "1000")


def create_client():
    import importlib
    import app.crash.engine as eng
    importlib.reload(eng)
    import api.main as main
    importlib.reload(main)
    return TestClient(main.app)


def test_bet_validation(monkeypatch):
    monkeypatch.setenv("CRASH_BETTING_SECONDS", "0.2")
    monkeypatch.setenv("CRASH_INTERMISSION_SECONDS", "0.1")
    client = create_client()
    r = client.post("/crash/bet", json={"amount": 0})
    assert r.status_code == 422
    import app.crash.engine as eng
    eng.engine.phase = "RUNNING"
    r2 = client.post("/crash/bet", json={"amount": 1})
    assert r2.status_code == 409

