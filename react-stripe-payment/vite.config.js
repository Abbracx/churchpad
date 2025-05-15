import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Expose the server to the network
    allowedHosts: ['df19-102-89-33-105.ngrok-free.app'], // Allow the specified host
  },
})
