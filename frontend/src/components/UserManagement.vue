
<template>
  <div>
    <h2>用戶管理系統</h2>

    <div class="top-controls">
      <div class="button-container0">
        <button @click="goToCreateUser">創建新用戶</button>
        <button @click="apidetail">近期api調用</button>
        <button @click="viewAllCustom">所有數據</button>
        <button @click="checkServerStatus">服務器</button>
      </div>
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
        <th @click="sortData('data_count')" style="font-size:12px;padding:0">數據總數 <span :class="getArrowClass('data_count')" ></span></th>
        <th style="justify-items: center">管理員操作</th>
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
        <td>{{ user.data_count }}條</td> <!-- 顯示用戶的數據總數 -->
        <td>
          <div class="button-container">
            <button @click="goToCustomPerUser(user)">用戶數據</button>
            <button @click="viewUserStats(user)">api統計</button>
            <button @click="editUser(user)">編輯賬號</button>
          </div>
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
  </div>
</template>
<script>
import api from '../axios'; // 引入我們的 axios 配置

export default {
  data() {
    return {
      users: [],
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
    checkServerStatus() {
      // 新分頁打開阿里雲服務器控制台
      window.open('https://ecs.console.aliyun.com/server/region/cn-shenzhen#/', '_blank');
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

.button-container {
  display: flex;
  justify-content: flex-start;  /* 按钮从左侧开始 */
  gap: 5px;                    /* 按钮间距 */
  flex-wrap: nowrap;            /* 强制按钮不换行 */
  overflow: hidden;             /* 超出部分隐藏 */
  width: 100%;                  /* 容器宽度为100% */
  white-space: nowrap;          /* 保证按钮文本不换行 */
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
  border-color: #217825;  /* 聚焦时输入框的绿色边框 */
  outline: none;
}

table {
  width: 80%;  /* 可根据需要调整宽度 */
  border-collapse: collapse;
  margin: 20px auto 0;
  border-radius: 12px;
  overflow: hidden;
  background-color: #f1f8e9;  /* 苹果绿色背景 */
  border: 1px solid #81c784; /* 苹果绿色边框 */
}

th, td {
  padding: 12px 18px;
  text-align: left;
  font-size: 16px;
}

th {
  background-color: #a5d6a7;  /* 更深的绿色作为表头背景 */
  color: #333;
  font-weight: 600;
  white-space: nowrap;  /* 防止表头文字换行 */
}

tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: rgba(187, 234, 196, 0.34);  /* 行悬停时的背景颜色 */
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
  background-color: #4CAF50; /* 按钮的苹果绿色 */
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

.top-controls {
  display: flex;
  justify-content: center!important;  /* 居中按钮和搜索框 */
  align-items: center;      /* 垂直居中 */
  gap: 10px;                /* 按钮和搜索框之间的间距 */
  flex-wrap: wrap;          /* 如果空间不足，允许换行 */
  width: 100%;              /* 确保容器宽度为100% */
}

.button-container0 button {
  padding: 10px 20px;
}

/* 按钮容器，确保按钮水平居中 */
.button-container0 {
  display: flex;
  justify-content: center;  /* 水平居中按钮 */
  gap: 10px;                /* 按钮之间的间距 */
  flex-wrap: nowrap;          /* 如果空间不足，允许换行 */
  max-width: 500px;         /* 最大宽度控制 */
  width: 100%;              /* 确保按钮容器宽度为100% */
}

/* 搜索框容器 */
.search-container {
  display: flex;
  justify-content: center;  /* 让搜索框居中 */
  align-items: center;      /* 垂直居中 */
  flex-grow: 1;             /* 让搜索框占据剩余空间 */
  max-width: 400px;         /* 限制搜索框的最大宽度 */
  flex-shrink: 0;           /* 确保搜索框不会缩小 */
  justify-self: center;
}

/* 搜索框样式 */
.search-container input {
  width: 100%;  /* 搜索框占据父容器的宽度 */
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
  border-color: #4CAF50;  /* 聚焦时的绿色边框 */
  box-shadow: 0 0 10px #217825;  /* 聚焦时的绿色阴影 */
  background: linear-gradient(145deg, #e0e0e0, #f0f0f0);  /* 聚焦时背景色变化 */
}

.search-container input::placeholder {
  color: #aaa;  /* 设置占位符颜色 */
  opacity: 1;  /* 确保占位符始终显示 */
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
  .pagination-controls button {
    font-size: 12px;  /* 调整分页按钮大小 */
  }
}

</style>


