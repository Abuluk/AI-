import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'  // 关键：需引入 path 模块

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 配置 '@' 指向项目的 src 目录
      '@': path.resolve(__dirname, 'src')  
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    }
  }
})