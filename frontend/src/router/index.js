import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
import UserManagement from '../components/UserManagement.vue'
import EditUser from '../components/user/EditUser.vue'
import UserStats from '../components/user/UserStats.vue'
import Login from '../components/Login.vue';  // 引入 Login 頁面
import CreateUser from '../components/user/CreateUser.vue';
import ApiDetail from "../components/user/ApiDetail.vue";  // 引入新頁面
import ApiChart from "../components/user/ApiChart.vue";  // 引入新頁面
import Custom from "../components/custom/Custom.vue";  // 引入新頁面
import CustomPerUser from "../components/custom/CustomPerUser.vue";  // 引入新頁面
import CreateCustom from "../components/custom/CreateCustom.vue";
import DeleteCustom from "../components/custom/DeleteCustom.vue";
import EditCustom from "../components/custom/EditCustom.vue";  // 引入新頁面
import IP from "../components/user/IPQuery.vue"

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
        path: '/apiUsage',
        name: 'ApiDetail',
        component: ApiDetail
    },
    {
        path: '/ip/:ip',
        name: 'IP',
        component: IP
    },
    {
        path: '/users/stats',
        name: 'UserStats',
        component: UserStats
    },
    {
        path: '/utils-chart',
        name: 'ApiChart',
        component: ApiChart
    },
    {
        path: '/custom',
        name: 'Custom',
        component: Custom
    },
    {
        path: '/per-user',
        name: 'PerUser',
        component: CustomPerUser
    },
    {
        path: '/custom/create',
        name: 'CreateCustom',
        component: CreateCustom
    },
    {
        path: '/custom/delete',
        name: 'DeleteCustom',
        component: DeleteCustom
    },
    {
        path: '/custom/edit',
        name: 'EditCustom',
        component: EditCustom
    },
]

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes
})

export default router
