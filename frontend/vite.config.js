import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/admin/',  // 根路径，如果 Vue 应用部署在根目录
})
//   base: '/',  // 根路径，如果 Vue 应用部署在根目录
//   build: {
//     rollupOptions: {
//       input: {
//         main: 'index.html',
//       },
//       output: {
//         entryFileNames: 'admin.html',  // 将生成的 HTML 文件名改为 admin.html
//       },
//     },
//   },
// })