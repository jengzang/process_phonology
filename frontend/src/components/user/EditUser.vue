<template>
  <div>
    <h2>編輯用戶<strong> {{ oldname }} </strong> </h2>
    <h3> 當前郵箱:{{ oldemail }}</h3>
    <!-- 用戶更新表單 -->
    <form @submit.prevent="updateUser" class="update-form">
      <!-- 用戶名輸入框 -->
      <div class="form-group">
        <label for="username">更新用戶名:</label>
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
        <label for="email">更新郵箱:</label>
        <input
            id="email"
            v-model="updatedUser.email"
            placeholder="請輸入新郵箱"
            class="form-control"
        />
      </div>
      <!-- 更新按鈕 -->
      <button type="button" @click="updateEmail" class="btn btn-secondary">更新郵箱</button>

      <!-- 密碼輸入框 -->
      <div class="form-group">
        <label for="email">更改密碼:</label>
        <input
            id="email"
            v-model="updatedUser.password"
            placeholder="請輸入新密碼"
            class="form-control"
        />
      </div>
      <!-- 更新按鈕 -->
      <button type="button" @click="updatePassword" class="btn btn-secondary">更改密碼</button>

    </form>

    <!-- 設置為管理員按鈕 -->
    <button type="button" @click="showSetAdminConfirm" class="btn btn-secondary" style="background: darkblue">設置為管理員</button>

    <!-- 刪除按鈕 -->
    <button type="button" @click="showDeleteConfirm(oldname)" class="btn-primary" style="background: darkred">刪除用戶</button>

    <!-- 返回首頁按鈕 -->
    <button type="button" @click="goToHome" class="btn-primary" style="background: darkgoldenrod">返回首頁</button>

    <!-- 自定義設置為管理員確認彈窗 -->
    <div v-if="showAdminConfirmDialog" class="overlay">
      <div class="confirm-dialog">
        <p>你確定要將用戶 {{ oldname }} 設置為管理員嗎？</p>
        <button @click="confirmSetAdmin" class="btn-primary" style="background: #4CAF50;">確定</button>
        <button @click="cancelSetAdmin" class="btn-secondary" style="background: darkgoldenrod">取消</button>
      </div>
    </div>

    <!-- 自定義刪除確認彈窗 -->
    <div v-if="showConfirmDialog" class="overlay">
      <div class="confirm-dialog">
        <p>你確定要刪除用戶 {{ confirmUser?.username }} 嗎？</p>
        <button @click="confirmDelete" class="btn-primary" style="background: #9a2118;">删除</button>
        <button @click="cancelDelete" class="btn-secondary" style="background: darkgoldenrod">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../axios.js';  // 引入我們的全局 axios 配置

