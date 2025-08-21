const BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");
const join = (p: string) => (p.startsWith("/") ? p : `/${p}`);

export async function api(path: string, init: RequestInit = {}) {
  const res = await fetch(`${BASE}${join(path)}`, {
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
