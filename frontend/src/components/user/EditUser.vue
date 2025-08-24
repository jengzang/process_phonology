<template>
  <div>
    <h2>編輯用戶</h2>

    <!-- 顯示原始的用戶名和郵箱 -->
    <div v-if="oldname && oldemail" class="user-info">
      <p><strong>當前用戶名:</strong> {{ oldname }}</p>
      <p><strong>當前郵箱:</strong> {{ oldemail }}</p>
    </div>

    <!-- 用戶更新表單 -->
    <form @submit.prevent="updateUser" class="update-form">
      <!-- 用戶名輸入框 -->
      <div class="form-group">
        <label for="username">新用戶名:</label>
        <input
            id="username"
            v-model="updatedUser.username"
            placeholder="請輸入新用戶名"
            class="form-control"
        />
      </div>

      <button type="button" @click="updateUsername" class="btn btn-primary">更新用戶名</button>

      <!-- 郵箱輸入框 -->
      <div class="form-group">
        <label for="email">新郵箱:</label>
        <input
            id="email"
            v-model="updatedUser.email"
            placeholder="請輸入新郵箱"
            class="form-control"
        />
      </div>
      <!-- 更新按鈕 -->
      <button type="button" @click="updateEmail" class="btn btn-secondary">更新郵箱</button>
    </form>
    <button @click="goToHome">返回首頁</button>
  </div>
</template>

<script>
import api from '../../axios.js';  // 引入我們的全局 axios 配置

export default {
  data() {
    return {
      updatedUser: { username: '', email: '' },  // 用來存放用戶更新的數據
      oldname: this.$route.query.username,       // 從路由中獲取原始用戶名
      oldemail: this.$route.query.email,         // 從路由中獲取原始郵箱
    };
  },
  methods: {
    // 更新用戶名
    async updateUsername() {
      if (this.updatedUser.username && this.updatedUser.username !== this.oldname) {
        try {
          await api.put(`/users/update?query=${this.oldname}`, { username: this.updatedUser.username });
          alert('用戶名更新成功!');
          this.oldname = this.updatedUser.username; // 更新顯示的用戶名
        } catch (error) {
          // 捕獲錯誤並顯示詳細錯誤信息
          if (error.response && error.response.data && error.response.data.detail) {
            alert(`編輯用戶失敗: ${error.response.data.detail}`);
          } else {
            // 如果沒有詳細錯誤信息，顯示通用錯誤
            alert('編輯用戶失敗，請稍後再試');
          }
        }
      } else {
        alert('請輸入有效的用戶名');
      }
    },

    // 更新郵箱
    async updateEmail() {
      if (this.updatedUser.email && this.updatedUser.email !== this.oldemail) {
        try {
          await api.put(`/users/update?query=${this.oldemail}`, { email: this.updatedUser.email });
          alert('郵箱更新成功!');
          this.oldemail = this.updatedUser.email; // 更新顯示的郵箱
        } catch (error) {
          console.error('Error updating email', error);
        }
      } else {
        alert('請輸入有效的郵箱');
      }
    },

    // 初始化頁面時，根據路由參數獲取用戶數據
    async mounted() {
      if (this.oldname || this.oldemail) {
        try {
          // 根據用戶名或郵箱查詢用戶數據
          const response = await api.get(`/users/single?query=${this.oldname || this.oldemail}`);
          this.updatedUser.username = response.data.username;
          this.updatedUser.email = response.data.email;
        } catch (error) {
          console.error('Error fetching user data', error);
        }
      }
    },
    goToHome(){
      this.$router.push({name: 'Home'});
    },
  }
};
</script>

<style scoped>
/* 優化排版樣式 */
.user-info {
  margin-bottom: 20px;
}

.user-info p {
  margin: 5px 0;
}

.update-form {
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  font-size: 18px;
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.form-control {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 10px; /* 圓角設計 */
  transition: all 0.3s ease; /* 平滑過渡 */
}

.form-control:focus {
  border-color: #4CAF50; /* 聚焦時綠色邊框 */
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.5); /* 聚焦時陰影 */
}


button {
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 10px; /* 圓角設計 */
  margin-bottom: 30px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  border: none;
}

.btn-primary {
  background-color: #4CAF50; /* 綠色按鈕 */
  color: white;
}

.btn-primary:hover {
  background-color: #45a049; /* 按鈕懸停顏色 */
  transform: scale(1.05);
}

.btn-secondary {
  background-color: #8bc34a; /* 淺綠色 */
  color: white;
}

.btn-secondary:hover {
  background-color: #7cb342; /* 按鈕懸停顏色 */
  transform: scale(1.05);
}

button:active {
  transform: scale(0.98);
}
</style>
