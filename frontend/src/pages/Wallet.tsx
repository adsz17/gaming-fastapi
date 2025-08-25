import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/card";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { useGameStore } from "@/lib/store";
import { API_URL } from "@/lib/env";

export default function Wallet() {
  const { balance, setBalance } = useGameStore();
  const [deposit, setDeposit] = useState("");
  const [withdraw, setWithdraw] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token") || "";
    fetch(`${API_URL}/wallet/balance`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: "include",
    })
      .then((res) => (res.ok ? res.json().catch(() => ({})) : {}))
      .then((data) => {
        if (typeof data.balance === "number") {
          setBalance(data.balance);
        }
      })
      .catch(() => {});
  }, [setBalance]);

  async function sendTxn(amount: number, reason: string) {
    const token = localStorage.getItem("token") || "";
    const res = await fetch(`${API_URL}/wallet/txn`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
      body: JSON.stringify({
        amount,
        reason,
        idempotency_key: crypto.randomUUID(),
      }),
    });
    if (res.ok) {
      const data = await res.json().catch(() => ({}));
      if (typeof data.balance === "number") {
        setBalance(data.balance);
      }
    }
  }

  const handleDeposit = () => {
    const amt = parseFloat(deposit);
    if (!isNaN(amt) && amt > 0) {
      sendTxn(amt, "deposit").then(() => setDeposit(""));
    }
  };

  const handleWithdraw = () => {
    const amt = parseFloat(withdraw);
    if (!isNaN(amt) && amt > 0) {
      sendTxn(-amt, "withdraw").then(() => setWithdraw(""));
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="p-4 space-y-4 max-w-md mx-auto w-full">
        <Card className="space-y-4 p-4">
          <div className="text-xl font-bold">Balance: ${balance.toFixed(2)}</div>
          <div className="space-y-2">
            <Input
              type="number"
              value={deposit}
              onChange={(e) => setDeposit(e.target.value)}
              placeholder="Amount"
            />
            <Button onClick={handleDeposit} className="w-full" disabled={!deposit}>
              Deposit
            </Button>
          </div>
          <div className="space-y-2">
            <Input
              type="number"
              value={withdraw}
              onChange={(e) => setWithdraw(e.target.value)}
              placeholder="Amount"
            />
            <Button onClick={handleWithdraw} className="w-full" disabled={!withdraw}>
              Withdraw
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
