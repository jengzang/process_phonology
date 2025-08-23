import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import api from './axios'  // 引入 axios 配置

const app = createApp(App);
app.config.globalProperties.$api = api;  // 全局掛載 axios 配置
app.use(router);
app.mount('#app');

// 设置 API 基础路径
window.WEB_BASE = "http://10.250.101.238:5000";
window.API_BASE = window.WEB_BASE + "/api";
window.LOG_BASE = window.WEB_BASE + "/auth";