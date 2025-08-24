<template>
  <div>
    <h1>{{username}}的個人數據</h1>
    <div class="top-controls">
      <p>當前共有 {{ users.length }} 條數據</p>
      <button @click="goToCreateCustom(username)" >添加數據</button>
      <button @click="goToDeleteCustom(username)" style="background: darkred;">刪除數據</button>
      <button @click="goToEditCustom(username)" style="background: darkblue">編輯數據</button>
      <!-- 搜索框 -->
      <div class="search-container">
        <input v-model="searchQuery" @input="searchUser" type="text" placeholder="搜索用戶名、簡稱、音典分區、特徵、值、說明" />
      </div>
    </div>
    <table v-if="users.length" border="1">
      <thead>
      <tr>
        <th @click="sortData('簡稱')">簡稱 <span :class="getArrowClass('簡稱')"></span></th>
        <th @click="sortData('音典分區')">音典分區 <span :class="getArrowClass('音典分區')"></span></th>
        <th @click="sortData('經緯度')">經緯度 <span :class="getArrowClass('經緯度')"></span></th>
        <th @click="sortData('特徵')">特徵 <span :class="getArrowClass('特徵')"></span></th>
        <th @click="sortData('值')">值 <span :class="getArrowClass('值')"></span></th>
        <th @click="sortData('說明')">說明 <span :class="getArrowClass('說明')"></span></th>
        <th @click="sortData('created_at')">創建時間 <span :class="getArrowClass('created_at')"></span></th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="user in currentPageData" :key="user.id">
        <td>{{ user.簡稱 }}</td>
        <td>{{ user.音典分區 }}</td>
        <td>{{ user.經緯度 }}</td>
        <td>{{ user.特徵 }}</td>
        <td>{{ user.值 }}</td>
        <td>{{ user.說明 || '無' }}</td> <!-- 如果說明為 null 或 undefined，顯示 '無' -->
        <td>{{ formatTime(user.created_at)}}</td>
      </tr>
      </tbody>
    </table>
    <h3 v-else>🤷‍♂️<br>{{ username }} 無個人數據</h3>

    <!-- 分頁控制 -->
    <div class="pagination-controls">
      <button @click="prevPage" :disabled="currentPage === 1">上一頁</button>
      <span>頁面 {{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">下一頁</button>
    </div>
  </div>
</template>

<script>
import api from "../../axios.js";
import { formatTime } from "../../utils.js";

export default {
  data() {
    return {
      users: [],  // 用於存儲從 API 獲取的用戶數據
      searchQuery: '',  // 用於存儲搜索框的內容
      currentPage: 1,  // 当前页码
      pageSize: 30,  // 每页显示的记录数
      totalPages: 1,  // 总页数
      sortOrder: {  // 控制排序的对象
        簡稱: 'asc',
        音典分區: 'asc',
        經緯度: 'asc',
        特徵: 'asc',
        值: 'asc',
        說明: 'asc',
        created_at: 'asc',
      },
      sortField: '',  // 当前排序字段
      username: '',  // 当前的用户名
    };
  },
  async mounted() {
    const { username } = this.$route.query;  // 从路由参数中获取用户名
    const { created_at } = this.$route.query;  // 从路由查询参数中获取创建时间
    if (created_at) {
      this.searchQuery = created_at;  // 将创建时间填入搜索框
    }
    this.username = username;  // 设置当前的用户名
    try {
      const response = await api.get(`/custom/user?query=${username}`);
      this.users = response.data;
      this.totalPages = Math.ceil(this.users.length / this.pageSize);  // 计算总页数
    } catch (error) {
      console.error("API 请求错误:", error);
    }
  },
  computed: {
    // 当前页面的数据
    currentPageData() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      return this.filteredUsers.slice(startIndex, startIndex + this.pageSize);  // 根据当前页码和每页显示的数据数量筛选
    },

    // 过滤后的用户数据
    filteredUsers() {
      if (!this.searchQuery) {
        return this.users;
      }
      return this.users.filter(user => {
        const searchTerm = this.searchQuery.toLowerCase();
        return (
            (user.簡稱 && user.簡稱.toLowerCase().includes(searchTerm)) ||
            (user.音典分區 && user.音典分區.toLowerCase().includes(searchTerm)) ||
            (user.特徵 && user.特徵.toLowerCase().includes(searchTerm)) ||
            (user.值 && user.值.toLowerCase().includes(searchTerm)) ||
            (user.說明 && user.說明.toLowerCase().includes(searchTerm)) ||
            formatTime(user.created_at).toLowerCase().includes(searchTerm) // 搜索创建时间
        );
      });
    },
  },
  methods: {
    formatTime,
    // 获取箭头的 CSS 类
    getArrowClass(field) {
      return this.sortOrder[field] === 'asc' ? 'arrow-up' : 'arrow-down';
    },
    // 排序方法
    sortData(field) {
      const currentOrder = this.sortOrder[field] === 'asc' ? 'desc' : 'asc';
      this.sortOrder[field] = currentOrder;

      // 排序字段为时间的特殊处理
      if (field === 'created_at') {
        this.users.sort((a, b) => {
          const timeA = new Date(a.created_at).getTime();
          const timeB = new Date(b.created_at).getTime();
          return currentOrder === 'asc' ? timeA - timeB : timeB - timeA;
        });
      } else {
        this.users.sort((a, b) => {
          const valueA = a[field] || '';
          const valueB = b[field] || '';
          return currentOrder === 'asc' ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
        });
      }

      // 排序后重新计算分页
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

    goToCreateCustom(username) {
      this.$router.push({
        name: 'CreateCustom',
        query: { username: username }
      });
    },
    goToDeleteCustom(username) {
      this.$router.push({
        name: 'DeleteCustom',
        query: { username: username }
      });
    },
    goToEditCustom(username) {
      this.$router.push({
        name: 'EditCustom',
        query: { username: username }
      });
    }
  },
};
</script>

<style scoped>
/* 表格标题样式 */
h1 {
  font-size: 30px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 0;
  color: #2c6e49;  /* 苹果风格绿色 */
}

/* 显示数据总数的样式 */
p {
  font-size: 18px;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
  font-weight: normal;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  border-radius: 12px;
  overflow: hidden;
}

th,
td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: center;
  font-size: 16px;
}

th {
  background-color: #e4f4e7;  /* 浅绿色背景 */
  color: #2c6e49;  /* 绿色字体 */
  font-weight: bold;
  cursor: pointer;
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

/* 增加悬浮效果 */
th:hover {
  background-color: #c8e7c2;  /* 鼠标悬浮时的浅绿色 */
}

td {
  background-color: #f9f9f9;
}

/* 表格行悬停效果 */
tr:hover {
  background-color: #e1f5e1;  /* 鼠标悬浮时的浅绿色 */
}

/* 按钮的苹果绿色风格 */
button {
  margin-top: 10px;
  margin-left: 10px;
  margin-right: 10px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 25px; /* 圆角按钮 */
  background-color: #4CAF50;  /* 绿色 */
  color: white;
  border: none;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

button:hover {
  background-color: #45a049;  /* 深绿色 */
  transform: scale(1.05); /* 鼠标悬停时按钮稍微放大 */
}

button:disabled {
  background-color: rgba(76, 175, 80, 0.5);  /* 禁用按钮的背景颜色 */
  cursor: not-allowed; /* 禁用时的鼠标样式 */
}

/* 搜索框样式 */
.search-container input {
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 25px;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
  transition: all 0.3s ease-in-out;
}

.search-container input:focus {
  outline: none;
  border-color: #4CAF50;  /* 聚焦时的绿色边框 */
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);  /* 聚焦时的绿色阴影 */
  background-color: #eafaf0;  /* 聚焦时背景色变化 */
}

/* 分页控制 */
.pagination-controls {
  margin-top: 20px;
  text-align: center;
}

.pagination-controls button {
  padding: 12px 24px;
  margin: 0 10px;
  background-color: #4CAF50; /* 按钮的绿色 */
  color: white;
  border: none;
  border-radius: 20px; /* 圆角效果 */
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.pagination-controls button:hover {
  background-color: #45a049;
  transform: scale(1.05);
}

.pagination-controls button:disabled {
  background-color: rgba(76, 175, 80, 0.5);
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
</style>

