import { createRouter, createWebHistory } from 'vue-router'
import UserManagement from '../components/UserManagement.vue'
import EditUser from '../components/EditUser.vue'
import LoginHistory from '../components/ApiDetail.vue'
import UserStats from '../components/UserStats.vue'
import Login from '../components/Login.vue';  // 引入 Login 頁面
import CreateUser from '../components/CreateUser.vue';
import ApiDetail from "../components/ApiDetail.vue";  // 引入新頁面
import ApiChart from "../components/ApiChart.vue";  // 引入新頁面
import Custom from "../components/Custom.vue";  // 引入新頁面

// 根路徑配置
const routes = [
    {
        path: '/',
        name: 'Home',  // 根路徑
        component: UserManagement  // 根路徑顯示用戶管理頁面
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,  // 登錄頁面
    },
    {
        path: '/users/create',  // 設置路徑
        name: 'CreateUser',     // 路由名稱
        component: CreateUser,  // 引入的組件
    },
    {
        path: '/users/edit',
        name: 'EditUser',
        component: EditUser
    },
    {
        path: '/api-usage',
        name: 'ApiDetail',
        component: ApiDetail
    },
    {
        path: '/users/stats',
        name: 'UserStats',
        component: UserStats
    },
    {
        path: '/api-chart',
        name: 'ApiChart',
        component: ApiChart
    },
    {
        path: '/custom',
        name: 'Custom',
        component: Custom
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

export default router
