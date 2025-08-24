
<template>
  <div>
    <h2>用戶列表</h2>

    <!-- 創建用戶按鈕 -->
    <button @click="goToCreateUser">創建新用戶</button>
    <button @click="apidetail">近期API調用</button>
    <button @click="viewAllCustom">所有用戶數據</button>

    <table v-if="users.length">
      <thead>
      <tr>
        <th>用戶名</th>
        <th>Email</th>
        <th>數據總數</th> <!-- 新增的列 -->
        <th>管理員操作</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="user in users" :key="user.id">
        <!-- 根據 role 判斷背景顏色，如果是 admin，就將背景色設置為暗紅色 -->
        <td :style="{ backgroundColor: user.role === 'admin' ? 'rgba(246,121,121,0.62)' : 'transparent' }">
          {{ user.username }}
        </td>
        <td>{{ user.email }}</td>
        <td>{{ user.data_count }}</td> <!-- 顯示用戶的數據總數 -->
        <td>
          <button @click="goToCustomPerUser(user)">個人數據</button>
          <button @click="viewUserStats(user)">查看統計信息</button>
          <button @click="editUser(user)">編輯</button>
          <button @click="showDeleteConfirm(user)">刪除</button>
        </td>
      </tr>
      </tbody>
    </table>

    <!-- 自定義刪除確認彈窗 -->
    <div v-if="showConfirmDialog" class="overlay">
      <div class="confirm-dialog">
        <p>你確定要刪除用戶 {{ confirmUser?.username }} 嗎？</p>
        <button @click="confirmDelete">確定</button>
        <button @click="cancelDelete">取消</button>
      </div>
    </div>
  </div>
</template>
<script>
import api from '../axios'; // 引入我們的 axios 配置

export default {
  data() {
    return {
      users: [],
      showConfirmDialog: false,  // 控制彈窗顯示
      confirmUser: null,  // 儲存選中的用戶
      newUser: { username: '', email: '' } // 新用戶的數據
    };
  },
  methods: {
    // 獲取用戶列表
    async getUsers() {
      try {
        // 獲取用戶列表
        const response = await api.get('/users/all');
        const users = response.data;

        // 獲取每個用戶的數據總數
        const dataCountResponse = await api.get('/custom-query/num');
        const dataCounts = dataCountResponse.data;
        // 將數據總數與用戶列表合併
        users.forEach(user => {
          const userData = dataCounts.find(item => item.username === user.username);
          user.data_count = userData ? userData.data_count : 0;  // 如果沒有數據則設為 0
        });

        this.users = users;
      } catch (error) {
        console.error('Error fetching users', error);
        if (error.response && error.response.status === 401) {
          alert('Token 無效或已過期，請重新登錄');
          this.$router.push({name: 'Login'});
        }
      }
    },

    // 詳細api
    async apidetail(user) {
      this.$router.push({name: 'ApiDetail'});
    },

    // 跳轉到創建用戶頁面
    goToCreateUser() {
      this.$router.push({ name: 'CreateUser' });  // 跳轉到創建用戶頁面
    },

    // 顯示刪除確認彈窗
    showDeleteConfirm(user) {
      this.showConfirmDialog = true;
      this.confirmUser = user;  // 存儲需要刪除的用戶
    },

    // 確認刪除
    async confirmDelete() {
      try {
        await api.delete(`/users/delete?query=${this.confirmUser.username}`);  // 刪除用戶
        this.users = this.users.filter((u) => u.id !== this.confirmUser.id);
        this.showConfirmDialog = false;  // 關閉彈窗
      } catch (error) {
        this.showConfirmDialog = false;  // 關閉彈窗
        // 捕獲錯誤並顯示詳細錯誤信息
        if (error.response && error.response.data && error.response.data.detail) {
          alert(`刪除用戶失敗: ${error.response.data.detail}`);
        } else {
          // 如果沒有詳細錯誤信息，顯示通用錯誤
          alert('刪除用戶失敗，請稍後再試');
        }
      }
    },

    // 取消刪除
    cancelDelete() {
      this.showConfirmDialog = false;  // 關閉彈窗
    },

    // 查看用戶統計
    async viewUserStats(user) {
      this.$router.push({name: 'UserStats', query: {username: user.username}});
    },
    async viewAllCustom() {
      this.$router.push({name: 'Custom'});
    },

    // 編輯用戶
    async editUser(user) {
      this.$router.push({name: 'EditUser', query: {username: user.username, email: user.email}});
    },
    // 查看用戶個人界面
    goToCustomPerUser(user) {
      this.$router.push({ name: 'PerUser' ,query: {username: user.username}});  // 跳轉到創建用戶頁面
    },

  },
  mounted() {
    this.getUsers();  // 加載用戶列表
  }
};
</script>

<style scoped>
/* 一些簡單的樣式 */
form div {
  margin-bottom: 10px;
}

button {
  margin-top: 10px;
  padding: 5px 15px;
  font-size: 16px;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.confirm-dialog {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

input {
  padding: 8px;
  margin-top: 5px;
  width: 100%;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 10px;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}

td {
  border-top: 1px solid #e0e0e0;
}

button {
  cursor: pointer;
}
</style>

<style scoped>
/* 彈窗樣式 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.confirm-dialog {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

button {
  margin: 5px;
}
</style>
