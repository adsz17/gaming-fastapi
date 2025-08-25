import asyncio, math, os, time, uuid, random
from typing import Dict, Optional, Set
from fastapi import WebSocket

CRASH_MIN_BET = float(os.getenv("CRASH_MIN_BET", "1"))
CRASH_TICK_MS = int(os.getenv("CRASH_TICK_MS", "100"))
CRASH_GROWTH_RATE = float(os.getenv("CRASH_GROWTH_RATE", "0.06"))
CRASH_INTERMISSION_SECONDS = float(os.getenv("CRASH_INTERMISSION_SECONDS", "4"))

class CrashEngine:
    def __init__(self) -> None:
        self.phase: str = "BETTING"  # BETTING | RUNNING | CRASHED
        self.round_id: str = str(uuid.uuid4())
        self.multiplier: float = 1.0
        self.crash_at: Optional[float] = None
        self.started: bool = False  # si ya arrancó la ronda actual
        self.bets: Dict[str, Dict] = {}  # player_id -> {amount, cashed:bool, payout:Optional[float], cash_at:Optional[float]}
        self.connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._runner_task: Optional[asyncio.Task] = None

    # --------- utilidades ----------
    def _gen_crash_at(self) -> float:
        # cola pesada simple (exponencial) + pequeños límites
        u = random.random()
        base = 1 + (-math.log(max(1e-9, 1 - u)))
        return round(max(1.01, base), 2)

    async def _broadcast(self, msg: dict) -> None:
        dead = []
        for ws in list(self.connections):
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.connections.discard(ws)

    # --------- API pública ----------
    async def subscribe(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)
        # estado inicial compacto
        await ws.send_json({"t": "state", "phase": self.phase, "m": self.multiplier, "rid": self.round_id})

    async def place_bet(self, player_id: str, amount: float, auto: Optional[float] = None):
        if amount < CRASH_MIN_BET:
            raise ValueError("MIN_BET")
        async with self._lock:
            if self.phase != "BETTING":
                raise RuntimeError("NOT_BETTING")
            if player_id in self.bets:
                raise RuntimeError("ALREADY_BET")
            self.bets[player_id] = {
                "amount": float(amount),
                "auto": auto,
                "cashed": False,
                "payout": None,
                "cash_at": None,
            }
            await self._broadcast({"t": "player_bet", "a": amount})
            # si es la primera apuesta de la ronda, arrancamos
            if not self.started:
                self.started = True
                self.crash_at = self._gen_crash_at()
                self.phase = "RUNNING"
                self.multiplier = 1.0
                if self._runner_task is None or self._runner_task.done():
                    # El loop se dispara únicamente acá
                    self._runner_task = asyncio.create_task(self._run_loop())

    async def cashout(self, player_id: str):
        async with self._lock:
            if self.phase != "RUNNING":
                raise RuntimeError("NOT_RUNNING")
            bet = self.bets.get(player_id)
            if not bet:
                raise RuntimeError("NO_ACTIVE_BET")
            if bet["cashed"]:
                return {"at": bet["cash_at"], "payout": bet["payout"]}
            bet["cashed"] = True
            bet["payout"] = round(bet["amount"] * self.multiplier, 2)
            bet["cash_at"] = self.multiplier
            await self._broadcast({"t": "player_cash", "at": self.multiplier, "p": bet["payout"]})
            return {"at": bet["cash_at"], "payout": bet["payout"]}

    async def state(self, player_id: Optional[str] = None):
        you = None
        if player_id and player_id in self.bets:
            b = self.bets[player_id]
            you = {"amount": b["amount"], "cashed": b["cashed"], "payout": b["payout"], "auto": b["auto"]}
        return {
            "round_id": self.round_id,
            "phase": self.phase,
            "multiplier": self.multiplier,
            "your_bet": you,
            "min_bet": CRASH_MIN_BET,
        }

    # --------- loop de ejecución ----------
    async def _run_loop(self):
        # corre hasta crash; luego CRASHED un rato; luego reset a BETTING
        t0 = time.perf_counter()
        await self._broadcast({"t": "start", "rid": self.round_id, "at": self.crash_at})
        try:
            while True:
                await asyncio.sleep(CRASH_TICK_MS / 1000.0)
                # crecimiento exponencial suave
                self.multiplier = round(math.exp(CRASH_GROWTH_RATE * (time.perf_counter() - t0)), 2)
                await self._broadcast({"t": "tick", "m": self.multiplier})
                # auto cashout
                for pid, b in list(self.bets.items()):
                    if not b["cashed"] and b["auto"] and self.multiplier >= float(b["auto"]):
                        b["cashed"] = True
                        b["payout"] = round(b["amount"] * self.multiplier, 2)
                        b["cash_at"] = self.multiplier
                        await self._broadcast({"t": "player_cash", "at": self.multiplier, "p": b["payout"]})
                if self.crash_at and self.multiplier >= self.crash_at:
                    break
        finally:
            # CRASH!
            self.phase = "CRASHED"
            await self._broadcast({"t": "crash", "at": self.crash_at})
            # liquidar perdedores (sin cashout)
            for pid, b in self.bets.items():
                if not b["cashed"]:
                    b["payout"] = 0.0
            await asyncio.sleep(CRASH_INTERMISSION_SECONDS)
            # reset
            self.phase = "BETTING"
            self.round_id = str(uuid.uuid4())
            self.multiplier = 1.0
            self.crash_at = None
            self.started = False
            self.bets.clear()
            self._runner_task = None
            await self._broadcast({"t": "betting", "rid": self.round_id})
