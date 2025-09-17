<template>
  <div class="stats-container">
    <h2>用戶統計</h2>
    <div class="user-info">
      <h3>{{ username }} 的統計信息</h3>
    </div>
    <div class="stats-card">
      <div><strong>登錄次數:</strong> {{ stats.login_count }}</div>
      <div><strong>登錄失敗次數:</strong> {{ stats.failed_attempts }}</div>
      <div><strong>註冊IP:</strong> {{ stats.register_ip }}</div>
      <div><strong>總在線時長:</strong> {{ formatOnlineTime(stats.total_online_seconds) }}</div>
      <div><strong>最近一次登錄:</strong> {{ formatTime(stats.last_login) }}</div>
    </div>
    <div class="logout-button-container">
      <button @click="goToHome" >返回首頁</button>
    </div>

    <h2>近期登錄</h2>
    <div class="table-wrapper">
      <table class="dynamic-table">
        <thead>
        <tr>
          <th>IP地址</th>
          <th>次數</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(count, ip) in ipCounts" :key="ip">
          <td>{{ ip }}</td>
          <td>{{ count }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <h2>API 使用統計</h2>
    <table>
      <thead>
      <tr>
        <th>API 路徑</th>
        <th>使用次數</th>
        <th>上次使用時間</th>
        <th>總使用時長</th>
        <th>總上行流量</th>
        <th>總下行流量</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="log in filteredApiUsage" :key="log.id">
        <td>{{ log.path }}</td>
        <td>{{ log.count }}</td>
        <td>{{ formatTime(log.last_updated) }}</td>
        <td>{{ (log.total_duration || 0).toFixed(2) }} 秒</td>
        <td>{{ (log.total_upload || 0).toFixed(2) }} KB</td>
        <td>{{ ((log.total_download || 0) / 1024).toFixed(2) }} MB</td>
      </tr>
      </tbody>
    </table>

    <h2>近期 API 使用詳情</h2>
    <table>
      <thead>
      <tr>
        <th>IP 地址</th>
        <th>API 路徑</th>
        <th>持續時長(秒)</th>
<!--        <th>設備</th>-->
        <th>操作系統</th>
        <th>瀏覽器</th>
        <th>發起時間</th>
        <th>上行流量</th>
        <th>下行流量</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="log in apiLogs" :key="log.id">
        <td>{{ log.ip }}</td>
        <td>{{ log.path }}</td>
        <td>{{ log.duration.toFixed(3) }}s</td>  <!-- 保留三位小数 -->
        <td>
          <div class="browser-cell" @mouseover="showUserAgent($event,log)" @mouseleave="hideUserAgent(log)">
            <span>{{ log.os }}</span>
            <div v-show="log.showUserAgent" class="user-agent-tooltip">
              {{ log.user_agent }}
            </div>
          </div>
        </td>   <!-- 操作系统 -->
        <td>{{ log.browser }}</td><!-- 浏览器 -->
        <td>{{ formatTime(log.called_at) }}</td>  <!-- 北京时间 -->
        <!-- 新增的上行流量 -->
        <td>{{ log.uploadTraffic }}KB</td>
        <!-- 新增的下行流量 -->
        <td>{{ log.downloadTraffic }}KB</td>
      </tr>
      </tbody>
    </table>

  </div>
</template>

<script>
import api from '../../axios.js';  // 引入我們的全局 axios 配置
import {formatTime} from "../../utils.js";

export default {
  data() {
    return {
      stats: {},
      username: '',
      filteredApiUsage: [],  // API 使用統計
      loginHistory: [],
      ipCounts: {} , // 用於存儲按 IP 地址分組後的次數統計
      apiLogs:{},
    };
  },
  async mounted() {
    const { username } = this.$route.query;  // 從路由參數中獲取用戶名
    this.username = username;  // 設置當前的用戶名
    try {
      // 獲取用戶統計數據
      const statsResponse = await api.get(`/stats/stats?query=${username}`);
      this.stats = statsResponse.data;

      // 獲取API使用統計數據
      const apiUsageResponse = await api.get(`/api-usage/api-summary?query=${username}`);
      // console.log(apiUsageResponse.data);
      this.apiUsage = apiUsageResponse.data;
      this.filteredApiUsage = this.apiUsage.filter(log => !log.path.includes('/login'));

      const response = await api.get(`/login-logs/success-login-logs?query=${username}`);
      this.loginHistory = response.data;
      this.processIpCounts();  // 處理 IP 地址及其對應的次數

      const response2 = await api.get(`/api-usage/api-detail?query=${username}`);  // 请求后端接口获取 API 使用情况
      this.userName = response2.data.user;

      this.apiLogs = response2.data.api_logs.map(log => ({
        ...log,
        // 提取操作系统和浏览器信息
        ...this.getDeviceInfo(log.user_agent),
        showUserAgent: false,  // 初始时不显示 User Agent
        // 假设 log.request_size 是上行流量，log.response_size 是下行流量
        uploadTraffic: log.request_size ? (log.request_size / 1024).toFixed(2) : '0.00',  // 转换为 KB
        downloadTraffic: log.response_size ? (log.response_size /  1024).toFixed(2) : '0.00',  // 转换为 KB
      }));

      // 初始化按 API 路径分组的对象
      // const apiStats = {};
      // 按 path 分组并累加每个 API 的统计数据
      // response2.data.api_logs.forEach(log => {
      //   const duration = log.duration ? parseFloat(log.duration) : 0;
      //   const uploadTraffic = log.request_size ? (log.request_size / 1024) : 0;  // 转换为 KB
      //   const downloadTraffic = log.response_size ? (log.response_size / 1024) : 0;  // 转换为 KB
      //
      //   const path = log.path;
      //
      //   // 如果该 API 路径没有记录，就初始化它
      //   if (!apiStats[path]) {
      //     apiStats[path] = {
      //       path: path,
      //       totalDuration: 0,
      //       totalUploadTraffic: 0,
      //       totalDownloadTraffic: 0,
      //       count: 0,
      //     };
      //   }
      //
      //   // 累加该 API 的数据
      //   apiStats[path].totalDuration += duration;
      //   apiStats[path].totalUploadTraffic += uploadTraffic;
      //   apiStats[path].totalDownloadTraffic += downloadTraffic;
      //   apiStats[path].count += 1;
      // });

      // // 将累加后的数据添加到 filteredApiUsage 中
      // this.filteredApiUsage.forEach(api => {
      //   const stats = apiStats[api.path] || {
      //     // path: api.path,
      //     totalDuration: 0,
      //     totalUploadTraffic: 0,
      //     totalDownloadTraffic: 0,
      //     // count: 0,
      //   };
      //
      //   // 将累加的统计信息直接添加到 filteredApiUsage 中
      //   api.totalDuration = stats.totalDuration;
      //   api.totalUploadTraffic = stats.totalUploadTraffic;
      //   api.totalDownloadTraffic = stats.totalDownloadTraffic;
      //   // api.count = stats.count;
      // });


    } catch (error) {
      console.error('Error fetching stats and API usage', error);
    }
  },
  methods: {
    formatTime,
    // 將秒數轉換為小時和分鐘格式
    formatOnlineTime(seconds) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}小時 ${minutes}分鐘`;
    },

    processIpCounts() {
      const counts = {};
      this.loginHistory.forEach(log => {
        if (counts[log.ip]) {
          counts[log.ip] += 1;  // 如果 IP 已經出現過，次數加 1
        } else {
          counts[log.ip] = 1;  // 否則初始化次數為 1
        }
      });
      this.ipCounts = counts;  // 更新統計結果
    },
    // 提取操作系统和浏览器信息
    getDeviceInfo(userAgent) {
      let os = "Unknown OS";
      let browser = "Unknown Browser";

      // 操作系统提取
      if (/iPhone|iPad|iPod/.test(userAgent)) {
        os = "iOS";
      } else if (/Android/.test(userAgent)) {
        os = "Android";
      } else if (/Windows/.test(userAgent)) {
        os = "Windows";
      } else if (/Macintosh/.test(userAgent)) {
        os = "Mac OS";
      } else if (/Linux/.test(userAgent)) {
        os = "Linux";
      }

      // 浏览器提取
      if (/Chrome/.test(userAgent)) {
        browser = "Chrome";
      } else if (/Firefox/.test(userAgent)) {
        browser = "Firefox";
      } else if (/Safari/.test(userAgent)) {
        browser = "Safari";
      } else if (/Edge/.test(userAgent)) {
        browser = "Edge";
      }

      return { os, browser };
    },

// 显示原始 User Agent并根据鼠标位置调整 top 和 left
    showUserAgent(event, log) {
      log.showUserAgent = true;

      // 获取鼠标位置
      const rect = event.currentTarget.getBoundingClientRect(); // 获取单元格位置

      // 动态设置工具提示的 top 和 left 位置
      this.tooltipStyle = {
        position: 'fixed',
        top: `${event.clientY + 10}px`,  // 鼠标 Y 坐标加上偏移量 10px
        left: `${rect.left + window.scrollX}px`,  // 获取单元格的 left 位置
        zIndex: 1000
      };
    },

    // 隐藏原始 User Agent
    hideUserAgent(log) {
      log.showUserAgent = false;
    },
    goToHome(){
      this.$router.push({name: 'Home'});
    },
  }
};
</script>

<style scoped>
/* 設置整體容器 */
.stats-container {
  margin: 20px;
  font-family: Arial, sans-serif;
  padding: 10px;
}


.user-info {
  margin-bottom: 20px;
}

h3 {
  color: #333;
}

.stats-card {
  background: #f5f8f1;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  font-size: 16px;
  margin-bottom: 20px;
}

.stats-card div {
  margin-bottom: 10px;
}

strong {
  color: #007bff;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: #f1f8e9; /* 苹果绿色背景 */
  border: 1px solid #81c784; /* 苹果绿色边框 */
  border-radius: 8px;
  overflow: hidden; /* 避免圆角被覆盖 */
}

th, td {
  padding: 10px;
  text-align: center; /* 表格内容居中 */
  border-top: 1px solid #81c784; /* 苹果绿色边框 */
  word-wrap: break-word; /* 自动换行 */
  max-width: 200px; /* 设置最大宽度 */
  overflow: hidden; /* 超出内容隐藏 */
  text-overflow: ellipsis; /* 文字溢出时显示省略号 */
}

th {
  background-color: #a5d6a7; /* 更深的绿色作为表头背景 */
  color: #fff;
  white-space: nowrap; /* 防止标题文字换行 */
}

.browser-cell {
  position: relative;
}

.user-agent-tooltip {
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 10px;
  border-radius: 5px;
  width: 250px;
  max-height: 150px;
  overflow-y: auto;
  display: none;
  z-index: 1000;
}

/* 当鼠标悬停时，显示工具提示并使其脱离表格的限制 */
.browser-cell:hover .user-agent-tooltip {
  display: block;
  position: fixed;  /* 使工具提示固定在视口 */
  top: 10px;        /* 你可以调整这里的位置 */
  left: 10px;       /* 你可以调整这里的位置 */
  z-index: 1000;    /* 让工具提示层级更高，避免被其他内容覆盖 */
}

.table-wrapper {
  width: 100%;
  text-align: center;     /* 子元素居中 */
  overflow-x: auto;       /* 超宽时横向滚动 */
  border-radius: 8px;
}

.dynamic-table {
  display: inline-table;  /* 🔥 重点：用 inline-table 而不是 width: 100% */
  border-collapse: collapse;
  margin: 0 auto;         /* 保险起见，也居中处理 */
  background-color: #f1f8e9;
  border: 1px solid #81c784;
  border-radius: 8px;
  text-align: center;
}

/* 其他原有样式保持 */
.dynamic-table th, .dynamic-table td {
  padding: 10px;
  text-align: center;
  border-top: 1px solid #81c784;
  word-wrap: break-word;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dynamic-table th {
  background-color: #a5d6a7;
  color: #fff;
}


/* 移动端适配 */
@media (max-width: 768px) {
  .stats-container {
    margin: 10px;
    padding: 5px;
  }

  button {
    padding: 10px 20px;
    font-size: 14px;
    min-width: 100px; /* 在小屏幕上减少按钮宽度 */
  }

  .stats-card {
    padding: 15px;
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

@media (max-width: 480px) {
  button {
    padding: 8px 16px;
    font-size: 12px; /* 更小的字体 */
  }

  .stats-card {
    padding: 10px;
  }

  table {
    font-size: 12px; /* 更小的字体 */
  }
}


</style>


