import { useEffect, useState } from "react";
import Card from "@/components/ui/card";
import { useFilters } from "../filters";
import { fetchRounds, fetchLedger } from "../api";
import { Round, LedgerItem } from "../types";
import { formatMoney } from "../utils/format";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export default function Dashboard() {
  const { range, userId } = useFilters();
  const [rounds, setRounds] = useState<Round[]>([]);
  const [ledger, setLedger] = useState<LedgerItem[]>([]);

  useEffect(() => {
    const params: any = {};
    if (range.from) params.from = range.from.toISOString();
    if (range.to) params.to = range.to.toISOString();
    if (userId) params.user_id = userId;
    fetchRounds(params).then(setRounds);
    fetchLedger(params).then(setLedger);
  }, [range, userId]);

  const totalBets = rounds.reduce((s, r) => s + r.bet, 0);
  const totalPayouts = rounds.reduce((s, r) => s + r.payout, 0);
  const net = totalBets - totalPayouts;
  const movements = ledger.length;

  const daily: Record<string, { date: string; bet: number; payout: number; net: number }> = {};
  rounds.forEach((r) => {
    const day = r.created_at.slice(0, 10);
    if (!daily[day]) daily[day] = { date: day, bet: 0, payout: 0, net: 0 };
    daily[day].bet += r.bet;
    daily[day].payout += r.payout;
    daily[day].net += r.bet - r.payout;
  });
  const chartData = Object.values(daily).sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-neutral-400">Total Bets</div>
          <div className="text-xl font-bold">{formatMoney(totalBets)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-400">Total Payouts</div>
          <div className="text-xl font-bold">{formatMoney(totalPayouts)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-400">Net</div>
          <div className="text-xl font-bold">{formatMoney(net)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-400">Movements</div>
          <div className="text-xl font-bold">{movements}</div>
        </Card>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <div className="mb-2 font-medium">Net by Day</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="net" stroke="#39ff14" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card className="p-4">
          <div className="mb-2 font-medium">Bets vs Payouts</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="bet" fill="#00ffff" />
                <Bar dataKey="payout" fill="#ff00ff" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
