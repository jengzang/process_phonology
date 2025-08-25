
<template>
  <div>
    <h2>用戶管理系統</h2>

    <div class="top-controls">
      <button @click="goToCreateUser">創建新用戶</button>
      <button @click="apidetail">近期API調用</button>
      <button @click="viewAllCustom">所有用戶數據</button>
      <!-- 搜索框 -->
      <div class="search-container">
        <input v-model="searchQuery"  @input="searchUser" type="text" placeholder="搜索用戶名或郵箱" />
      </div>
    </div>

    <table v-if="users.length">
      <thead>
      <tr>
        <th @click="sortData('username')">用戶名 <span :class="getArrowClass('username')"></span></th>
        <th @click="sortData('email')">Email <span :class="getArrowClass('email')"></span></th>
        <th @click="sortData('data_count')">數據總數 <span :class="getArrowClass('data_count')"></span></th>
        <th>管理員操作</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="user in currentPageData" :key="user.id">
        <!-- 根據 role 判斷背景顏色，如果是 admin，就將背景色設置為暗紅色 -->
        <td>
          <span v-if="user.role === 'admin'" style="font-weight: bold;" title="管理员">🛠️</span>
          <span :style="{ fontWeight: user.role === 'admin' ? 'bold' : 'normal' }" :title="user.role === 'admin' ? '管理员' : ''">
            {{ user.username }}
          </span>
        </td>


        <td>{{ user.email }}</td>
        <td>{{ user.data_count }}</td> <!-- 顯示用戶的數據總數 -->
        <td>
          <button @click="goToCustomPerUser(user)">個人數據</button>
          <button @click="viewUserStats(user)">統計信息</button>
          <button @click="editUser(user)">編輯</button>
          <button @click="showDeleteConfirm(user)">刪除</button>
        </td>
      </tr>
      </tbody>
    </table>

    <h3 v-else>🤷‍♂️<br>無用戶數據</h3>
    <!-- 分頁控制 -->
    <div class="pagination-controls">
      <button @click="prevPage" :disabled="currentPage === 1">上一頁</button>
      <span>頁面 {{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">下一頁</button>
    </div>

    <div class="logout-button-container">
      <button @click="logout">返回網站</button>
    </div>

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
      searchQuery: '',  // 用于存储搜索框的内容
      searchResultIndex: -1,  // 存储匹配的行索引
      filteredUsers: [],  // 新增的字段，确保 Vue 可以访问它
      confirmUser: null,  // 儲存選中的用戶
      newUser: { username: '', email: '' }, // 新用戶的數據
      currentPage: 1,  // 当前页码
      pageSize: 30,  // 每页显示的记录数
      totalPages: 1,  // 总页数
      sortOrder: {  // 控制排序的对象
        username: 'asc',
        email: 'asc',
        data_count: 'asc',
      },
      username: '',  // 当前的用户名
    };
  },
  methods: {
    async getUsers() {
      try {
        // 调用获取用户数据的函数
        await this.fetchUserData();
      } catch (error) {
        // console.error('Error fetching users', error);
        if (error.response && error.response.status === 401) {
          alert('Token 无效或已过期，请重新登录');

          // 延迟 0.5 秒后重试
          setTimeout(async () => {
            try {
              await this.fetchUserData();  // 重新调用获取数据函数
            } catch (retryError) {
              console.error('Retry failed', retryError);
              this.$router.push({ name: 'Login' });  // 如果重试失败，跳转到登录页面
            }
          }, 500);  // 延迟 0.5 秒（500 毫秒）
        }
      }
    },

// 封装获取用户数据的函数
    async fetchUserData() {
      const response = await api.get('/users/all');
      const users = response.data;

      const dataCountResponse = await api.get('/custom/num');
      const dataCounts = dataCountResponse.data;

      // 将数据总数与用户列表合并
      users.forEach(user => {
        const userData = dataCounts.find(item => item.username === user.username);
        user.data_count = userData ? userData.data_count : 0;
      });

      this.users = users;
      this.totalPages = Math.ceil(this.users.length / this.pageSize);  // 计算总页数
    },

    // 获取箭头的 CSS 类
    getArrowClass(field) {
      return this.sortOrder[field] === 'asc' ? 'arrow-up' : 'arrow-down';
    },

    searchUser() {
      // console.log("Search Query:", this.searchQuery);  // 调试：打印搜索框输入的内容
      const searchQueryLower = this.searchQuery.toLowerCase();

      // 过滤符合条件的用户
      this.filteredUsers = this.users.filter(user =>
          (user.username && user.username.toLowerCase().includes(searchQueryLower)) ||
          (user.email && user.email.toLowerCase().includes(searchQueryLower))
      );

      // console.log("Filtered Users:", this.filteredUsers);  // 调试：打印过滤后的用户

      this.currentPage = 1;
      this.totalPages = Math.ceil(this.filteredUsers.length / this.pageSize);
    },


    // 排序方法
    sortData(field) {
      const currentOrder = this.sortOrder[field] === 'asc' ? 'desc' : 'asc';
      this.sortOrder[field] = currentOrder;

      if (field === 'username' || field === 'email') {
        // 字符串字段排序
        this.users.sort((a, b) => {
          const valueA = a[field] || '';
          const valueB = b[field] || '';
          return currentOrder === 'asc' ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
        });
      } else if (field === 'data_count') {
        // 数字字段排序
        this.users.sort((a, b) => {
          return currentOrder === 'asc' ? a[field] - b[field] : b[field] - a[field];
        });
      }

      // 排序之后重新计算分页
      this.totalPages = Math.ceil(this.users.length / this.pageSize);
      this.currentPage = 1;  // 重置当前页为第一页
    },

    // 上一页
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },

    // 下一页
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
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
    logout() {
      // 退出後跳轉到 WEB_BASE
      window.location.href = window.WEB_BASE;
    },

  },
  computed: {
    // 当前页面的数据
    currentPageData() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      const currentData = this.searchQuery ? this.filteredUsers : this.users; // 如果有搜索，使用 filteredUsers 否则使用原始 users
      if (!Array.isArray(currentData)) return [];
      return currentData.slice(startIndex, startIndex + this.pageSize);  // 根据当前页码和每页显示的数据数量筛选
    },
  },
  mounted() {
    this.getUsers();  // 加載用戶列表
  }
};
</script>

