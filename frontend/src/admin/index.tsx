import { Routes, Route } from "react-router-dom";
import { AdminAuthProvider, AdminRoute } from "./auth";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Rounds from "./pages/Rounds";
import Ledger from "./pages/Ledger";

export default function AdminApp() {
  return (
    <AdminAuthProvider>
      <Routes>
        <Route path="login" element={<Login />} />
        <Route element={<AdminRoute><Layout /></AdminRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="rounds" element={<Rounds />} />
          <Route path="ledger" element={<Ledger />} />
        </Route>
      </Routes>
    </AdminAuthProvider>
  );
}
