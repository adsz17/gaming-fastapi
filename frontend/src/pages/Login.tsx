import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Card from "@/components/ui/card";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useGameStore } from "@/lib/store";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const toast = useToast();
  const { setBalance } = useGameStore();
  const { setUser } = useAuthStore();
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", { email, password });
      const data = res.data;
      localStorage.setItem("token", data.token);
      setUser(data.user);
      const balRes = await api.get("/wallet/balance");
      if (typeof balRes.data?.balance === "number") {
        setBalance(balRes.data.balance);
      }
      toast("Logged in");
      navigate("/play");
    } catch (err: any) {
      toast(err.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
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
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Loading..." : "Login"}
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
