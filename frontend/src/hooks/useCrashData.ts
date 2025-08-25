import { useEffect, useRef, useState } from "react";
import { API_URL, WS_URL } from "@/lib/env";
import { postJSON } from "@/lib/http";

type Phase = "BETTING" | "RUNNING" | "CRASHED";
export function useCrashData() {
  const [phase, setPhase] = useState<Phase>("BETTING");
  const [multiplier, setMultiplier] = useState(1);
  const [minBet, setMinBet] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Carga inicial
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_URL}/crash/state`, { credentials: "include" });
        const d = await r.json();
        if (d.phase) setPhase(d.phase);
        if (typeof d.multiplier === "number") setMultiplier(d.multiplier);
        if (typeof d.min_bet === "number") setMinBet(d.min_bet);
      } catch (e: any) {
        setError(e?.message ?? "Error inicial");
      }
    })();
  }, []);

  // WS
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/crash/stream`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.t === "state") {
          if (msg.phase) setPhase(msg.phase);
          if (typeof msg.m === "number") setMultiplier(msg.m);
          if (typeof msg.min_bet === "number") setMinBet(msg.min_bet);
        } else if (msg.t === "start") {
          setPhase("RUNNING");
          setMultiplier(1);
        } else if (msg.t === "tick") {
          setPhase("RUNNING");
          if (typeof msg.m === "number") setMultiplier(msg.m);
        } else if (msg.t === "crash") {
          setPhase("CRASHED");
        } else if (msg.t === "betting") {
          setPhase("BETTING");
          setMultiplier(1);
        }
      } catch {}
    };
    ws.onerror = () => setError("WS error");
    ws.onclose = () => {};
    return () => ws.close();
  }, []);

  async function bet(amount: number, auto?: number | null) {
    return postJSON("/crash/bet", { amount, auto_cashout: auto ?? null });
  }

  async function cashout() {
    return postJSON("/crash/cashout", {});
  }

  return { phase, multiplier, minBet, error, bet, cashout };
}
