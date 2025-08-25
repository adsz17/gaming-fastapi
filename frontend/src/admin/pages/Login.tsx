import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "@/components/ui/card";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { useAdminAuth } from "../auth";

export default function Login() {
  const [val, setVal] = useState("");
  const { setToken } = useAdminAuth();
  const navigate = useNavigate();
  function submit(e: React.FormEvent) {
    e.preventDefault();
    setToken(val);
    localStorage.setItem("adminToken", val);
    navigate("/admin");
  }
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="p-4 space-y-4 max-w-sm w-full">
        <h1 className="text-xl font-bold">Admin Login</h1>
        <form className="space-y-2" onSubmit={submit}>
          <Input
            placeholder="Admin Token"
            value={val}
            onChange={(e) => setVal(e.target.value)}
          />
          <Button type="submit" className="w-full">
            Login
          </Button>
        </form>
      </Card>
    </div>
  );
}
