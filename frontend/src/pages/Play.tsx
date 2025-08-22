import Navbar from "@/components/Navbar";
import LastRoundsStrip from "@/components/LastRoundsStrip";
import GameCanvas from "@/components/GameCanvas";
import BetPanel from "@/components/BetPanel";

export default function Play() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex-1 p-4 space-y-4 max-w-3xl mx-auto w-full">
        <LastRoundsStrip />
        <GameCanvas />
        <BetPanel />
      </div>
    </div>
  );
}
