import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/lib/auth";

interface Props {
  children: ReactNode;
  admin?: boolean;
}

export default function ProtectedRoute({ children, admin = false }: Props) {
  const user = useAuthStore((s) => s.user);
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (admin && !user.is_admin) {
    return <div className="p-4">403 Forbidden</div>;
  }
  return <>{children}</>;
}
