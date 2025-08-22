import { useGameStore } from "@/lib/store";
import Button from "./ui/button";
import Input from "./ui/input";
import Card from "./ui/card";
import { useToast } from "./ui/toast";

export default function BetPanel() {
  const {
    bet,
    setBet,
    autoCashout,
    setAutoCashout,
    phase,
    setPhase,
    balance,
    setBalance,
  } = useGameStore();
  const toast = useToast();

  const handleBet = () => {
    if (bet > balance) {
      toast("Insufficient balance");
      return;
    }
    setBalance(balance - bet);
    setPhase("betting");
  };

  const handleCashout = () => {
    setPhase("idle");
    toast(`Cashed out at ${useGameStore.getState().multiplier.toFixed(2)}x`);
  };

  return (
    <Card className="space-y-4">
      <div className="flex items-center gap-2">
        <Input
          type="number"
          value={bet}
          onChange={(e) => setBet(Number(e.target.value))}
          className="w-full"
        />
        <Button onClick={() => setBet(bet / 2)}>1/2</Button>
        <Button onClick={() => setBet(bet * 2)}>2x</Button>
      </div>
      <Input
        type="number"
        value={autoCashout}
        onChange={(e) => setAutoCashout(Number(e.target.value))}
        placeholder="Auto cashout"
        className="w-full"
      />
      {phase === "flying" ? (
        <Button className="w-full bg-neon-pink" onClick={handleCashout}>
          Cashout
        </Button>
      ) : (
        <Button className="w-full bg-neon-blue" onClick={handleBet} disabled={phase !== "idle"}>
          Bet
        </Button>
      )}
    </Card>
  );
}
