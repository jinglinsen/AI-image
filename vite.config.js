import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // 监听所有网络接口，允许通过 127.0.0.1 和 localhost 访问
    port: 3000,
    open: true,
    // 允许的主机列表，支持内网穿透等场景
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.natappfree.cc',  // 允许所有 natappfree.cc 子域名
      '.ngrok.io',       // 允许 ngrok
      '.cpolar.cn',      // 允许 cpolar
      '.localtunnel.me'  // 允许 localtunnel
    ]
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})

