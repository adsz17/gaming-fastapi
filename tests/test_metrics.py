import types

import pytest
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry, Counter
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from backend import main
from backend.models import Base


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    main.engine = engine

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

    main.WALLET_URL = "http://wallet"
    main.RNG_URL = "http://rng"
    main.httpx.post = fake_post  # type: ignore
    main.registry = CollectorRegistry()
    main.rtp_observed = Counter(
        "rtp_observed", "Observed Return To Player", registry=main.registry
    )
    return TestClient(main.app)


def test_metrics_increment(client: TestClient):
    body = {"bet": 10, "client_seed": "s", "idem": "k"}
    assert client.post("/crash/round", json=body).status_code == 200
    metrics = client.get("/metrics").text
    assert "rtp_observed_total" in metrics
    line = [ln for ln in metrics.splitlines() if ln.startswith("rtp_observed_total")][0]
    assert float(line.split()[1]) == 20.0
