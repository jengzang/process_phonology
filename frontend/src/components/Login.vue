<template>
  <div class="login-container">
    <h2>登錄</h2>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">用戶名</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">密碼</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">登錄</button>
    </form>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<script>
import api from '../utils';  // 根據實際路徑調整

export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
    };
  },
  methods: {
    async login() {
      try {
        // 准备请求数据
        const form = new URLSearchParams();
        form.append('username', this.username);
        form.append('password', this.password);

        // 发起登录请求
        const res = await api('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form,
        });

        const { access_token } = res;  // 解构响应中的 access_token

        // 保存 Token 到 localStorage
        localStorage.setItem('ACCESS_TOKEN', access_token);

        // 登录成功后跳转，如果要确保跳转正确，检查页面是否需要刷新
        this.redirectAfterLogin();

      } catch (error) {
        console.error('Login failed:', error.response?.data || error.message);
        this.errorMessage = '登录失败，用户名或密码错误';
      }
    },

    // 统一跳转逻辑
    redirectAfterLogin() {
      setTimeout(() => {
        // 使用 push 来触发路由跳转并确保重新加载
        this.$router.replace({ name: 'Home' });
      }, 500);  // 延迟 500 毫秒（0.5 秒）
    }
  },
};

</script>

<style scoped>
/* 使用绿色苹果风格的样式 */

.login-container {
  width: 100%;
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 15px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  font-size: 24px;
  color: #2c6e49;  /* 苹果风格绿色 */
  font-weight: bold;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  font-size: 16px;
  color: #333;
}

input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 25px;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
  margin-top: 5px;
  transition: all 0.3s ease-in-out;
}

input:focus {
  outline: none;
  border-color: #4CAF50;  /* 聚焦时的绿色边框 */
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);  /* 聚焦时的绿色阴影 */
  background-color: #eafaf0;  /* 聚焦时背景色变化 */
}

button {
  width: 100%;
  padding: 12px;
  font-size: 18px;
  color: white;
  background-color: #4CAF50; /* 苹果绿色 */
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

button:hover {
  background-color: #45a049;  /* 深绿色 */
  transform: scale(1.05); /* 鼠标悬停时按钮稍微放大 */
}

button:disabled {
  background-color: rgba(76, 175, 80, 0.5);
  cursor: not-allowed;
}

.error-message {
  text-align: center;
  color: red;
  font-size: 14px;
  margin-top: 15px;
}
</style>
