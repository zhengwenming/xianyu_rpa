import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  // 相对路径：让打包后的 HTML 引用相对资源
  base: './',
  // 输出到后端 static/web 目录，供 FastAPI 直接挂载
  build: {
    outDir: path.resolve(__dirname, '../backend/static/web'),
    emptyOutDir: true,
    // 单一入口避免 chunk 加载路径问题
    chunkSizeWarningLimit: 2000,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8765',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8765',
        ws: true,
      },
    },
  },
})