<style scoped>
/* 一些简单的样式 */
form div {
  margin-bottom: 15px;
}

button {
  margin-top: 10px;
  margin-left: 10px;
  margin-right: 10px;
  padding: 8px 16px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 12px;
  background-color: #4CAF50;  /* 苹果风格的蓝色 */
  color: white;
  border: none;
  transition: background-color 0.3s ease, transform 0.2s ease;
  max-width: 150px;
}

button:hover {
  background-color: #217825; /* 鼠标悬停时的深蓝色 */
  transform: scale(1.05); /* 按钮放大 */
}

button:disabled {
  background-color: rgba(42, 175, 53, 0.34); /* 禁用按钮的背景颜色 */
  cursor: not-allowed; /* 禁用时的鼠标样式 */
}

input {
  padding: 10px;
  margin-top: 5px;
  width: 100%;
  border-radius: 12px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #217825;  /* 聚焦时输入框的蓝色边框 */
  outline: none;
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

table {
  width: 80%;  /* 可根据需要调整宽度 */
  /* 使表格居中 */
  border-collapse: collapse;
  margin: 20px auto 0;
  border-radius: 12px;
  overflow: hidden;
}

th, td {
  padding: 12px 18px;
  text-align: left;
  font-size: 16px;
}

th {
  background-color: #f2f2f2;
  color: #333;
  font-weight: 600;
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: rgba(187, 209, 234, 0.34);  /* 行悬停时的背景颜色 */
}

.arrow-up::after {
  content: '↑';
  margin-left: 5px;
  font-size: 14px;
}

.arrow-down::after {
  content: '↓';
  margin-left: 5px;
  font-size: 14px;
}


.pagination-controls {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.pagination-controls button {
  padding: 12px 24px;
  margin: 0 12px;
  background-color: #4CAF50; /* 按钮的苹果蓝 */
  color: white;
  border: none;
  border-radius: 20px; /* 圆角效果 */
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  max-width: 120px;
}

.pagination-controls button:hover {
  background-color: #217825;
  transform: scale(1.05);
}

.pagination-controls button:disabled {
  background-color: rgba(42, 175, 53, 0.34);
  cursor: not-allowed;
}

.pagination-controls span {
  font-size: 16px;
  color: #333;
  align-self: center;
}

/* 控制按钮和搜索框在同一行 */
.top-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px; /* 给按钮和搜索框之间加个间距 */
}

/* 搜索框的样式 */
.search-container {
  flex-grow: 1;  /* 让搜索框占据剩余的空间 */
  max-width: 400px;  /* 限制搜索框的最大宽度 */
  flex-shrink: 0;  /* 确保搜索框不会缩小 */
  display: flex;
  justify-content: center;
}

.search-container input {
  width: 100%;  /* 让输入框填充父容器的宽度 */
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 25px;
  border: 1px solid #d1d1d1;
  background: linear-gradient(145deg, #f0f0f0, #e0e0e0);  /* 渐变背景色 */
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.1), -4px -4px 10px rgba(255, 255, 255, 0.1);  /* 立体阴影 */
  transition: all 0.3s ease-in-out;  /* 添加平滑过渡 */
}

.search-container input:focus {
  outline: none;
  border-color: #4CAF50;  /* 聚焦时的蓝色边框 */
  box-shadow: 0 0 10px #217825;  /* 聚焦时的蓝色阴影 */
  background: linear-gradient(145deg, #e0e0e0, #f0f0f0);  /* 聚焦时背景色变化 */
}

.search-container input::placeholder {
  color: #aaa;  /* 设置占位符颜色 */
  opacity: 1;  /* 确保占位符始终显示 */
}

/* 退出按鈕容器 */
.logout-button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;  /* 給退出按鈕上方加點間距 */
}

.logout-button-container button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #9a2118;  /* 退出按鈕的顏色 */
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  max-width: 120px;
}

