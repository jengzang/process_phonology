import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  base: '/admin/',
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'admin.js',
        chunkFileNames: 'admin.js',
        assetFileNames: (a) =>
            a.name && a.name.endsWith('.css') ? 'admin.css' : a.name,
        manualChunks: undefined,
        inlineDynamicImports: true          // 合并动态导入，确保单文件
      }
    }
  }
})
