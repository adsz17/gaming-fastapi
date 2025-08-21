import { useState } from "react";
import { api } from "../lib/api";

export default function Register() {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);
    const fd = new FormData(e.currentTarget);
    const email = String(fd.get("email") || "");
    const username = String(fd.get("username") || "");
    const password = String(fd.get("password") || "");

    if (!email || !username || password.length < 6) {
      setErr("Completá todos los campos (password mínimo 6).");
      return;
    }
    setLoading(true);
    try {
      const r = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, username, password }),
      });
      localStorage.setItem("token", r.access_token);
      window.location.href = "/"; // redirigir al index
    } catch (e: any) {
      setErr(e.message || "Error registrando");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow p-6">
        <h1 className="text-2xl font-semibold mb-2">Crear cuenta</h1>
        <p className="text-sm text-gray-500 mb-6">
          Registrate para empezar a jugar.
        </p>
        <form onSubmit={onSubmit} className="space-y-3">
          <input name="email" type="email" placeholder="Email"
                 className="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring"
                 required />
          <input name="username" placeholder="Usuario"
                 className="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring"
                 required />
          <input name="password" type="password" placeholder="Contraseña (min 6)"
                 className="w-full border rounded-xl px-3 py-2 focus:outline-none focus:ring"
                 minLength={6} required />
          {err && <div className="text-sm text-red-600">{err}</div>}
          <button disabled={loading}
                  className="w-full rounded-xl px-3 py-2 bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">
            {loading ? "Creando..." : "Registrarse"}
          </button>
        </form>
        <a href="/" className="block text-center text-sm text-gray-500 mt-4 hover:underline">
          Volver al inicio
        </a>
      </div>
    </div>
  );
}
