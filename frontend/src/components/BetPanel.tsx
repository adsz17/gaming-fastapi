import { useCrashData } from "@/hooks/useCrashData";
import { useState } from "react";
import Button from "./ui/button";
import Input from "./ui/input";
import Card from "./ui/card";

export default function BetPanel() {
  const { phase, multiplier, minBet, bet, cashout } = useCrashData();
  const [amount, setAmount] = useState<number>(minBet);

  const betDisabled = phase !== "BETTING" || !amount || amount < minBet;
  const cashDisabled = phase !== "RUNNING";

  return (
    <Card className="space-y-4">
      <div className="text-6xl font-extrabold text-[#39FF14] text-center">
        {multiplier.toFixed(2)}x
      </div>

      <Input
        type="number"
        min={minBet}
        value={amount}
        onChange={(e) => setAmount(Number(e.target.value))}
        className="w-full"
      />
      <Button
        disabled={betDisabled}
        className="w-full bg-neon-blue"
        onClick={async () => {
          try {
            await bet(amount);
          } catch (e) {
            console.error(e);
          }
        }}
      >
        Bet
      </Button>

      <Button
        disabled={cashDisabled}
        className="w-full bg-neon-pink"
        onClick={() => cashout().catch(console.error)}
      >
        Cashout
      </Button>

      {phase === "BETTING" && (
        <p className="text-xs text-slate-400">
          Esperando apuestas (mín: {minBet})…
        </p>
      )}
      {phase === "CRASHED" && (
        <p className="text-xs text-rose-400">
          💥 Crash! Nueva ronda en segundos…
        </p>
      )}
    </Card>
  );
}
