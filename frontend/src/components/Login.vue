<template>
  <div>
    <h2>登錄</h2>
    <form @submit.prevent="login">
      <div>
        <label for="username">用戶名</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div>
        <label for="password">密碼</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">登錄</button>
    </form>
    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
  </div>
</template>

<script>
import api from '../api';  // 根據實際路徑調整

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
        const form = new URLSearchParams();
        form.append('username', this.username);
        form.append('password', this.password);
        const res = await api('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form,
        });


        const { access_token } = res;  // 解構 res 物件中的 access_token

        // 儲存 Token
        localStorage.setItem('ACCESS_TOKEN', access_token);

        // 登錄成功後，跳轉到後台頁面或主頁
        this.$router.push({ name: 'Home' }); // 假設有一個 Home 頁面

      } catch (error) {
        console.error('Login failed:', error.response?.data || error.message);
        this.errorMessage = '登錄失敗，請檢查用戶名或密碼';
      }
    },
  },
};
</script>
