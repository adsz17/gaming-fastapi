import { Routes, Route } from "react-router-dom";
import Lobby from "./pages/Lobby";
import Play from "./pages/Play";
import Wallet from "./pages/Wallet";
import Profile from "./pages/Profile";
import Leaderboard from "./pages/Leaderboard";
import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { ToastProvider } from "./components/ui/toast";

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route path="/" element={<Lobby />} />
        <Route path="/play" element={<Play />} />
        <Route path="/wallet" element={<Wallet />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </ToastProvider>
  );
}
