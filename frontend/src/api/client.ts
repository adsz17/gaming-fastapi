import { api } from "../lib/api";

export async function registerUser(p:{email:string; username:string; password:string}) {
  return api("/api/auth/register", { method: "POST", body: JSON.stringify(p) });
}

export async function loginUser(p:{email:string; password:string}) {
  return api("/api/auth/login", { method: "POST", body: JSON.stringify(p) });
}
