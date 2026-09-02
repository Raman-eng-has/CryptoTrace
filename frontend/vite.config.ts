import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/investigation': 'http://127.0.0.1:8000',
      '/risk': 'http://127.0.0.1:8000',
      '/graph': 'http://127.0.0.1:8000',
      '/evidence-packet': 'http://127.0.0.1:8000',
      '/summarize': 'http://127.0.0.1:8000',
      '/explain': 'http://127.0.0.1:8000',
      '/qa': 'http://127.0.0.1:8000',
    },
  },
})