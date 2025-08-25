import * as React from "react";
import Card from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Skeleton from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { formatMoney, formatMultiplier } from "@/lib/utils";
import BetForm from "@/components/BetForm";
import ActiveBetsPanel from "@/components/ActiveBetsPanel";
import { API_URL } from "@/lib/env";

export default function Play() {
  const [balance, setBalance] = React.useState<number | null>(null);
  const [multiplier, setMultiplier] = React.useState(1);
  const toast = useToast();

  React.useEffect(() => {
    fetch(`${API_URL}/wallet/balance`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setBalance(data.balance ?? 0))
      .catch(() => toast("Error cargando saldo"));
  }, [toast]);

  React.useEffect(() => {
    const id = setInterval(() => {
      setMultiplier((m) => Number((m + 0.01).toFixed(2)));
    }, 100);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-inter">
      <header className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="text-neon-pink font-bold" aria-label="Logo">
          NeonCrash
        </div>
        {balance === null ? (
          <Skeleton className="h-6 w-24" />
        ) : (
          <Badge className="bg-gray-800 border border-neon-blue text-neon-blue">
            {formatMoney(balance)}
          </Badge>
        )}
      </header>
      <main className="p-4 grid grid-cols-1 md:grid-cols-12 gap-4">
        <div className="md:col-span-8 space-y-4">
          <Card className="flex flex-col items-center justify-center h-64 space-y-4 shadow-md" aria-label="Multiplicador">
            <div className="text-6xl font-bold text-neon-green transition-all duration-300">
              {formatMultiplier(multiplier)}
            </div>
            <div className="w-full bg-gray-700 h-2 rounded">
              <div
                className="bg-neon-pink h-2 rounded"
                style={{ width: `${(multiplier % 1) * 100}%`, transition: "width 0.1s linear" }}
              />
            </div>
          </Card>
          {balance !== null && <BetForm balance={balance} onBet={setBalance} />}
        </div>
        <div className="md:col-span-4">
          <ActiveBetsPanel />
        </div>
      </main>
    </div>
  );
}
