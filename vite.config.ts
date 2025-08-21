import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  root: 'frontend',            // acá está tu index.html
  plugins: [react()],
  build: {
    outDir: 'dist',            // => genera frontend/dist
    emptyOutDir: true
  },
  server: { port: 5173 },
  preview: { port: 5173 }
})

