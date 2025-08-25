import * as React from "react";
import Card from "@/components/ui/card";
import Skeleton from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { formatMoney, formatMultiplier } from "@/lib/utils";
import { API_URL } from "@/lib/env";

interface Bet {
  id: number;
  amount: number;
  cashout: number;
}

export default function ActiveBetsPanel() {
  const [bets, setBets] = React.useState<Bet[]>([]);
  const [loading, setLoading] = React.useState(true);
  const toast = useToast();

  React.useEffect(() => {
    const token = localStorage.getItem("token") || "";
    fetch(`${API_URL}/bets/active`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("failed");
        }
        return res.json();
      })
      .then((data) => setBets(Array.isArray(data) ? data : []))
      .catch(() => {
        toast("Error cargando apuestas");
        setBets([]);
      })
      .finally(() => setLoading(false));
  }, [toast]);

  return (
    <Card className="h-full flex flex-col" aria-label="Apuestas activas">
      <h2 className="mb-2 text-lg">Apuestas activas</h2>
      <div className="flex-1 overflow-y-auto space-y-2">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))
        ) : bets.length === 0 ? (
          <p className="text-sm text-gray-400">Sin apuestas</p>
        ) : (
          bets.map((b) => (
            <div key={b.id} className="flex justify-between text-sm">
              <span>{formatMoney(b.amount)}</span>
              <span>{formatMultiplier(b.cashout)}</span>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
