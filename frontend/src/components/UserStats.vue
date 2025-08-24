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

    <h2>登錄歷史</h2>
    <table>
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

    <h2>API 使用統計</h2>
    <table>
      <thead>
      <tr>
        <th>API 路徑</th>
        <th>使用次數</th>
        <th>上次使用時間</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="log in filteredApiUsage" :key="log.id">
        <td>{{ log.path }}</td>
        <td>{{ log.count }}</td>
        <td>{{ formatTime(log.last_updated) }}</td>
      </tr>
      </tbody>
    </table>

    <h2>近期 API 使用詳情</h2>
    <table>
      <thead>
      <tr>
        <th>IP 地址</th>
        <th>持續時長(秒)</th>
<!--        <th>設備</th>-->
        <th>操作系統</th>
        <th>瀏覽器</th>
        <th>發起時間</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="log in apiLogs" :key="log.id">
        <td>{{ log.ip }}</td>
        <td>{{ log.duration.toFixed(3) }}s</td>  <!-- 保留三位小数 -->
        <td>
          <div class="browser-cell" @mouseover="showUserAgent(log)" @mouseleave="hideUserAgent(log)">
            <span>{{ log.os }}</span>
            <div v-show="log.showUserAgent" class="user-agent-tooltip">
              {{ log.user_agent }}
            </div>
          </div>
        </td>   <!-- 操作系统 -->
        <td>{{ log.browser }}</td><!-- 浏览器 -->
        <td>{{ formatTime(log.called_at) }}</td>  <!-- 北京时间 -->
      </tr>
      </tbody>
    </table>

  </div>
</template>

<script>
import api from '../axios';  // 引入我們的全局 axios 配置
import {formatTime} from "../utils.js";

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
        showUserAgent: false  // 初始时不显示 User Agent
      }));

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
    // 显示原始 User Agent
    showUserAgent(log) {
      log.showUserAgent = true;
    },
    // 隐藏原始 User Agent
    hideUserAgent(log) {
      log.showUserAgent = false;
    },
  }
};
</script>

<style scoped>
/* 設置整體容器 */
.stats-container {
  margin: 20px;
  font-family: Arial, sans-serif;
}

.user-info {
  margin-bottom: 20px;
}

h3 {
  color: #333;
}

.stats-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  font-size: 16px;
}

.stats-card div {
  margin-bottom: 10px;
}

strong {
  color: #007bff;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 10px;
  text-align: left;
  border-top: 1px solid #e0e0e0;
}

th {
  background-color: #f4f4f4;
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
}

.browser-cell:hover .user-agent-tooltip {
  display: block;
}
</style>
