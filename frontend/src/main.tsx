import React from "react";
import { createRoot } from "react-dom/client";
import RegisterPage from "./pages/RegisterPage";
import "./index.css";

function Index() {
  const token = localStorage.getItem("token");
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-6 rounded-2xl shadow space-y-3 text-center">
        <h1 className="text-2xl font-semibold">Gaming FastAPI</h1>
        {token ? (
          <>
            <p className="text-gray-600">Sesión iniciada.</p>
            <button
              onClick={() => { localStorage.removeItem("token"); location.reload(); }}
              className="rounded-xl px-3 py-2 border"
            >Cerrar sesión</button>
          </>
        ) : (
          <>
            <a href="/register" className="rounded-xl px-3 py-2 bg-indigo-600 text-white inline-block">Registrarse</a>
          </>
        )}
      </div>
    </div>
  );
}

// ruteo súper simple por path
const path = location.pathname;
const root = createRoot(document.getElementById("app")!);
root.render(path.startsWith("/register") ? <RegisterPage /> : <Index />);
