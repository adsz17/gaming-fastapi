import { Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import Lobby from "./pages/Lobby";
import Play from "./pages/Play";
import Wallet from "./pages/Wallet";
import Profile from "./pages/Profile";
import Leaderboard from "./pages/Leaderboard";
import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";
import { ToastProvider, useToast } from "./components/ui/toast";
import { setClientErrorHandler } from "./api/client";

function AppRoutes() {
  const toast = useToast();
  useEffect(() => {
    setClientErrorHandler((msg) => toast(msg));
  }, [toast]);
  return (
    <Routes>
      <Route path="/" element={<Lobby />} />
      <Route path="/play" element={<ProtectedRoute><Play /></ProtectedRoute>} />
      <Route path="/wallet" element={<ProtectedRoute><Wallet /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
      <Route path="/admin" element={<ProtectedRoute admin><Admin /></ProtectedRoute>} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppRoutes />
    </ToastProvider>
  );
}
