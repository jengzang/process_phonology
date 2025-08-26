<template>
  <div>
    <h1>所有用戶數據</h1>
    <div class="top-controls">
      <p>當前共有 {{ data.length }} 條數據</p>
      <div class="logout-button-container" style="margin-top: 0">
        <button @click="goToHome" style="background:#9e9d24">返回首頁</button>
      </div>

      <!-- 搜索框 -->
      <div class="search-container">
        <input v-model="searchQuery" @input="searchUser" type="text" placeholder="搜索用戶名、簡稱、音典分區、特徵、值、說明" />
      </div>
    </div>
    <!-- 表格 -->
    <table>
      <thead>
      <tr>
        <th @click="sortData('username')">用戶名 <span :class="getArrowClass('username')"></span></th>
        <th @click="sortData('簡稱')" style="min-width: 70px">簡稱 <span :class="getArrowClass('簡稱')"></span></th>
        <th @click="sortData('音典分區')">音典分區 <span :class="getArrowClass('音典分區')"></span></th>
        <th @click="sortData('經緯度')">經緯度 <span :class="getArrowClass('經緯度')"></span></th>
        <th @click="sortData('特徵')">特徵 <span :class="getArrowClass('特徵')"></span></th>
        <th @click="sortData('值')">值 <span :class="getArrowClass('值')"></span></th>
        <th @click="sortData('說明')" style="min-width: 120px">說明 <span :class="getArrowClass('說明')"></span></th>
        <th @click="sortData('time')">創建時間 <span :class="getArrowClass('time')"></span></th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="item in currentPageData" :key="item.id" @click="goToPerUser(item)">
        <td>{{ item.username }}</td>
        <td>{{ item.簡稱 }}</td>
        <td>{{ item.音典分區 }}</td>
        <td>{{ item.經緯度 }}</td>
        <td>{{ item.特徵 }}</td>
        <td>{{ item.值 }}</td>
        <td>{{ item.說明 }}</td>
        <td>{{ formatTime(item.created_at) }}</td>
      </tr>
      </tbody>
    </table>

    <!-- 分頁控制 -->
    <div class="pagination-controls">
      <button @click="prevPage" :disabled="currentPage === 1">上一頁</button>
      <span>頁面 {{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">下一頁</button>
    </div>
  </div>
</template>


<script>
import { ref, onMounted, computed } from 'vue';
import api from '../../axios.js'; // 引入API请求配置
import { formatTime } from "../../utils.js";  // 假设你有一个 utils.js 用来处理时间格式化

export default {
  name: 'DataTable',
  setup() {
    const data = ref([]);  // 定义所有数据
    const currentPage = ref(1);  // 当前页码
    const searchQuery = ref('');  // 用于绑定搜索框内容
    const pageSize = 50;  // 每页最多显示 50 行
    const totalPages = computed(() => {
      return Math.ceil(data.value.length / pageSize);
    });

    // 排序状态
    const sortField = ref(''); // 当前排序字段
    const sortOrder = ref('asc'); // 当前排序顺序（升序/降序）

    // 获取数据
    const fetchData = async () => {
      try {
        const result = await api.get('/custom/all');  // 使用 await 等待异步请求结果
        data.value = result.data;  // 把结果赋值给反应式变量
      } catch (error) {
        console.error('Error:', error);  // 如果有错误，会在控制台打印
      }
    };

    // 当组件加载完成后，请求数据
    onMounted(() => {
      fetchData();
    });

    // 计算当前页面显示的数据
    const currentPageData = computed(() => {
      let filteredData = data.value;

      // 过滤数据
      if (searchQuery.value) {
        filteredData = filteredData.filter(item => {
          const formattedTime = formatTime(item.created_at);  // 获取格式化后的时间
          return (
              (item.username && item.username.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
              (item.簡稱 && item.簡稱.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
              (item.音典分區 && item.音典分區.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
              (item.特徵 && item.特徵.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
              (item.值 && item.值.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
              (item.說明 && item.說明.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
              formattedTime.includes(searchQuery.value)  // 比较用户输入的日期
          );
        });
      }

      // 排序数据
      let sortedData = [...filteredData];
      if (sortField.value) {
        sortedData.sort((a, b) => {
          const valA = a[sortField.value] || '';
          const valB = b[sortField.value] || '';

          if (sortOrder.value === 'asc') {
            return valA < valB ? -1 : valA > valB ? 1 : 0;
          } else {
            return valA > valB ? -1 : valA < valB ? 1 : 0;
          }
        });
      }

      // 根据当前页码计算当前页数据
      const startIndex = (currentPage.value - 1) * pageSize;
      return sortedData.slice(startIndex, startIndex + pageSize);
    });

    // 上一页
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    // 下一页
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    // 排序方法
    const sortData = (field) => {
      if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortField.value = field;
        sortOrder.value = 'asc';
      }
    };

    // 获取排序的箭头图标
    const getArrowClass = (field) => {
      return sortField.value === field ? (sortOrder.value === 'asc' ? 'arrow-up' : 'arrow-down') : '';
    };

    return {
      data,
      currentPage,
      searchQuery,
      totalPages,
      currentPageData,
      prevPage,
      nextPage,
      sortData,
      getArrowClass,
      formatTime,
    };
  },
  methods:{
    goToPerUser(user) {
      const formattedTime = this.formatTime(user.created_at);  // 格式化创建时间
      this.$router.push({
        name: 'PerUser',
        query: {
          username: user.username,
          created_at: formattedTime,  // 将创建时间传递给目标页面
        }
      });
    },
    goToHome(){
      this.$router.push({name: 'Home'});
    },
  }
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
  white-space: nowrap;
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
  max-width: 120px;
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

/* 表格行悬停效果 */
tr:hover {
  background-color: #e1f5e1;  /* 鼠标悬浮时的浅绿色背景 */
  cursor: pointer;  /* 鼠标悬浮时变为手形 */
  transition: background-color 0.3s ease;  /* 平滑过渡效果 */
}

/* 可选：表格头部悬停效果 */
th:hover {
  background-color: #c8e7c2;  /* 鼠标悬浮时的背景色变化 */
}

/* 移動端適配 */
@media (max-width: 768px) {
  th, td {
    padding: 8px; /* 減少表格單元格的內邊距 */
  }

  .stat-btn {
    font-size: 14px; /* 調整按鈕文字大小 */
    padding: 12px; /* 增加按鈕的內邊距 */
  }

  .modal-content {
    width: 95%; /* 彈窗的寬度更小，適應小屏幕 */
  }

  .pagination-controls button {
    font-size: 14px; /* 分頁按鈕文字大小調整 */
    min-width: 100px; /* 調整分頁按鈕最小寬度 */
  }

  table {
    font-size: 14px;  /* 更小的字体 */
    overflow-x: auto;
    display: block;  /* 使表格可滚动 */
  }

  th, td {
    padding: 8px 12px;
  }
}

/* 更小的屏幕適配（如手機） */
@media (max-width: 480px) {
  table {
    font-size: 14px; /* 調整表格字體大小 */
  }

  .pagination-controls button {
    font-size: 12px; /* 調整分頁按鈕字體大小 */
    padding: 8px 16px; /* 調整按鈕的內邊距 */
  }

  .stat-btn {
    font-size: 12px; /* 調整按鈕文字大小 */
    padding: 10px; /* 調整按鈕內邊距 */
  }

  .close {
    font-size: 50px; /* 關閉按鈕大小調整 */
  }

  .modal-content {
    padding: 15px; /* 彈窗內邊距調整 */
  }
  table {
    font-size: 12px; /* 更小的字体 */
  }
}

</style>