.logout-button-container button:hover {
  background-color: #3a0b0b;  /* 鼠標懸停時的顏色 */
  transform: scale(1.05);
}

.logout-button-container button:disabled {
  background-color: rgba(244, 67, 54, 0.34);
  cursor: not-allowed;
}

/* 在移动端时调整 */
@media (max-width: 768px) {
  table {
    width: 100%;  /* 在小屏幕上设置表格宽度为100% */
    overflow-x: auto;  /* 允许在小屏幕上水平滚动 */
    display: block; /* 使表格成为块级元素，启用水平滚动 */
  }

  th, td {
    padding: 8px 12px; /* 调整内边距，使内容适应屏幕 */
    font-size: 14px;  /* 调整字体大小 */
  }

  button {
    padding: 8px 16px;
    font-size: 14px;  /* 调整按钮大小 */
    max-width: 100px;
  }

  .pagination-controls button {
    padding: 8px 16px;
    font-size: 14px;  /* 调整分页按钮大小 */
  }

  /* 对话框调整 */
  .confirm-dialog {
    width: 90%;  /* 弹窗在小屏幕上占宽度的90% */
  }

  .top-controls {
    flex-wrap: wrap; /* 让控件在移动端可以换行 */
    justify-content: flex-start;  /* 左对齐 */
  }

  .search-container {
    max-width: 100%; /* 确保搜索框在小屏幕上占满 */
  }
}

@media (max-width: 480px) {
  table {
    font-size: 12px;  /* 在更小的设备上，进一步缩小字体 */
  }

  button {
    padding: 6px 12px;  /* 更小的按钮 */
    font-size: 12px;
  }

  .pagination-controls button {
    font-size: 12px;  /* 调整分页按钮大小 */
  }
}


</style>

