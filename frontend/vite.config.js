import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/products': 'http://localhost:8001',
      '/api/cart': 'http://localhost:8002',
      '/api/orders': 'http://localhost:8003',
      '/api/payments': 'http://localhost:8004',
      '/api/chat': 'http://localhost:8005',
    },
  },
})
