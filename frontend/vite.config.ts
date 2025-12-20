import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Build metadata - injected at build time by CI/CD
  const buildVersion = process.env.VITE_BUILD_VERSION || env.VITE_BUILD_VERSION || '0.0.0-local'
  const buildCommit = process.env.VITE_BUILD_COMMIT || env.VITE_BUILD_COMMIT || 'local'
  const buildDate = process.env.VITE_BUILD_DATE || env.VITE_BUILD_DATE || new Date().toISOString()
  const buildNumber = process.env.VITE_BUILD_NUMBER || env.VITE_BUILD_NUMBER || '0'

  return {
    plugins: [react()],
    
    // Define global constants (injected at build time)
    define: {
      __BUILD_VERSION__: JSON.stringify(buildVersion),
      __BUILD_COMMIT__: JSON.stringify(buildCommit),
      __BUILD_DATE__: JSON.stringify(buildDate),
      __BUILD_NUMBER__: JSON.stringify(buildNumber),
      __BUILD_MODE__: JSON.stringify(mode),
    },
    
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path,
        },
      },
    },
    
    build: {
      outDir: 'dist',
      sourcemap: mode !== 'production', // Enable sourcemaps for non-prod builds
      
      // Optimize chunk splitting for caching
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            query: ['@tanstack/react-query'],
            utils: ['date-fns', 'clsx', 'axios'],
          },
          // Include content hash for cache-busting
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].[ext]',
        },
      },
      
      // Report compressed size
      reportCompressedSize: true,
      
      // Chunk size warning limit (300KB)
      chunkSizeWarningLimit: 300,
    },
    
    // Environment variable prefix
    envPrefix: 'VITE_',
  }
})
