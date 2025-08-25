import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import api from './axios';  // 引入 axios 配置
import './style.css'; // 引入全局CSS
import ElementPlus from 'element-plus';  // 引入 Element Plus
import 'element-plus/dist/index.css';  // 引入 Element Plus 样式

const app = createApp(App);
// 设置 API 基础路径

// 全局挂载 axios 配置
app.config.globalProperties.$api = api;

// 注册 Element UI 插件
app.use(ElementPlus);

// 使用 Vue Router
app.use(router);

// 挂载应用
app.mount('#app');

