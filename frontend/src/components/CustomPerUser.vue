<template>
  <div>
    <h1>{{username}}的個人數據</h1>
    <table v-if="users.length" border="1">
      <thead>
      <tr>
        <th>簡稱</th>
        <th>音典分區</th>
        <th>經緯度</th>
        <th>特徵</th>
        <th>值</th>
        <th>說明</th>
        <th>創建時間</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="user in users" :key="user.id">
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
  </div>
</template>

<script>
import api from "../axios";
import {formatTime} from "../utils.js";

export default {
  methods: {formatTime},
  data() {
    return {
      users: [],  // 用於存儲從 API 獲取的用戶數據
    };
  },
  async mounted() {
    const { username } = this.$route.query;  // 從路由參數中獲取用戶名
    this.username = username;  // 設置當前的用戶名
    try {
      const response = await api.get(`/custom-query/user?query=${username}`);
      this.users = response.data;
    } catch (error) {
      console.error("API 請求錯誤:", error);
    }
  },
};
</script>

<style scoped>
/* 在這裡定義樣式，例如表格的基本樣式 */
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 8px 12px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
</style>
