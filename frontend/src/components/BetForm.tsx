import * as React from "react";
import Card from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Tooltip from "@/components/ui/tooltip";
import { useToast } from "@/components/ui/toast";
import { formatMoney } from "@/lib/utils";

interface BetFormProps {
  balance: number;
  onBet: (newBalance: number) => void;
}

export default function BetForm({ balance, onBet }: BetFormProps) {
  const [amount, setAmount] = React.useState(0);
  const [cashout, setCashout] = React.useState<number | "">("");
  const toast = useToast();

  const insufficient = amount > balance;

  const placeBet = () => {
    if (insufficient) {
      toast("Saldo insuficiente");
      return;
    }
    onBet(balance - amount);
    toast(`Apuesta de ${formatMoney(amount)} realizada`);
  };

  return (
    <Card className="space-y-4" aria-label="Formulario de apuesta">
      <div className="flex items-center gap-2">
        <Input
          aria-label="Monto"
          type="number"
          value={amount}
          onChange={(e) => setAmount(Number(e.target.value))}
          className="w-full"
        />
        <Tooltip content="Mitad">
          <Button aria-label="Mitad" onClick={() => setAmount(amount / 2)}>1/2</Button>
        </Tooltip>
        <Tooltip content="Doble">
          <Button aria-label="Doble" onClick={() => setAmount(amount * 2)}>2x</Button>
        </Tooltip>
      </div>
      <Input
        aria-label="Cashout"
        type="number"
        value={cashout}
        onChange={(e) => setCashout(e.target.value ? Number(e.target.value) : "")}
        placeholder="Cashout"
        className="w-full"
      />
      <Button
        aria-label="Bet"
        className="w-full bg-neon-blue text-gray-900"
        onClick={placeBet}
        disabled={insufficient}
      >
        Bet
      </Button>
    </Card>
  );
}
