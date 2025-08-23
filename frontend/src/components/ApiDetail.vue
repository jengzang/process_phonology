<template>
  <div>
    <h2>近期 API 使用詳情</h2>

    <!-- 功能统计部分 -->
    <div class="stats">
      <button @click="showUniqueUsers" class="stat-btn">所有用户: {{ uniqueUsersCount }}</button>
      <button @click="showUniqueIPs" class="stat-btn">所有IP: {{ uniqueIPsCount }}</button>
      <button @click="showAPICalls" class="stat-btn">API調用數: {{ totalAPICalls }}</button>
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
              :class="{ 'clickable': userStat.user !== '未登錄用戶' }"
              @click="userStat.user !== '未登錄用戶' && viewUserStats(userStat.user)"
          >
            <td>{{ userStat.user }}</td>  <!-- 显示用户名 -->
            <td>{{ userStat.totalDuration.toFixed(3) }}s</td> <!-- 总使用时长 -->
            <td>{{ userStat.occurrenceCount }}</td> <!-- 出现次数 -->
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
          </tr>
          </thead>
          <tbody>
          <tr v-for="ipStat in ipStats" :key="ipStat.ip">
            <td>{{ ipStat.ip }}</td>
            <td>{{ ipStat.totalDuration.toFixed(3) }}s</td> <!-- 总使用时长 -->
            <td>{{ ipStat.occurrenceCount }}</td> <!-- 出现次数 -->
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
            <th>調用次數</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(count, path) in apiCalls" :key="path">
            <td>{{ path }}</td>
            <td>{{ count }}</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>


    <table>
      <thead>
      <tr>
        <th>用戶</th>
        <th>IP 地址</th>
        <th>API 路徑</th>
        <th>持續時長</th>
        <th>操作系統</th>
        <th>瀏覽器</th>
        <th>請求時間</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(log, index) in apiLogs" :key="index">
        <td>{{ log.user || '' }}</td> <!-- 用户 -->
        <td>{{ log.ip }}</td>
        <td>{{ log.path }}</td>
        <td>{{ log.duration.toFixed(3) }}s</td>  <!-- 持续时长 -->
        <td>{{ log.os }}</td> <!-- 操作系统 -->
        <td>{{ log.browser }}</td> <!-- 浏览器 -->
        <td>{{ formatTime(log.called_at) }}</td> <!-- 使用时间 -->
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from '../axios';  // 引入全局 axios 配置

export default {
  data() {
    return {
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
    };
  },
  async mounted() {
    try {
      const response = await api.get(`/api-usage/api-usage`);  // 请求后端接口获取 API 使用情况
      this.apiLogs = response.data;  // 处理返回的 API 使用记录

      // 独特用户统计
      this.uniqueUsers = [...new Set(this.apiLogs.map(log => log.user || ''))];
      this.uniqueUsersCount = this.uniqueUsers.length;

      this.userStats = this.uniqueUsers.map(user => {
        const userLogs = this.apiLogs.filter(log => log.user === user);
        const totalDuration = userLogs.reduce((acc, log) => acc + log.duration, 0);
        const occurrenceCount = userLogs.length;
        return { user: user || '未登錄用戶', totalDuration, occurrenceCount };  // 处理空用户名
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
        return { ip, totalDuration, occurrenceCount };
      });

      // 排序：按总使用时长从大到小
      this.ipStats.sort((a, b) => b.totalDuration - a.totalDuration);

      // 统计每个 API 调用的次数和总数
      this.apiCalls = this.apiLogs.reduce((acc, log) => {
        acc[log.path] = (acc[log.path] || 0) + 1;
        this.totalAPICalls += 1;
        return acc;
      }, {});
    } catch (error) {
      console.error('Error fetching API usage data', error);
    }
  },
  methods: {
    // 將 UTC 時間轉換為北京時間（加上 8 小時）
    formatTime(lastLogin) {
      if (!lastLogin) return '未知時間';  // 如果時間無效，顯示"未知時間"
      const date = new Date(lastLogin);  // 轉換為 Date 對象
      if (isNaN(date)) return '無效時間';  // 檢查時間是否有效
      date.setHours(date.getHours() + 8);  // 增加 8 小時以轉換為北京時間
      return date.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });  // 格式化為北京時間
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
  }
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
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
}

.stat-btn:hover {
  background-color: #45a049;
}

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
  width: 80%;
  max-width: 800px;
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


tr.clickable:hover {
  background-color: #ddecdf; /* 背景色变化 */
  transition: background-color 0.3s ease; /* 平滑过渡 */
  cursor: pointer;
}


</style>