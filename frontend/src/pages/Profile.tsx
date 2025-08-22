import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/card";
import { useGameStore } from "@/lib/store";

interface User {
  id: string;
  email: string;
  username: string;
}

export default function Profile() {
  const [user, setUser] = useState<User | null>(null);
  const { setBalance } = useGameStore();

  useEffect(() => {
    const token = localStorage.getItem("token") || "";
    fetch("/me", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json().catch(() => null) : null))
      .then((data) => data && setUser(data))
      .catch(() => {});
    fetch("/wallet/balance", { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json().catch(() => ({})) : {}))
      .then((data) => {
        if (typeof data.balance === "number") {
          setBalance(data.balance);
        }
      })
      .catch(() => {});
  }, [setBalance]);

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <div className="p-4">
          <Card>Loading...</Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="p-4">
        <Card className="space-y-2">
          <div>
            <strong>ID:</strong> {user.id}
          </div>
          <div>
            <strong>Email:</strong> {user.email}
          </div>
          <div>
            <strong>Username:</strong> {user.username}
          </div>
        </Card>
      </div>
    </div>
  );
}
