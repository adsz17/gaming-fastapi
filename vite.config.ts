import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiUrl = (env.VITE_API_URL ?? '').replace(/\/$/, '')
  return {
    root: 'frontend',
    plugins: [react()],
    build: { outDir: 'dist', emptyOutDir: true },
    server: {
      port: 5173,
      proxy: apiUrl ? { '/api': apiUrl } : undefined,
    },
    preview: {
      port: 5173,
      proxy: apiUrl ? { '/api': apiUrl } : undefined,
    },
  }
})

