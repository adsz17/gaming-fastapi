import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/card";

interface Entry {
  username: string;
  balance: number;
}

export default function Leaderboard() {
  const [entries, setEntries] = useState<Entry[]>([]);

  useEffect(() => {
    fetch("/leaderboard")
      .then((res) => res.json())
      .then(setEntries)
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="p-4">
        <Card className="overflow-x-auto">
          <h2 className="text-xl font-bold mb-4">Top Players</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-700">
                <th>Username</th>
                <th>Balance</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.username} className="border-b border-gray-800">
                  <td>{e.username}</td>
                  <td>${e.balance.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}
