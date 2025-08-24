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
import api from '../../axios.js';  // 引入我們的 axios 配置

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
  width: 100%;
  max-width: 600px; /* 设置表单最大宽度 */
  margin: 0 auto; /* 居中显示表单 */
}

input, select {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 12px; /* 更加圆润的输入框 */
  margin-top: 10px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  transition: all 0.3s ease;
  box-sizing: border-box; /* 确保内边距不会让元素撑开 */
}

/* 输入框聚焦时的效果 */
input:focus, select:focus {
  border-color: #28a745; /* 绿色的聚焦边框 */
  outline: none;
  box-shadow: 0 0 8px rgba(40, 167, 69, 0.3); /* 绿色阴影 */
}

/* 按钮样式 */
button {
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 12px;
  cursor: pointer;
  background-color: #28a745; /* 绿色按钮 */
  color: white;
  border: none;
  transition: background-color 0.3s ease, transform 0.2s ease;
  width: auto;  /* 按钮宽度自适应 */
  margin-top: 10px;
  display: inline-block;
}

/* 按钮悬停效果 */
button:hover {
  background-color: #218838; /* 深绿色 */
  transform: scale(1.05); /* 按钮放大 */
}

/* 按钮点击时的酷炫效果 */
button:active {
  transform: scale(0.98); /* 按钮点击时稍微缩小 */
  background-color: #1e7e34; /* 点击后的深绿色 */
}

button:disabled {
  background-color: #d6e9d7; /* 禁用按钮的颜色 */
  cursor: not-allowed;
}

/* 表单区域 */
.form-group label {
  font-weight: bold;
  color: #333;
}

.form-group input, .form-group select {
  font-family: 'Arial', sans-serif; /* 苹果风格的字体 */
}

/* 让所有的表单控件都更加现代 */
input, select {
  font-family: 'Arial', sans-serif;
}

</style>


