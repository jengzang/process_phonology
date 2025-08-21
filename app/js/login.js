const { createApp, ref, defineComponent, onMounted ,watch } = window.Vue


function showAuthPopup() {
    const container = document.createElement('div')
    document.body.appendChild(container)

    const AuthPopup = defineComponent({
        setup() {
            const mode = ref('login') // login | register | profile
            const username = ref('')
            const password = ref('')
            const email = ref('')
            const error = ref('')
            const loading = ref(false)
            const user = ref(null)


            const close = () => {
                app.unmount()
                document.body.removeChild(container)
            }

            const validateEmail = (email) => {
                const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
                return re.test(email)
            }

            const login = async () => {
                error.value = ''

                if (password.value.length < 6) {
                    error.value = '密碼不得少於 6 位'
                    return
                }

                loading.value = true

                try {
                    const form = new URLSearchParams()
                    form.append('username', username.value)
                    form.append('password', password.value)
                    const res = await api('/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: form,
                    })
                    saveToken(res.access_token)
                    await fetchUser()
                    mode.value = 'profile'
                    error.value = '✅ 登入成功'
                    setTimeout(() => {
                        error.value = ''
                    }, 1500)
                } catch (e) {
                    const msg = e.message || ''
                    if (msg.includes('Invalid credentials')) {
                        error.value = '用戶名不存在或密碼錯誤！'
                    } else {
                        error.value = msg
                    }
                } finally {
                    loading.value = false  // ✅ 保證流程結束後可再次提交
                }
            }


            const register = async () => {
                error.value = ''

                // 驗證 email 與密碼
                if (!validateEmail(email.value)) {
                    error.value = '請輸入正確的郵箱'
                    return
                }
                if (password.value.length < 6) {
                    error.value = '密碼不得少於 6 位'
                    return
                }

                loading.value = true

                try {
                    const res = await api('/auth/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: username.value,
                            email: email.value,
                            password: password.value,
                        }),
                    })
                    error.value = '✅ 註冊成功，請登入'
                    mode.value = 'login'
                } catch (e) {
                    const msg = e.message || ''
                    if (msg.includes('Username already exists')) {
                        error.value = '該用戶名已被佔用，請更換一個'
                    } else if (msg.includes('Email already exists')) {
                        error.value = '該郵箱已註冊，可直接登錄'
                    } else {
                        error.value = msg
                    }
                } finally {
                    loading.value = false  // ✅ 結束 loading，讓使用者可再次操作
                }
            }




            const logout = async () => {
                try {
                    await api('/auth/logout', { method: 'POST' })
                } catch {}
                clearToken()
                mode.value = 'login'
            }

            const fetchUser = async () => {
                try {
                    const res = await api('/auth/me')
                    user.value = res
                } catch {
                    clearToken()
                    mode.value = 'login'
                }
            }

            onMounted(async () => {
                if (getToken()) {
                    await fetchUser()
                    if (user.value) mode.value = 'profile'
                }
            })

            // ✅ 格式化為北京時間（UTC+8）
            const fmt = (isoStr) => {
                const utc = new Date(isoStr)
                const beijing = new Date(utc.getTime() + 8 * 60 * 60 * 1000)
                return beijing.toLocaleString('zh-Hant-CN', { hour12: false })
            }

            const formatOnlineTime = (seconds) => {
                if (!seconds || isNaN(seconds)) return '-'
                const hours = Math.floor(seconds / 3600)
                const minutes = Math.floor((seconds % 3600) / 60)
                return `${hours} 小時 ${minutes} 分鐘`
            }

            watch(mode, () => {
                error.value = ''
            })


            return {
                username, password, email, error, loading,
                user, mode, login, register, logout, close, fmt,
                formatOnlineTime // 👈 新增這行
            }

        },
        template: `
      <div class="query-detail-panel" @click.self="close">
        <button class="popup-close" @click="close" style="position:absolute;top:8px;right:12px;font-size:20px;background:none;border:none;cursor:pointer;">×</button>

        <!-- 登錄介面 -->
        <div v-if="mode === 'login'" style="padding: 12px; text-align: center;">
          <h3>登錄界面</h3>
          <div class="form-row" style="display: flex; justify-content: center;"><input v-model="username" placeholder="用戶名" /></div>
          <div class="form-row" style="display: flex; justify-content: center;"><input v-model="password" type="password" placeholder="密碼" /></div>
          <div class="form-row" style="display: flex; justify-content: center;">
            <button class="btn-search" @click="login" :disabled="loading">登錄</button>
          </div>
          <p v-if="error" class="err">{{ error }}</p>
          <p><a href="#" @click.prevent="mode='register'">沒有帳號？註冊一個</a></p>
        </div>

        <!-- 註冊介面 -->
        <div v-else-if="mode === 'register'" style="padding: 12px; text-align: center;">
          <h3>註冊界面</h3>
          <div class="form-row" style="display: flex; justify-content: center;"><input v-model="username" placeholder="用戶名" /></div>
          <div class="form-row" style="display: flex; justify-content: center;"><input v-model="email" placeholder="郵箱" /></div>
          <div class="form-row" style="display: flex; justify-content: center;"><input v-model="password" type="password" placeholder="密碼" /></div>
          <div class="form-row" style="display: flex; justify-content: center;">
            <button class="btn-search" @click="register" :disabled="loading">註冊</button>
          </div>
          <p v-if="error" class="err">{{ error }}</p>
          <p><a href="#" @click.prevent="mode='login'">已有帳號？登錄</a></p>
        </div>

        <!-- 🎉 Profile 歡迎彈窗 -->
        <div
            v-if="mode === 'profile' && user"
            style="padding: 12px; text-align: center;"
        >
          <h3 id="login-title" style="font-size: 28px; white-space: nowrap">👋 歡迎回來，{{ user.username }}！✨</h3>
          <p id="login-info" style="font-size: 17px">
            {{ user?.role === 'admin' ? '🛡️ 您是管理員' : '👤 您是普通用戶' }}
          </p>
          <p id="login-info" style="font-size: 17px">🗓️ 註冊時間：{{ fmt(user.created_at) }}</p>
          <p id="login-info" style="font-size: 17px">⏱️ 總在線時長：{{ formatOnlineTime(user.total_online_seconds) }}</p>
          <div class="form-row" style="justify-content: center;">
            <button class="btn-search" @click="logout">登出</button>
          </div>
        </div>
      </div>
    `
    })

    const app = createApp(AuthPopup)
    app.mount(container)

    // ✅ 顯示面板 + 居中 + 自適應大小（不改 CSS）
    setTimeout(() => {
        const panel = container.querySelector('.query-detail-panel')
        if (panel) {
            panel.style.display = 'flex'
            panel.style.left = '50%'
            panel.style.top = '50%'
            panel.style.transform = 'translate(-50%, -50%)'
            panel.style.width = 'auto'
            panel.style.height = 'auto'
            panel.style.maxWidth = '90vw'
            panel.style.maxHeight = '90vh'
            panel.style.alignItems = 'center'
            panel.style.justifyContent = 'center'
        }
    }, 0)
}

