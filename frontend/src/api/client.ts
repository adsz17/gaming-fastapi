const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export async function api(path: string, opts: RequestInit = {}) {
  const r = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
export async function registerUser(p:{email:string; username:string; password:string}) {
  return api("/api/auth/register", { method: "POST", body: JSON.stringify(p) });
}
export async function loginUser(p:{email:string; password:string}) {
  return api("/api/auth/login", { method: "POST", body: JSON.stringify(p) });
}
