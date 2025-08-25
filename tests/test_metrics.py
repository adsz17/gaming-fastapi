import os
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry, Counter
from api.auth import _create_token
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg://user:pass@localhost/test"
os.environ["RATE_LIMIT_PER_MIN"] = "1000"

import api.main as main  # noqa: E402
from api.models import Base  # noqa: E402
import api.db as db  # noqa: E402
import api.routers.crash as crash_router  # noqa: E402
import api.routers.metrics as metrics_router  # noqa: E402


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    db.engine = engine
    db.SessionLocal.configure(bind=engine)

    user = types.SimpleNamespace(id="u1", email="u@example.com")
    dep = None
    for route in main.app.routes:
        if getattr(route, "path", None) == "/crash/round":
            dep = route.dependant.dependencies[0].call
            break
    assert dep is not None
    main.app.dependency_overrides[dep] = lambda: user

    def fake_post(url, json=None, headers=None):
        class Resp:
            def json(self):
                if "rng" in url:
                    return {"multiplier": 2.0, "nonce": 1, "server_seed_hash": "hash"}
                return {"balance": 100}

            def raise_for_status(self) -> None:
                pass

        return Resp()

    crash_router.WALLET_URL = "http://wallet"
    crash_router.RNG_URL = "http://rng"
    crash_router.httpx.post = fake_post  # type: ignore
    metrics_router.registry = CollectorRegistry()
    metrics_router.rtp_observed = Counter(
        "rtp_observed", "Observed Return To Player", registry=metrics_router.registry
    )
    crash_router.rtp_observed = metrics_router.rtp_observed
    return TestClient(main.app)


def test_metrics_increment(client: TestClient):
    body = {"bet": 10, "client_seed": "s", "idem": "k"}
    token = _create_token("u1")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/crash/round", json=body, headers=headers).status_code == 200
    metrics = client.get("/metrics").text
    assert "rtp_observed_total" in metrics
    line = [ln for ln in metrics.splitlines() if ln.startswith("rtp_observed_total")][0]
    assert float(line.split()[1]) == 20.0
