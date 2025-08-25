import { createContext, useContext, useState, ReactNode } from "react";
import { Navigate, useNavigate } from "react-router-dom";

interface AuthContext {
  token: string | null;
  setToken: (t: string | null) => void;
  logout: () => void;
}

const Ctx = createContext<AuthContext | undefined>(undefined);

export function AdminAuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem("adminToken")
  );
  const navigate = useNavigate();
  const logout = () => {
    setToken(null);
    localStorage.removeItem("adminToken");
    navigate("/admin/login");
  };
  return (
    <Ctx.Provider value={{ token, setToken, logout }}>{children}</Ctx.Provider>
  );
}

export function useAdminAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAdminAuth must be used within provider");
  return ctx;
}

export function AdminRoute({ children }: { children: ReactNode }) {
  const { token } = useAdminAuth();
  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }
  return <>{children}</>;
}
