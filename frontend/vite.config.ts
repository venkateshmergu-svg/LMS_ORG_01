import react from '@vitejs/plugin-react'
import path from 'path'
import { defineConfig, loadEnv } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Build metadata - injected at build time by CI/CD
  const buildVersion = process.env.VITE_BUILD_VERSION || env.VITE_BUILD_VERSION || '0.0.0-local'
  const buildCommit = process.env.VITE_BUILD_COMMIT || env.VITE_BUILD_COMMIT || 'local'
  const buildDate = process.env.VITE_BUILD_DATE || env.VITE_BUILD_DATE || new Date().toISOString()
  const buildNumber = process.env.VITE_BUILD_NUMBER || env.VITE_BUILD_NUMBER || '0'
  
  // Check if we're doing bundle analysis (prefixed with _ to indicate intentionally unused)
  const _isAnalyze = mode === 'analyze'

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
      
      // Minification options for production
      minify: mode === 'production' ? 'esbuild' : false,
      
      // Optimize chunk splitting for caching
      rollupOptions: {
        output: {
          manualChunks: {
            // Core React libraries
            vendor: ['react', 'react-dom', 'react-router-dom'],
            // Data fetching
            query: ['@tanstack/react-query'],
            // Utilities and icons (tree-shakeable)
            utils: ['date-fns', 'clsx', 'axios', 'lucide-react'],
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
      
      // Target modern browsers for smaller bundles
      target: 'es2020',
    },
    
    // Optimize dependencies
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom', '@tanstack/react-query'],
    },
    
    // Environment variable prefix
    envPrefix: 'VITE_',
    
    // Enable CSS code splitting
    css: {
      devSourcemap: mode !== 'production',
    },
    
    // esbuild options for production
    esbuild: mode === 'production' ? {
      // Remove console.log in production
      drop: ['console', 'debugger'],
    } : {},
  }
})
