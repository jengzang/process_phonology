<template>
  <div>
    <h2>近期 API 使用詳情</h2>

    <button @click="goToApiStatsPage" style="max-width: 100px;padding:0;">API統計圖表</button>

    <!-- 功能统计部分 -->
    <div class="stats">
      <button @click="showUniqueUsers" class="stat-btn">所有用户: {{ uniqueUsersCount }}</button>
      <button @click="showUniqueIPs" class="stat-btn">所有IP: {{ uniqueIPsCount }}</button>
      <button @click="showAPICalls" class="stat-btn" style="max-width: 180px">API調用數: {{ totalAPICalls }}</button>
      <button @click="goToHome" class="stat-btn" style="background: darkgoldenrod;">返回首頁</button>
    </div>

    <!-- 独特用户弹窗 -->
    <div v-if="showUserModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeUserModal">&times;</span>
        <h3>用户列表</h3>
        <table>
          <thead>
          <tr>
            <th>用戶名</th>
            <th>總使用時長</th>
            <th>次數</th>
          </tr>
          </thead>
          <tbody>
          <tr
              v-for="userStat in userStats"
              :key="userStat.user"
              :class="{ 'clickable': userStat.user !== '匿名用戶' }"
              @click="userStat.user !== '匿名用戶' && viewUserStats(userStat.user)"
          >
            <td>{{ userStat.user }}</td>  <!-- 显示用户名 -->
            <td>{{ userStat.totalDuration.toFixed(3) }}s</td> <!-- 总使用时长 -->
            <td>{{ userStat.occurrenceCount }}</td> <!-- 出现次数 -->
          </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="showUserModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeUserModal">&times;</span>
        <h3>用户列表</h3>
        <table>
          <thead>
          <tr>
            <th>用戶名</th>
            <th>總使用時長</th>
            <th>次數</th>
            <th>上行流量</th>  <!-- 新增列 -->
            <th>下行流量</th>  <!-- 新增列 -->
          </tr>
          </thead>
          <tbody>
          <tr
              v-for="userStat in userStats"
              :key="userStat.user"
              :class="{ 'clickable': userStat.user !== '匿名用戶' }"
              @click="userStat.user !== '匿名用戶' && viewUserStats(userStat.user)"
          >
            <td>{{ userStat.user }}</td>  <!-- 显示用户名 -->
            <td>{{ userStat.totalDuration.toFixed(3) }}s</td> <!-- 总使用时长 -->
            <td>{{ userStat.occurrenceCount }}</td> <!-- 出现次数 -->
            <td>{{ userStat.totalUploadTraffic }}KB</td>  <!-- 上行流量 -->
            <td>{{ userStat.totalDownloadTraffic }}MB</td>  <!-- 下行流量 -->
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 独特IP弹窗 -->
    <div v-if="showIPModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeIPModal">&times;</span>
        <h3>所有IP地址</h3>
        <table>
          <thead>
          <tr>
            <th>IP 地址</th>
            <th>總使用時長</th>
            <th>次數</th>
            <th>上行流量</th>  <!-- 新增列 -->
            <th>下行流量</th>  <!-- 新增列 -->
          </tr>
          </thead>
          <tbody>
          <tr v-for="ipStat in ipStats" :key="ipStat.ip">
            <td>{{ ipStat.ip }}</td>
            <td>{{ ipStat.totalDuration.toFixed(3) }}s</td> <!-- 总使用时长 -->
            <td>{{ ipStat.occurrenceCount }}</td> <!-- 出现次数 -->
            <td>{{ ipStat.totalUploadTraffic }}KB</td>  <!-- 上行流量 -->
            <td>{{ ipStat.totalDownloadTraffic }}MB</td>  <!-- 下行流量 -->
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- API调用统计弹窗 -->
    <div v-if="showAPICallsModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeAPICallsModal">&times;</span>
        <h3>各個API調用次數</h3>
        <table>
          <thead>
          <tr>
            <th>API 路徑</th>
            <th>總時長</th>  <!-- 新增总持续时间列 -->
            <th>調用次數</th>
            <th>上行流量</th>  <!-- 新增列 -->
            <th>下行流量</th>  <!-- 新增列 -->
          </tr>
          </thead>
          <tbody>
          <tr v-for="(data, path) in apiCalls" :key="path">
            <td>{{ path }}</td>
            <td>{{ data.totalDuration.toFixed(3) }}s</td>  <!-- 显示总持续时间 -->
            <td>{{ data.count }}</td>
            <td>{{ data.totalUploadTraffic.toFixed(2) }}KB</td>  <!-- 上行流量 -->
            <td>{{ data.totalDownloadTraffic.toFixed(2) }}MB</td>  <!-- 下行流量 -->
          </tr>
          </tbody>
        </table>
      </div>
    </div>


    <!--    詳細表格-->
    <table>
      <thead>
      <tr>
        <th @click="sortData('user')">用戶 <span :class="getArrowClass('user')"></span></th>
        <th @click="sortData('ip')">IP 地址 <span :class="getArrowClass('ip')"></span></th>
        <th @click="sortData('path')">API 路徑 <span :class="getArrowClass('path')"></span></th>
        <th @click="sortData('duration')">持續時長 <span :class="getArrowClass('duration')"></span></th>
        <th @click="sortData('os')">操作系統 <span :class="getArrowClass('os')"></span></th>
        <th @click="sortData('browser')">瀏覽器 <span :class="getArrowClass('browser')"></span></th>
        <th @click="sortData('called_at')">請求時間 <span :class="getArrowClass('called_at')"></span></th>
        <th @click="sortData('uploadTraffic')">上行流量 <span :class="getArrowClass('uploadTraffic')"></span></th>
        <th @click="sortData('downloadTraffic')">下行流量 <span :class="getArrowClass('downloadTraffic')"></span></th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(log, index) in currentPageData" :key="index">
        <td>{{ log.user || '' }}</td> <!-- 用户 -->
        <td>{{ log.ip }}</td>
        <td>{{ log.path }}</td>
        <td>{{ log.duration.toFixed(3) }}s</td>  <!-- 持续时长 -->
        <td>{{ log.os }}</td> <!-- 操作系统 -->
        <td>{{ log.browser }}</td> <!-- 浏览器 -->
        <td>{{ formatTime(log.called_at) }}</td> <!-- 使用时间 -->
        <td>{{ log.uploadTraffic }}KB</td>  <!-- 上行流量 -->
        <td>{{ log.downloadTraffic }}KB</td>  <!-- 下行流量 -->
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
import api from '../../axios.js'; // 引入API请求配置
import {formatTime} from "../../utils.js";

