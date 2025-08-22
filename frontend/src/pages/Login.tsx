import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Card from "@/components/ui/card";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useGameStore } from "@/lib/store";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const toast = useToast();
  const { setBalance } = useGameStore();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        toast(err.error || "Login failed");
        return;
      }
      const data = await res.json();
      localStorage.setItem("token", data.token);
      // fetch balance for store
      const balRes = await fetch("/wallet/balance", {
        headers: { Authorization: `Bearer ${data.token}` },
      });
      if (balRes.ok) {
        const bal = await balRes.json();
        setBalance(bal.balance);
      }
      toast("Logged in");
      navigate("/");
    } catch {
      toast("Login failed");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-sm w-full space-y-4 p-4">
        <h2 className="text-xl font-bold text-center">Login</h2>
        <form className="space-y-2" onSubmit={handleLogin}>
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" className="w-full">
            Login
          </Button>
        </form>
        <p className="text-sm text-center">
          No account? {""}
          <Link to="/register" className="text-neon-pink">
            Register
          </Link>
        </p>
      </Card>
    </div>
  );
}
