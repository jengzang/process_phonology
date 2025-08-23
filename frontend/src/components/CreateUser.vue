<template>
  <div>
    <h2>創建新用戶</h2>

    <form @submit.prevent="createUser">
      <div class="form-group">
        <label for="username">用戶名:</label>
        <input
            id="username"
            v-model="newUser.username"
            placeholder="請輸入用戶名"
            required
        />
      </div>

      <div class="form-group">
        <label for="email">郵箱:</label>
        <input
            id="email"
            v-model="newUser.email"
            type="email"
            placeholder="請輸入郵箱"
            required
        />
      </div>

      <div class="form-group">
        <label for="password">密碼:</label>
        <input
            id="password"
            v-model="newUser.password"
            type="password"
            placeholder="請輸入密碼"
            required
        />
      </div>

      <div class="form-group">
        <label for="role">角色:</label>
        <select v-model="newUser.role" required>
          <option value="user">普通用戶</option>
          <option value="admin">管理員</option>
        </select>
      </div>

      <button type="submit">創建用戶</button>
    </form>
  </div>
</template>

<script>
import api from '../axios';  // 引入我們的 axios 配置

export default {
  data() {
    return {
      newUser: {
        username: '',
        email: '',
        password: '',
        role: 'user'  // 默認角色是 'user'
      }
    };
  },
  methods: {
    async createUser() {
      try {
        const response = await api.post('/users/create', this.newUser);
        alert('用戶創建成功!');
        this.$router.push({ name: 'Home' });  // 成功後跳轉回用戶管理頁面
      } catch (error) {
        // 捕獲錯誤並顯示詳細錯誤信息
        if (error.response && error.response.data && error.response.data.detail) {
          alert(`創建用戶失敗: ${error.response.data.detail}`);
        } else {
          // 如果沒有詳細錯誤信息，顯示通用錯誤
          alert('創建用戶失敗，請稍後再試');
        }
        console.error('Error creating user', error);
      }
    }
  }
};
</script>

<style scoped>
/* 表單樣式 */
.form-group {
  margin-bottom: 15px;
}

input, select {
  width: 100%;
  padding: 8px;
  font-size: 16px;
  border-radius: 4px;
  margin-top: 5px;
}

button {
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
}

button:hover {
  background-color: #0056b3;
}
</style>
