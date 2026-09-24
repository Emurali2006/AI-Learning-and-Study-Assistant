import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true 
      },
      manifest: {
        name: 'StudyAI Learning Assistant',
        short_name: 'StudyAI',
        description: 'AI-powered student learning assistant',
        theme_color: '#ffffff',
        background_color: '#f8f9fa',
        display: 'standalone',
        icons: [
          {
            // Now pointing to your new PNG image
            src: '/icon.png', 
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icon.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
})