import asyncio
import math
import os
import random
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional, Set

from fastapi import WebSocket


@dataclass
class Bet:
    amount: float
    auto_cashout: Optional[float]
    cashed: bool = False


class CrashEngine:
    """Simple in-memory crash game engine with rounds."""

    def __init__(self) -> None:
        self.betting_seconds = float(os.getenv("CRASH_BETTING_SECONDS", "6"))
        self.intermission_seconds = float(os.getenv("CRASH_INTERMISSION_SECONDS", "4"))
        self.tick_ms = int(os.getenv("CRASH_TICK_MS", "100"))
        self.growth_rate = float(os.getenv("CRASH_GROWTH_RATE", "0.06"))
        self.min_bet = float(os.getenv("CRASH_MIN_BET", "1"))
        self.house_edge = float(os.getenv("CRASH_HOUSE_EDGE", "0.01"))

        self.round_id = 0
        self.phase = "BETTING"
        self.multiplier = 1.0
        self.seconds_left = self.betting_seconds
        self.crash_at = 1.0

        self.bets: Dict[str, Bet] = {}
        self.balances: Dict[str, float] = defaultdict(float)
        self.websockets: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    def _generate_crash_at(self) -> float:
        u = random.random()
        base = 1 + (-math.log(1 - u))
        crash_at = round(max(1.01, base * (1 - self.house_edge)), 2)
        return crash_at

    async def run(self) -> None:
        """Main engine loop."""
        while True:
            self.round_id += 1
            self.phase = "BETTING"
            self.bets = {}
            start = time.time()
            while True:
                elapsed = time.time() - start
                left = self.betting_seconds - elapsed
                self.seconds_left = max(0.0, round(left, 2))
                await self.broadcast({"t": "betting", "left": self.seconds_left})
                if left <= 0:
                    break
                await asyncio.sleep(0.5)

            self.phase = "RUNNING"
            self.multiplier = 1.0
            self.crash_at = self._generate_crash_at()
            t0 = time.time()
            while True:
                elapsed = time.time() - t0
                m = round(math.exp(self.growth_rate * elapsed), 2)
                self.multiplier = m
                await self.broadcast({"t": "tick", "m": m})

                async with self.lock:
                    for pid, bet in list(self.bets.items()):
                        if not bet.cashed and bet.auto_cashout is not None and m >= bet.auto_cashout:
                            await self._cashout(pid, m)

                if m >= self.crash_at:
                    self.phase = "CRASHED"
                    await self.broadcast({"t": "crash", "at": self.crash_at})
                    async with self.lock:
                        for pid, bet in self.bets.items():
                            if not bet.cashed:
                                self.balances[pid] -= bet.amount
                                bet.cashed = True
                    break
                await asyncio.sleep(self.tick_ms / 1000)

            await asyncio.sleep(self.intermission_seconds)

    async def broadcast(self, data: dict) -> None:
        dead: Set[WebSocket] = set()
        for ws in self.websockets:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.websockets.discard(ws)

    async def place_bet(self, player_id: str, amount: float, auto: Optional[float]) -> None:
        if self.phase != "BETTING":
            raise RuntimeError("not_betting")
        if amount < self.min_bet:
            raise ValueError("min_bet")
        async with self.lock:
            if player_id in self.bets:
                raise RuntimeError("already_bet")
            self.bets[player_id] = Bet(amount=amount, auto_cashout=auto)
        await self.broadcast({"t": "player_bet", "amount": amount})

    async def _cashout(self, player_id: str, at: float) -> float:
        bet = self.bets[player_id]
        bet.cashed = True
        payout = round(bet.amount * at, 2)
        self.balances[player_id] += payout
        await self.broadcast({"t": "player_cashout", "at": at, "payout": payout})
        return payout

    async def cashout(self, player_id: str) -> dict:
        if self.phase != "RUNNING":
            raise RuntimeError("not_running")
        async with self.lock:
            bet = self.bets.get(player_id)
            if not bet or bet.cashed:
                raise RuntimeError("no_bet")
            m = self.multiplier
            if m >= self.crash_at:
                raise RuntimeError("crashed")
            payout = await self._cashout(player_id, m)
            return {"at": m, "payout": payout}

    def get_state(self, player_id: Optional[str]) -> dict:
        bet_info = None
        if player_id and player_id in self.bets:
            b = self.bets[player_id]
            bet_info = {
                "amount": b.amount,
                "auto_cashout": b.auto_cashout,
                "cashed_out": b.cashed,
            }
        return {
            "round_id": self.round_id,
            "phase": self.phase,
            "multiplier": self.multiplier,
            "seconds_left": self.seconds_left,
            "crash_at": self.crash_at if self.phase == "CRASHED" else None,
            "your_bet": bet_info,
            "your_balance": self.balances.get(player_id or "", 0.0),
        }


engine = CrashEngine()
