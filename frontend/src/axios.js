import axios from 'axios';
// window.WEB_BASE = location.origin
window.WEB_BASE = "http://10.250.101.238:5000";
window.API_BASE = window.WEB_BASE + "/api";
window.LOG_BASE = window.WEB_BASE + "/auth";
window.ADMIN_BASE = window.WEB_BASE + "/admin";
// 創建 Axios 實例
const api = axios.create({
    // baseURL: 'http://10.250.101.238:5000/admin',  // 你的後端服務地址
    baseURL: window.ADMIN_BASE,  // 你的後端服務地址
    timeout: 1000,  // 設置請求超時時間
});

// 讀取 Cookie 中的 Token
const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

// 獲取 Token 的方法
const getAuthToken = () => {
    // 首先從 localStorage 讀取 Token
    // 首先從 localStorage 讀取 Token
    let token = localStorage.getItem('ACCESS_TOKEN');
    // console.log('Token from localStorage:', token);  // 加入這行檢查

    // 如果 localStorage 沒有 Token，再從 Cookie 讀取 Token
    if (!token) {
        token = getCookie('ACCESS_TOKEN');
        // console.log('Token from Cookie:', token);  // 加入這行檢查
    }

    return token;
};

// 設置 Authorization 標頭，附加 Token
const token = getAuthToken();
if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    // console.log('Authorization header:', api.defaults.headers.common['Authorization']);
}

export default api;
