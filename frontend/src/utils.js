// utils.js
const getToken = () => {
    // 先從 localStorage 中讀取 Token
    let token = localStorage.getItem('ACCESS_TOKEN');

    // 如果 localStorage 中沒有 Token，再從 Cookie 中讀取
    if (!token) {
        token = getCookie('ACCESS_TOKEN');
    }

    return token;  // 返回 Token（如果找不到則返回 null）
};

// 這是你封裝的 api 函數
async function api(path, { method = 'GET', headers = {}, body = null } = {}) {
    const token = getToken();
    // const WEB_BASE = "http://10.250.101.238:5000"
    const WEB_BASE = window.WEB_BASE
    if (token) headers['Authorization'] = `Bearer ${token}`;  // 如果有 Token，就加上 Authorization 標頭
    const res = await fetch(WEB_BASE + path, { method, headers, body });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `請求失敗：${res.status}`);
    }
    const ct = res.headers.get('content-type') || '';
    return ct.includes('application/json') ? res.json() : res.text();  // 如果是 JSON 格式，則解析為 JSON
}

// 用來讀取 Cookie 的輔助函數
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

export default api;  // 導出 api 函數


export function formatTime(lastLogin) {
    if (!lastLogin) return '未知時間';  // 如果時間無效，顯示"未知時間"
    const date = new Date(lastLogin);  // 轉換為 Date 對象
    if (isNaN(date)) return '無效時間';  // 檢查時間是否有效
    date.setHours(date.getHours() + 8);  // 增加 8 小時以轉換為北京時間
    return date.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });  // 格式化為北京時間
}
