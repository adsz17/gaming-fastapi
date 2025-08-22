import { useGameStore } from "@/lib/store";
import { motion } from "framer-motion";
import Card from "./ui/card";

export default function GameCanvas() {
  const multiplier = useGameStore((s) => s.multiplier);
  const phase = useGameStore((s) => s.phase);
  return (
    <Card className="flex flex-col items-center justify-center h-64 md:h-80">
      <motion.div
        key={multiplier}
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.2 }}
        className="text-5xl md:text-7xl font-bold text-neon-green"
      >
        {multiplier.toFixed(2)}x
      </motion.div>
      <div className="text-gray-500 mt-2">
        {phase === "crashed" ? "Crashed!" : phase === "flying" ? "Flying..." : "Waiting"}
      </div>
      <div className="mt-4 h-32 w-full bg-gray-900 border border-gray-700 rounded flex items-end justify-center">
        <div className="w-1/2 h-1 bg-neon-pink"></div>
      </div>
    </Card>
  );
}
