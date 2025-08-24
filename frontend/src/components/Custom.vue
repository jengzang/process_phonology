<template>
  <div>
    <h1>查詢結果</h1>

    <!-- 表格 -->
    <table>
      <thead>
      <tr>
        <th>用戶名</th>
        <th>簡稱</th>
        <th>音典分區</th>
        <th>經緯度</th>
        <th>特徵</th>
        <th>值</th>
        <th>說明</th>
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

export default {
  name: 'DataTable',
  setup() {
    const data = ref([]);  // 定義所有數據
    const currentPage = ref(1);  // 當前頁數
    const pageSize = 100;  // 每頁最多顯示 100 行
    const totalPages = computed(() => {
      return Math.ceil(data.value.length / pageSize);
    });
// 獲取數據
    const fetchData = async () => {
      try {
        const result = await api.get('/custom-query/all');  // 使用 await 等待異步請求結果
        data.value = result.data;  // 把結果賦值給反應式變量
        console.log(result.data)
      } catch (error) {
        console.error('Error:', error);  // 如果有錯誤，會在控制台打印
      }
    };

    // 當組件加載完成後，請求數據
    onMounted(() => {
      fetchData();
    });

    // 計算當前頁面顯示的數據
    const currentPageData = computed(() => {
      const startIndex = (currentPage.value - 1) * pageSize;
      const endIndex = startIndex + pageSize;
      return data.value.slice(startIndex, endIndex);
    });

    // 上一頁
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    // 下一頁
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    return {
      data,
      currentPage,
      totalPages,
      currentPageData,
      prevPage,
      nextPage,
    };
  },
};
</script>

<style scoped>
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
