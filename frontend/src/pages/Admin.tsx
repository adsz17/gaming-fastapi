import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/card";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";

interface User {
  id: string;
  email: string;
  username: string;
  balance: number;
}

export default function Admin() {
  const [token, setToken] = useState(localStorage.getItem("admin_token") || "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [users, setUsers] = useState<User[]>([]);
  const [amounts, setAmounts] = useState<Record<string, string>>({});

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      const data = await res.json();
      setToken(data.access_token);
      localStorage.setItem("admin_token", data.access_token);
    }
  }

  useEffect(() => {
    if (token) {
      fetchUsers();
    }
  }, [token]);

  async function fetchUsers() {
    const res = await fetch("/api/admin/users", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      setUsers(data);
    }
  }

  async function credit(userId: string) {
    const amount = amounts[userId];
    if (!amount) return;
    await fetch("/api/admin/credit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ email_or_user_id: userId, amount: parseFloat(amount) }),
    });
    setAmounts((a) => ({ ...a, [userId]: "" }));
    fetchUsers();
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-sm w-full space-y-4">
          <h2 className="text-xl font-bold">Admin Login</h2>
          <form className="space-y-2" onSubmit={handleLogin}>
            <Input
              placeholder="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" className="w-full">
              Login
            </Button>
          </form>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="p-4 space-y-4">
        <h1 className="text-2xl font-bold">Admin Panel</h1>
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-gray-700">
              <th>Email</th>
              <th>Username</th>
              <th>Balance</th>
              <th className="w-48">Credit</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-gray-800">
                <td>{u.email}</td>
                <td>{u.username}</td>
                <td>{u.balance}</td>
                <td className="space-x-2">
                  <Input
                    type="number"
                    value={amounts[u.id] || ""}
                    onChange={(e) =>
                      setAmounts({ ...amounts, [u.id]: e.target.value })
                    }
                    className="w-24 inline-block"
                  />
                  <Button onClick={() => credit(u.id)}>Add</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