export default {
  data() {
    return {
      updatedUser: { username: '', email: '', password: '' },  // 用來存放用戶更新的數據
      oldname: this.$route.query.username,       // 從路由中獲取原始用戶名
      oldemail: this.$route.query.email,         // 從路由中獲取原始郵箱
      showConfirmDialog: false,  // 控制彈窗顯示
      showAdminConfirmDialog: false,  // 控制設置管理員的確認彈窗顯示
    };
  },
  methods: {
    // 更新用戶名
    async updateUsername() {
      if (this.updatedUser.username && this.updatedUser.username !== this.oldname) {
        try {
          await api.put(`/users/update?query=${this.oldname}`, { username: this.updatedUser.username });
          this.$message.success('用戶名更新成功!');
          this.oldname = this.updatedUser.username; // 更新顯示的用戶名
        } catch (error) {
          // 捕獲錯誤並顯示詳細錯誤信息
          if (error.response && error.response.data && error.response.data.detail) {
            this.$message.error(`編輯用戶名失敗: ${error.response.data.detail}`);
          } else {
            this.$message.error('編輯用戶名失敗，請稍後再試');
          }
        }
      } else {
        this.$message.warning('請輸入有效的用戶名');
      }
    },

    // 更新郵箱
    async updateEmail() {
      const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/; // 郵箱格式正則表達式
      if (!this.updatedUser.email || !emailPattern.test(this.updatedUser.email)) {
        this.$message.warning('請輸入有效的郵箱地址');
        return;
      }
      if (this.updatedUser.email && this.updatedUser.email !== this.oldemail) {
        try {
          await api.put(`/users/update?query=${this.oldemail}`, { email: this.updatedUser.email });
          this.$message.success('郵箱更新成功!');
          this.oldemail = this.updatedUser.email; // 更新顯示的郵箱
        } catch (error) {
          // 捕獲錯誤並顯示詳細錯誤信息
          if (error.response && error.response.data && error.response.data.detail) {
            this.$message.error(`編輯郵箱失敗: ${error.response.data.detail}`);
          } else {
            this.$message.error('編輯郵箱失敗，請稍後再試');
          }
        }
      } else {
        this.$message.warning('請輸入有效的郵箱');
      }
    },

// 更新密碼
    async updatePassword() {
      const password = this.updatedUser.password;
      if (!password || password.length < 6) {
        this.$message.warning('密碼至少需要6個字符');
        return;
      }
      try {
        await api.put(`/users/password`, { username: this.oldname, password: password });
        this.$message.success('密碼更新成功!');
        this.updatedUser.password = ''; // 清空密碼框
      } catch (error) {
        // 捕獲錯誤並顯示詳細錯誤信息
        if (error.response && error.response.data && error.response.data.detail) {
          this.$message.error(`更新密碼失敗: ${error.response.data.detail}`);
        } else {
          this.$message.error('更新密碼失敗，請稍後再試');
        }
      }
    },

    // 設置當前用戶為管理員
    async confirmSetAdmin() {
      try {
        const response = await api.put('/users/let_admin', {
          username: this.oldname,
          role: 'admin'
        });
        this.$message.success('用戶已成功設置為管理員！');
        this.showAdminConfirmDialog = false;  // 隱藏彈窗
      } catch (error) {
        // 捕獲錯誤並顯示詳細錯誤信息
        if (error.response && error.response.data && error.response.data.detail) {
          this.$message.error(`設置管理員失敗: ${error.response.data.detail}`);
          this.showAdminConfirmDialog = false;  // 隱藏彈窗
        } else {
          this.$message.error('設置管理員失敗！' + (error.response?.data?.detail || ''));
          this.showAdminConfirmDialog = false;  // 隱藏彈窗
        }
      }
    },
    // 顯示設置為管理員的確認彈窗
    showSetAdminConfirm() {
      this.showAdminConfirmDialog = true;
    },
    // 取消設置為管理員
    cancelSetAdmin() {
      this.showAdminConfirmDialog = false;  // 隱藏彈窗
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

    // 顯示刪除確認彈窗
    showDeleteConfirm(user) {
      this.showConfirmDialog = true;
      this.confirmUser = user;  // 存儲需要刪除的用戶
    },

    // 確認刪除
    async confirmDelete() {
      try {
        // 進行刪除請求
        await api.delete(`/users/delete?query=${this.confirmUser}`);  // 刪除用戶

        // 顯示成功提示
        this.$message.success('用戶刪除成功！');
        // 關閉刪除確認彈窗
        this.showConfirmDialog = false;
        this.$router.push({ name: 'Home' });
      } catch (error) {
        // 關閉彈窗
        this.showConfirmDialog = false;

        // 捕獲錯誤並顯示詳細錯誤信息
        if (error.response && error.response.data && error.response.data.detail) {
          this.$message.error(`刪除用戶失敗: ${error.response.data.detail}`);
        } else {
          // 顯示通用錯誤信息
          this.$message.error('刪除用戶失敗，請稍後再試');
        }
      }
    },

    // 取消刪除
    cancelDelete() {
      this.showConfirmDialog = false;  // 關閉彈窗
    },


    goToHome() {
      this.$router.push({ name: 'Home' });
    },
  },
};
</script>


<style scoped>
/* 整體排版和設計 */
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
  padding: 12px;
  font-size: 16px;
  border: 1px solid #a8d5ba; /* 柔和的蘋果綠邊框 */
  border-radius: 12px; /* 圓角設計 */
  background-color: #f6fbf3; /* 淺綠色背景 */
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #60b68d; /* 聚焦時的柔和蘋果綠 */
  box-shadow: 0 0 10px rgba(96, 182, 141, 0.5); /* 聚焦時柔和的陰影 */
}

button {
  padding: 10px 16px;
  font-size: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  border: none;
  font-weight: 600;
  width: 100%; /* 保證按鈕的寬度一致 */
  max-width: 150px;
  margin-right: 20px;
  margin-left: 20px;
}

.btn-primary {
  background-color: #4CAF50; /* 正常狀態下的蘋果綠 */
  color: white;
}

.btn-primary:hover {
  background-color: #217825; /* 懸停時的深蘋果綠 */
  transform: scale(1.03);
}

.btn-primary:active {
  background-color: #1e7e1b; /* 按下時的更深的蘋果綠 */
  transform: scale(0.98);
}

.btn-secondary {
  background-color: #4CAF50; /* 使用與主按鈕相同的背景色 */
  color: white;
}

.btn-secondary:hover {
  background-color: #217825; /* 懸停時的顏色 */
  transform: scale(1.03);
}

.btn-secondary:active {
  background-color: #1e7e1b; /* 按下時的顏色 */
  transform: scale(0.98);
}

button:active {
  transform: scale(0.98);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}

.confirm-dialog {
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 400px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
}

.confirm-dialog h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.confirm-dialog button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #4CAF50; /* 蘋果綠背景 */
  border: none;
  border-radius: 12px;
  color: white;
  margin-top: 10px;
}

.confirm-dialog button:hover {
  background-color: #217825; /* 懸停時的顏色 */
}

.confirm-dialog button:active {
  background-color: #1e7e1b; /* 按下時的顏色 */
}
</style>


