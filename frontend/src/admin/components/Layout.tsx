import { Link, Outlet, useLocation } from "react-router-dom";
import { FiltersProvider, useFilters } from "../filters";
import DateRangePicker from "./DateRangePicker";
import Input from "@/components/ui/input";
import Button from "@/components/ui/button";
import { useAdminAuth } from "../auth";

function Header() {
  const { userId, setUserId } = useFilters();
  const { logout } = useAdminAuth();
  return (
    <header className="flex items-center justify-between border-b border-neutral-800 p-4">
      <div className="flex items-center space-x-2">
        <DateRangePicker />
        <Input
          placeholder="Search user_id"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="w-48"
        />
      </div>
      <Button onClick={logout}>Logout</Button>
    </header>
  );
}

function Sidebar() {
  const { pathname } = useLocation();
  const links = [
    { to: "/admin", label: "Dashboard" },
    { to: "/admin/rounds", label: "Rounds" },
    { to: "/admin/ledger", label: "Ledger" },
  ];
  return (
    <aside className="w-48 border-r border-neutral-800 p-4 space-y-2">
      {links.map((l) => (
        <Link
          key={l.to}
          to={l.to}
          className={`block px-2 py-1 rounded ${
            pathname === l.to ? "bg-neutral-800" : "hover:bg-neutral-800"
          }`}
        >
          {l.label}
        </Link>
      ))}
    </aside>
  );
}

export default function Layout() {
  return (
    <FiltersProvider>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 p-4 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </FiltersProvider>
  );
}
