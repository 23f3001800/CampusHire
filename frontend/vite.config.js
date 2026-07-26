import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [
    vue(),
    // Dev-server only. vite-plugin-vue-devtools is a devDependency, so a
    // production install (npm ci --omit=dev) would not have it available —
    // and shipping the devtools overlay to real users is not wanted anyway.
    ...(command === 'serve' ? [vueDevTools()] : []),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // Keeps the build log honest: html2pdf.js alone is ~975 kB, so the default
    // 500 kB warning fires on every build and trains you to ignore it.
    chunkSizeWarningLimit: 1100,
    rollupOptions: {
      output: {
        // Split the two heavy, rarely-changing libraries into their own chunks
        // so a code change does not invalidate ~1.2 MB of cached vendor JS.
        manualChunks: {
          chart: ['chart.js', 'vue-chartjs'],
          pdf: ['html2pdf.js'],
        },
      },
    },
  },
}))
