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
      '/static': {
        target: 'http://8.138.47.159:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})