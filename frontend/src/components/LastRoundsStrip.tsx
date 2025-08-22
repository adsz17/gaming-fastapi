import { useGameStore } from "@/lib/store";
import { Badge } from "./ui/badge";
import { motion, AnimatePresence } from "framer-motion";

export default function LastRoundsStrip() {
  const rounds = useGameStore((s) => s.lastRounds);
  return (
    <div className="flex gap-2 overflow-x-auto py-2">
      <AnimatePresence>
        {rounds.map((m, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <Badge className="bg-gray-700 text-neon-green">{m.toFixed(2)}x</Badge>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
