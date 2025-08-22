import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig({
  root: "frontend",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "frontend/src"),
    },
  },
  build: { outDir: "dist", emptyOutDir: true },
  server: { port: 5173 },
});
