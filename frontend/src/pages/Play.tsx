import Navbar from "@/components/Navbar";
import LastRoundsStrip from "@/components/LastRoundsStrip";
import GameCanvas from "@/components/GameCanvas";
import BetPanel from "@/components/BetPanel";
import { useAuth } from "@/store/auth";

export default function Play() {
  const balance = useAuth((s) => s.balance);
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex-1 p-4 grid gap-4 md:grid-cols-3">
        <div className="space-y-4">
          <LastRoundsStrip />
          <div className="p-4 bg-gray-800 rounded">Saldo: {balance.toFixed(2)}</div>
        </div>
        <div className="space-y-4">
          <GameCanvas />
          <BetPanel />
        </div>
        <div className="space-y-4">
          <div className="p-4 bg-gray-800 rounded">Apuestas activas</div>
        </div>
      </div>
    </div>
  );
}