export default {
  data() {
    return {
      currentPage: 1,  // 当前页码
      pageSize: 50,   // 每页显示的记录数
      totalPages: 1,  // 总页数
      userName: '',  // 用户名
      apiLogs: [],   // 用于存储用户的 API 使用记录
      uniqueUsers: [],  // 存储独特用户列表
      uniqueIPs: [],  // 存储独特IP地址列表
      apiCalls: {},   // 存储各个API调用次数
      totalAPICalls: 0, // 总的API调用次数
      showUserModal: false, // 控制独特用户弹窗
      showIPModal: false, // 控制独特IP弹窗
      showAPICallsModal: false, // 控制API调用统计弹窗
      uniqueUsersCount: 0,  // 独特用户数
      uniqueIPsCount: 0,    // 独特IP地址数
      sortOrder: {  // 控制排序的对象
        user: 'asc',
        totalDuration: 'desc',
        occurrenceCount: 'desc',
        ip: 'asc',
        path: 'asc',
        duration: 'desc',
        os: 'asc',
        browser: 'asc',
        called_at: 'desc',
      },
      sortField: '',  // 当前排序字段
    };
  },
  async mounted() {
    try {
      const response = await api.get(`/api-usage/api-usage`, {
        params: { page: this.currentPage, limit: this.pageSize } // 添加分页参数
      });
      this.apiLogs = response.data;  // 处理返回的 API 使用记录
      console.log(this.apiLogs)
      // 为每个日志添加上行流量和下行流量，假设 log.request_size 和 log.response_size 存在
      this.apiLogs = this.apiLogs.map(log => ({
        ...log,
        uploadTraffic: (log.request_size / 1024).toFixed(2),  // 转换为 KB，保留两位小数
        downloadTraffic: (log.response_size / 1024).toFixed(2) // 转换为 KB，保留两位小数
      }));

      // 独特用户统计
      this.uniqueUsers = [...new Set(this.apiLogs.map(log => log.user || ''))];
      this.uniqueUsersCount = this.uniqueUsers.length;

      this.userStats = this.uniqueUsers.map(user => {
        const userLogs = this.apiLogs.filter(log => log.user === user);
        const totalDuration = userLogs.reduce((acc, log) => acc + log.duration, 0);
        const occurrenceCount = userLogs.length;
        const totalUploadTraffic = userLogs.reduce((acc, log) => acc + (log.request_size || 0), 0);  // 上行流量
        const totalDownloadTraffic = userLogs.reduce((acc, log) => acc + (log.response_size || 0), 0);  // 下行流量
        return {
          user: user || '匿名用户',
          totalDuration,
          occurrenceCount,
          totalUploadTraffic: (totalUploadTraffic / (1024)).toFixed(2),  // 转换为 MB
          totalDownloadTraffic: (totalDownloadTraffic / (1024 * 1024)).toFixed(2)  // 转换为 MB
        };
      });

      // 排序：按总使用时长从大到小
      this.userStats.sort((a, b) => b.totalDuration - a.totalDuration);

      // 独特 IP 地址统计
      this.uniqueIPs = [...new Set(this.apiLogs.map(log => log.ip))];
      this.uniqueIPsCount = this.uniqueIPs.length;

      this.ipStats = this.uniqueIPs.map(ip => {
        const ipLogs = this.apiLogs.filter(log => log.ip === ip);
        const totalDuration = ipLogs.reduce((acc, log) => acc + log.duration, 0);
        const occurrenceCount = ipLogs.length;
        const totalUploadTraffic = ipLogs.reduce((acc, log) => acc + (log.request_size || 0), 0);  // 上行流量
        const totalDownloadTraffic = ipLogs.reduce((acc, log) => acc + (log.response_size || 0), 0);  // 下行流量
        return {
          ip,
          totalDuration,
          occurrenceCount,
          totalUploadTraffic: (totalUploadTraffic / (1024)).toFixed(2),  // 转换为 MB
          totalDownloadTraffic: (totalDownloadTraffic / (1024 * 1024)).toFixed(2)  // 转换为 MB

        };
      });

      // 排序：按总使用时长从大到小
      this.ipStats.sort((a, b) => b.totalDuration - a.totalDuration);

      this.apiCalls = this.apiLogs.reduce((acc, log) => {
        if (!acc[log.path]) {
          acc[log.path] = { count: 0, totalDuration: 0, totalUploadTraffic: 0, totalDownloadTraffic: 0 };
        }
        acc[log.path].count += 1;
        acc[log.path].totalDuration += log.duration;

        // 转换上行流量和下行流量为 MB，计算时保持数字类型，最后格式化为两位小数
        acc[log.path].totalUploadTraffic += ((log.request_size / (1024))) || 0;  // 转换为 MB，保持数字
        acc[log.path].totalDownloadTraffic += ((log.response_size / (1024 * 1024))) || 0;  // 转换为 MB，保持数字




        this.totalAPICalls += 1;
        return acc;
      }, {});

      // 总页数的计算
      this.totalPages = Math.ceil(this.totalAPICalls / this.pageSize);

      // 排序数据
      this.sortData();  // 初始化时排序所有数据

    } catch (error) {
      console.error('Error fetching API usage data', error);
    }
  },

  computed: {
// 当前页面的数据
    currentPageData() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      return this.apiLogs.slice(startIndex, startIndex + this.pageSize);  // 根据当前页码和每页显示的数据数量筛选
    },
  },
  methods: {
    formatTime,
    // 跳转到图表页面
    goToApiStatsPage() {
      this.$router.push({name: 'ApiChart'});
    },
    // 获取箭头的 CSS 类
    getArrowClass(field) {
      return this.sortOrder[field] === 'asc' ? 'arrow-up' : 'arrow-down';
    },
    // 排序方法
    sortData(field) {
      const currentOrder = this.sortOrder[field] === 'asc' ? 'desc' : 'asc';
      this.sortOrder[field] = currentOrder;

      // 排序字段为时间的特殊处理
      if (field === 'called_at') {
        // 处理时间字段排序
        this.apiLogs.sort((a, b) => {
          const timeA = new Date(a.called_at).getTime();
          const timeB = new Date(b.called_at).getTime();
          return currentOrder === 'asc' ? timeA - timeB : timeB - timeA;
        });
      } else if (field === 'user' || field === 'ip' || field === 'path' || field === 'os' || field === 'browser') {
        // 字符串字段排序
        this.apiLogs.sort((a, b) => {
          const valueA = a[field] || '';
          const valueB = b[field] || '';
          if (currentOrder === 'asc') {
            return valueA.localeCompare(valueB);
          } else {
            return valueB.localeCompare(valueA);
          }
        });
      } else {
        // 数字字段排序
        this.apiLogs.sort((a, b) => {
          if (currentOrder === 'asc') {
            return a[field] - b[field];
          } else {
            return b[field] - a[field];
          }
        });
      }

      // 排序之后重新计算分页
      this.totalPages = Math.ceil(this.apiLogs.length / this.pageSize);
      this.currentPage = 1;  // 重置当前页为第一页
    },

    // 上一页
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchPageData();
      }
    },

    // 下一页
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchPageData();
      }
    },

    // 更新当前页数据
    fetchPageData() {
      this.totalPages = Math.ceil(this.apiLogs.length / this.pageSize);  // 重新计算总页数
    },
    // 弹出独特用户的表格
    showUniqueUsers() {
      this.showUserModal = true;
    },
    closeUserModal() {
      this.showUserModal = false;
    },

    // 弹出独特IP地址的表格
    showUniqueIPs() {
      this.showIPModal = true;
    },
    closeIPModal() {
      this.showIPModal = false;
    },

    // 弹出各个API调用次数的统计表格
    showAPICalls() {
      this.showAPICallsModal = true;
    },
    closeAPICallsModal() {
      this.showAPICallsModal = false;
    },
    async viewUserStats(username) {
      this.$router.push({name: 'UserStats', query: {username: username}});
    },
    goToHome(){
      this.$router.push({name: 'Home'});
    },
  }
};
</script>

