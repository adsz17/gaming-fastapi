import argparse
import os
from typing import Optional, Tuple

import numpy as np

import hmac
import hashlib


def crash_multiplier(server_seed_hex: str, client_seed: str, nonce: int, house_edge: float = 0.01) -> float:
    digest = hmac.new(bytes.fromhex(server_seed_hex), f"{client_seed}:{nonce}".encode(), hashlib.sha256).hexdigest()
    sl = digest[:13]
    u = int(sl, 16) / float(16 ** 13)
    m = 1.0 / max(1e-12, (1.0 - (u * (1.0 - house_edge))))
    m = min(100.0, m)
    return float(f"{m:.2f}")


def run_simulation(iterations: int, server_seed: Optional[str] = None, client_seed: str = "simulation") -> Tuple[float, float, float, float, float]:
    """Run `iterations` crash multipliers and compute statistics.

    Returns a tuple with (rtp, mean, p50, p95, p99).
    """
    if server_seed is None:
        server_seed = os.urandom(32).hex()

    multipliers = np.empty(iterations, dtype=np.float64)
    for i in range(iterations):
        multipliers[i] = crash_multiplier(server_seed, client_seed, i + 1)

    total_payout = multipliers.sum()
    rtp = total_payout / iterations
    mean = multipliers.mean()
    p50, p95, p99 = np.percentile(multipliers, [50, 95, 99])
    return rtp, mean, p50, p95, p99


def main():
    parser = argparse.ArgumentParser(description="Simulate crash RNG and compute RTP and statistics")
    parser.add_argument("--iterations", "-n", type=int, default=10_000_000, help="Number of rounds to simulate")
    parser.add_argument("--server-seed", dest="server_seed", default=None, help="Hex server seed. Random if omitted")
    parser.add_argument("--client-seed", dest="client_seed", default="simulation", help="Client seed to use")
    args = parser.parse_args()

    rtp, mean, p50, p95, p99 = run_simulation(args.iterations, args.server_seed, args.client_seed)
    print(f"Iterations: {args.iterations}")
    print(f"RTP: {rtp:.4f}")
    print(f"Mean: {mean:.4f}")
    print(f"P50: {p50:.4f}")
    print(f"P95: {p95:.4f}")
    print(f"P99: {p99:.4f}")


if __name__ == "__main__":
    main()
