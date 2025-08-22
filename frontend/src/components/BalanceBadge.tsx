import { useGameStore } from "@/lib/store";
import { Badge } from "./ui/badge";

export default function BalanceBadge() {
  const balance = useGameStore((s) => s.balance);
  return <Badge className="bg-neon-blue text-gray-900">${balance.toFixed(2)}</Badge>;
}
