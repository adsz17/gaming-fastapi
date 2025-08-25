import * as React from "react";
import { Badge } from "@/components/ui/badge";
import Skeleton from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { formatMoney } from "@/lib/utils";
import BetPanel from "@/components/BetPanel";
import ActiveBetsPanel from "@/components/ActiveBetsPanel";
import { API_URL } from "@/lib/env";

export default function Play() {
  const [balance, setBalance] = React.useState<number | null>(null);
  const toast = useToast();

  React.useEffect(() => {
    const token = localStorage.getItem("token") || "";
    fetch(`${API_URL}/wallet/balance`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setBalance(data.balance ?? 0))
      .catch(() => toast("Error cargando saldo"));
  }, [toast]);

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
          <BetPanel />
        </div>
        <div className="md:col-span-4">
          <ActiveBetsPanel />
        </div>
      </main>
    </div>
  );
}
