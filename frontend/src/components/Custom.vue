<template>
  <div>
    <h1>所有用戶數據</h1>

    <p>當前共有 {{ data.length }} 條數據</p>
    <!-- 表格 -->
    <table>
      <thead>
      <tr>
        <th @click="sortData('username')">用戶名 <span :class="getArrowClass('username')"></span></th>
        <th @click="sortData('簡稱')">簡稱 <span :class="getArrowClass('簡稱')"></span></th>
        <th @click="sortData('音典分區')">音典分區 <span :class="getArrowClass('音典分區')"></span></th>
        <th @click="sortData('經緯度')">經緯度 <span :class="getArrowClass('經緯度')"></span></th>
        <th @click="sortData('特徵')">特徵 <span :class="getArrowClass('特徵')"></span></th>
        <th @click="sortData('值')">值 <span :class="getArrowClass('值')"></span></th>
        <th @click="sortData('說明')">說明 <span :class="getArrowClass('說明')"></span></th>
        <th @click="sortData('time')">創建時間 <span :class="getArrowClass('time')"></span></th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="item in currentPageData" :key="item.id">
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
import api from '../axios'; // 引入API请求配置
import { formatTime } from "../utils.js";  // 假设你有一个 utils.js 用来处理时间格式化

export default {
  name: 'DataTable',
  setup() {
    const data = ref([]);  // 定义所有数据
    const currentPage = ref(1);  // 当前页码
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
        const result = await api.get('/custom-query/all');  // 使用 await 等待异步请求结果
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
      // 排序数据
      let sortedData = [...data.value];
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
      totalPages,
      currentPageData,
      prevPage,
      nextPage,
      sortData,
      getArrowClass,
      formatTime,
    };
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
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

th {
  background-color: #f2f2f2;
  cursor: pointer;
  position: relative;
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
  background-color: #e0e0e0;
}

.pagination-controls {
  margin-top: 20px;
  text-align: center;
}

.pagination-controls button {
  padding: 8px 16px;
  margin: 0 10px;
}

.pagination-controls span {
  font-size: 16px;
}
</style>


