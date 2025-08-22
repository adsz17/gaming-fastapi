import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import Card from "@/components/ui/card";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

export default function Register() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const toast = useToast();
  const { setUser } = useAuthStore();
  const [loading, setLoading] = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register", { email, username, password });
      const data = res.data;
      localStorage.setItem("token", data.token);
      setUser(data.user);
      toast("Registered");
      navigate("/play");
    } catch (err: any) {
      toast(err.response?.data?.error || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-sm w-full space-y-4 p-4">
        <h2 className="text-xl font-bold text-center">Register</h2>
        <form className="space-y-2" onSubmit={handleRegister}>
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Loading..." : "Register"}
          </Button>
        </form>
        <p className="text-sm text-center">
          Already have an account? {""}
          <Link to="/login" className="text-neon-pink">
            Login
          </Link>
        </p>
      </Card>
    </div>
  );
}
