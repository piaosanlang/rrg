import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync } from 'fs'

export default defineConfig({
  base: "/",
  plugins: [
    react(),
    {
      name: 'copy-static-assets',
      closeBundle() {
        try {
          copyFileSync('favicon.svg', 'dist/favicon.svg')
          copyFileSync('icons.svg', 'dist/icons.svg')
        } catch (e) {
          console.warn('Failed to copy static assets:', e)
        }
      }
    }
  ],
  publicDir: false,
});
