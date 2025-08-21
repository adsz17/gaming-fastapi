import hashlib
import hmac
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

HOUSE_EDGE = float(os.getenv("RNG_HOUSE_EDGE", "0.01"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

app = FastAPI(title="RNG Service")

SEEDS: Dict[str, Any] = {
    "server_seed": os.urandom(32).hex(),
    "server_seed_hash": "",
    "nonce": 0
}

def _hash_seed(seed_hex: str) -> str:
    return hashlib.sha256(bytes.fromhex(seed_hex)).hexdigest()

SEEDS["server_seed_hash"] = _hash_seed(SEEDS["server_seed"])


def hmac_sha256(server_seed_hex: str, message: str) -> str:
    key = bytes.fromhex(server_seed_hex)
    return hmac.new(key, message.encode(), hashlib.sha256).hexdigest()


def verify_signature(message: str, signature: str) -> bool:
    """Verify an HMAC-SHA256 signature against the current server seed."""
    expected = hmac_sha256(SEEDS["server_seed"], message)
    return hmac.compare_digest(expected, signature)


def hex_to_unit(hex_str: str) -> float:
    sl = hex_str[:13]
    val = int(sl, 16)
    return min(1.0 - 1e-12, max(0.0, val / float(16 ** 13)))


def crash_multiplier(server_seed_hex: str, client_seed: str, nonce: int, house_edge: float) -> float:
    digest = hmac_sha256(server_seed_hex, f"{client_seed}:{nonce}")
    u = hex_to_unit(digest)
    m = 1.0 / max(1e-12, (1.0 - (u * (1.0 - house_edge))))
    m = min(100.0, m)
    return float(f"{m:.2f}")


class CrashReq(BaseModel):
    client_seed: str


class CrashResp(BaseModel):
    nonce: int
    multiplier: float
    server_seed_hash: str
    signature: str


class RotateResp(BaseModel):
    previous_server_seed: str
    previous_server_seed_hash: str
    new_server_seed_hash: str


@app.post("/rng/crash", response_model=CrashResp)
def rng_crash(body: CrashReq):
    SEEDS["nonce"] += 1
    nonce = SEEDS["nonce"]
    mult = crash_multiplier(SEEDS["server_seed"], body.client_seed, nonce, HOUSE_EDGE)
    msg = f"{body.client_seed}:{nonce}:{mult}"
    sig = hmac_sha256(SEEDS["server_seed"], msg)
    return {
        "nonce": nonce,
        "multiplier": mult,
        "server_seed_hash": SEEDS["server_seed_hash"],
        "signature": sig,
    }


@app.post("/rng/rotate", response_model=RotateResp)
def rng_rotate(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    prev_seed = SEEDS["server_seed"]
    prev_hash = SEEDS["server_seed_hash"]
    new_seed = os.urandom(32).hex()
    new_hash = _hash_seed(new_seed)
    SEEDS.update({"server_seed": new_seed, "server_seed_hash": new_hash, "nonce": 0})
    return {
        "previous_server_seed": prev_seed,
        "previous_server_seed_hash": prev_hash,
        "new_server_seed_hash": new_hash,
    }
