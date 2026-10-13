import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        host: true, // Listen on all addresses (0.0.0.0)
        strictPort: true,
        cors: true,
        allowedHosts: ['2ac68c1a83ced3.lhr.life', '.lhr.life', '.localhost.run', '.serveo.net'],
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
            },
        },
    },
})