<style scoped>
/* 按鈕樣式調整 */
button {
  max-width: 100%; /* 使按鈕適應屏幕寬度 */
  box-sizing: border-box; /* 讓按鈕寬度包含內邊距 */
}

.stat-btn {
  padding: 10px;
  margin: 10px;
  cursor: pointer;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 17px;
  max-width: 120px;
  width: 100%; /* 在移動端讓按鈕寬度適應 */
}

/* 按鈕懸停效果 */
.stat-btn:hover {
  background-color: #45a049;
}

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
  text-align: left;
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


/* 彈窗樣式優化 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  width: 90%; /* 使彈窗寬度適應小屏 */
  max-width: 500px; /* 限制彈窗最大寬度 */
  max-height: 80%;
  overflow-y: auto;
}

.close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 60px;
  cursor: pointer;
}

.close:hover {
  color: red;
}


/* 分頁控制樣式調整 */
.pagination-controls {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  flex-wrap: wrap; /* 允許分頁按鈕在移動端換行 */
}

.pagination-controls button {
  padding: 10px 20px;
  margin: 5px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px; /* 分頁按鈕設置最小寬度 */
  box-sizing: border-box;
}

.pagination-controls button:hover {
  background-color: #45a049;
  transform: scale(1.05);
}

.pagination-controls button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.pagination-controls span {
  font-size: 16px;
  align-self: center;
  color: #333;
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
