// Use API URL from environment variables; default to same origin
const API = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export async function http(path, { method = "GET", body, headers } = {}) {
  const res = await fetch(API + path, {
    method,
    headers: { "Content-Type": "application/json", ...(headers || {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const ct = res.headers.get("content-type") || "";
  const payload = ct.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    const err = new Error("HTTP " + res.status);
    err.status = res.status;
    err.payload = payload;
    throw err;
  }
  return payload;
}

export function register({ email, username, password }) {
  return http("/api/auth/register", {
    method: "POST",
    body: { email, username, password },
  });
}

export function login({ email, password }) {
  return http("/api/auth/login", {
    method: "POST",
    body: { email, password },
  });
}
