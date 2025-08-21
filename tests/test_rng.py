import os
import hmac
import hashlib
from fastapi.testclient import TestClient

# Ensure env vars before importing service
os.environ.setdefault("ADMIN_TOKEN", "test-token")
os.environ.setdefault("RNG_HOUSE_EDGE", "0.01")

from backend.services.rng import app

client = TestClient(app)


def test_signature_valid():
    body = {"client_seed": "abc"}
    r = client.post("/rng/crash", json=body)
    data = r.json()
    rotate = client.post("/rng/rotate", headers={"X-Admin-Token": os.environ["ADMIN_TOKEN"]})
    rot = rotate.json()

    assert data["server_seed_hash"] == rot["previous_server_seed_hash"]
    msg = f"{body['client_seed']}:{data['nonce']}:{data['multiplier']}"
    expected_sig = hmac.new(bytes.fromhex(rot["previous_server_seed"]), msg.encode(), hashlib.sha256).hexdigest()
    assert data["signature"] == expected_sig


def test_nonce_incremental():
    client.post("/rng/rotate", headers={"X-Admin-Token": os.environ["ADMIN_TOKEN"]})
    body = {"client_seed": "seed"}
    r1 = client.post("/rng/crash", json=body).json()
    r2 = client.post("/rng/crash", json=body).json()
    assert r2["nonce"] == r1["nonce"] + 1


def test_distribution_not_constant():
    client.post("/rng/rotate", headers={"X-Admin-Token": os.environ["ADMIN_TOKEN"]})
    body = {"client_seed": "seed"}
    mults = [client.post("/rng/crash", json=body).json()["multiplier"] for _ in range(20)]
    assert len(set(mults)) > 1