// ✅ 將函數掛到全局，可直接 onclick="showAuthPopup()"
window.showAuthPopup = showAuthPopup

//登錄請求api
const getToken = () => sessionStorage.getItem('ACCESS_TOKEN')
const saveToken = (token) => {
    sessionStorage.setItem('ACCESS_TOKEN', token)
}

const clearToken = () => {
    sessionStorage.removeItem('ACCESS_TOKEN')
    sessionStorage.removeItem('TOKEN_EXP')
}
async function api(path, { method = 'GET', headers = {}, body = null } = {}) {
    const token = getToken()
    const WEB_BASE = window.WEB_BASE || 'http://localhost:5000'
    if (token) headers['Authorization'] = `Bearer ${token}`
    const res = await fetch(WEB_BASE + path, { method, headers, body })
    if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `請求失敗：${res.status}`)
    }
    const ct = res.headers.get('content-type') || ''
    return ct.includes('application/json') ? res.json() : res.text()
}

/**
 * 驗證當前用戶是否已登入
 * @param {Event} [e] - 點擊事件，可選。如果傳入會自動 preventDefault/stopPropagation
 * @param popup_bool - 是否顯示彈窗
 * @returns {Promise<false | { id: string|number, username: string }>}
 *          - false = 未登入（事件已攔截，並彈出提示）
 *          - {id, username} = 已登入，用戶資訊
 */
async function ensureAuthenticated(e,popup_bool = true) {
    try {
        const res = await api('/auth/me');
        if (res && res.id && res.username) {
            // ✅ 已登入 → 返回用戶信息
            return { id: res.id, username: res.username };
        }
    } catch (err) {
        if (err.status === 401) {
            clearToken();  // 明確知道是 token 無效才清掉
        }
    }
    // ❌ 未登入 → 攔截事件
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    if (popup_bool) {// 提示登入
        showAuthPopup();
    }
    return false;
}

async function update_userdatas_bytoken(token,console_log = false) {
    try {
        const userRes = await fetch(`${window.WEB_BASE}/auth/me`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
        if (console_log) {
            if (userRes.ok) {
                const userData = await userRes.json();
                window.currentUser = userData;
                console.log("✅ 用戶資料已更新", userData);
                return userData; // 可選：回傳資料供外部使用
            } else {
                console.warn("⚠️ /auth/me 回傳非 200 狀態");
                return null;
            }
        };
    } catch (err) {
        console.error("❌ 無法更新用戶資料", err);
        return null;
    }
}


