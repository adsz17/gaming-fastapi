import { LedgerItem, Round } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

function buildUrl(path: string, query?: Record<string, any>) {
  const url = new URL(path, API_BASE_URL || window.location.origin);
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") {
        url.searchParams.append(k, String(v));
      }
    });
  }
  return url.toString();
}

async function apiFetch<T>(path: string, opts: { query?: Record<string, any> } = {}): Promise<T> {
  const token = localStorage.getItem("adminToken");
  const res = await fetch(buildUrl(path, opts.query), {
    headers: token ? { "X-Admin-Token": token } : undefined,
    credentials: "omit",
  });
  if (res.status === 401 || res.status === 403) {
    localStorage.removeItem("adminToken");
    window.location.href = "/admin/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(res.statusText);
  }
  return res.json();
}

export async function fetchRounds(params: Record<string, any>): Promise<Round[]> {
  const data = await apiFetch<{ rounds: Round[] }>("/admin/rounds", { query: params });
  return data.rounds || [];
}

export async function fetchLedger(params: Record<string, any>): Promise<LedgerItem[]> {
  const data = await apiFetch<{ ledger: LedgerItem[] }>("/admin/ledger", { query: params });
  return data.ledger || [];
}
