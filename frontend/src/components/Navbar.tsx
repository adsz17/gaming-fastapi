import { Link, NavLink } from "react-router-dom";
import BalanceBadge from "./BalanceBadge";
import { cn } from "@/lib/utils";

export default function Navbar() {
  const token = localStorage.getItem("token");

  return (
    <nav className="flex items-center justify-between p-4 bg-gray-800/50 border-b border-neon-blue">
      <Link to="/" className="text-neon-pink font-bold">
        CrashGame
      </Link>
      <div className="flex items-center gap-4">
        {token ? (
          <>
            <NavLink
              to="/play"
              className={({ isActive }) =>
                cn("hover:text-neon-pink", isActive && "text-neon-pink")
              }
            >
              Play
            </NavLink>
            <NavLink
              to="/wallet"
              className={({ isActive }) =>
                cn("hover:text-neon-pink", isActive && "text-neon-pink")
              }
            >
              Wallet
            </NavLink>
            <NavLink
              to="/leaderboard"
              className={({ isActive }) =>
                cn("hover:text-neon-pink", isActive && "text-neon-pink")
              }
            >
              Leaderboard
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                cn("hover:text-neon-pink", isActive && "text-neon-pink")
              }
            >
              Profile
            </NavLink>
            <BalanceBadge />
          </>
        ) : (
          <>
            <NavLink
              to="/login"
              className={({ isActive }) =>
                cn("hover:text-neon-pink", isActive && "text-neon-pink")
              }
            >
              Login
            </NavLink>
            <NavLink
              to="/register"
              className={({ isActive }) =>
                cn("hover:text-neon-pink", isActive && "text-neon-pink")
              }
            >
              Register
            </NavLink>
          </>
        )}
      </div>
    </nav>
  );
}
