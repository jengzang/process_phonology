<template>
  <div class="ip-page">
    <div v-if="ipInfo" class="info-box">
      <h1>IP查詢 - {{ ipInfo.query }}</h1>
      <div class="info-content">
        <div><strong>國家:</strong> {{ ipInfo.country }}</div>
        <div><strong>地區:</strong> {{ ipInfo.region }}</div>
        <div><strong>城市:</strong> {{ ipInfo.city }}</div>
        <div><strong>ISP:</strong> {{ ipInfo.isp }}</div>
        <div><strong>運營商:</strong> {{ ipInfo.org }}</div>
        <div><strong>詳細信息:</strong> {{ ipInfo.as }}</div>
      </div>

      <!-- 地圖區域 -->
      <div id="map" class="map-container">
        <p>地圖顯示區域</p>
      </div>
    </div>
    <p v-else class="error-message">正在查詢中或無法取得 IP 資訊。</p>

    <!-- 按钮切换 API -->
    <div class="api-selector">
      <button @click="selectApi('ip-api')">ip-api</button>
      <button @click="selectApi('ip-sb')">ip.sb API</button>
      <button @click="selectApi('nordvpn')">NordVPN API</button>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import api from "@/axios"; // 引入 Leaflet 库

export default {
  data() {
    return {
      ip: this.$route.params.ip || "",
      ipInfo: null,
      map: null, // 存储地图实例
      selectedApi: 'ip-api', // 默认使用 ip-api
    };
  },
  async mounted() {
    await this.fetchIPInfo(); // 获取 IP 信息并初始化地图
  },
  watch: {
    // 监听 IP 路由参数变化，重新发起请求
    '$route.params.ip'(newIp) {
      this.ip = newIp;
      this.fetchIPInfo();
    }
  },
  methods: {
    // 获取 IP 信息
    async fetchIPInfo() {
      if (!this.ip) return;
      try {
        const response = await api.get(`/ip/${this.selectedApi}/${this.ip}`);
        const data = await response.data;

        // 统一格式化返回数据
        this.ipInfo = {
          query: data.query,
          country: data.country,
          region: data.region,
          city: data.city,
          isp: data.isp,
          org: data.org,
          as: data.as,
          lat: data.lat,
          lon: data.lon
        };

        // 更新地图
        if (this.ipInfo.lat && this.ipInfo.lon) {
          this.$nextTick(() => {
            this.initMap(this.ipInfo.lat, this.ipInfo.lon);
          });
        }
      } catch (err) {
        console.error("获取 IP 信息失败:", err);
        this.ipInfo = null;
      }
    },
    // 初始化地图
    initMap(lat, lon) {
      if (this.map) {
        // 销毁现有地图实例，避免旧地图影响
        this.map.remove();
      }

      // 创建一个新的地图实例
      this.map = L.map('map').setView([lat, lon], 13);

      // 添加 OpenStreetMap 瓦片图层
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map);

      // 添加新的标记
      L.marker([lat, lon]).addTo(this.map)
          .bindPopup(`<b>緯度:</b> ${lat}<br><b>經度:</b> ${lon}`)
          .openPopup();
    },
    // 选择API
    selectApi(apiUrl) {
      this.selectedApi = apiUrl;
      this.fetchIPInfo(); // 切换API后重新查询IP信息
    }
  }
};
</script>


<style scoped>
.ip-page {
  padding: 20px;
  font-family: 'Arial', sans-serif;
  background: #eafaf1; /* 更清新的苹果绿色背景色 */
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.info-box {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  border-left: 8px solid #4CAF50; /* 添加绿色左边框 */
}

h1 {
  font-size: 26px;
  font-weight: bold;
  color: #388E3C; /* 更加深沉的苹果绿色 */
  margin-bottom: 15px;
}

.info-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  color: #444;
  background-color: #e0f7e0; /* 绿色背景块 */
  border-radius: 12px;
}

.info-content div {
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 8px;

}

.info-content div:hover {
  background-color: #c8e6c9; /* 鼠标悬停时更深的绿色 */
}

.error-message {
  color: #ff4d4f;
  text-align: center;
  font-size: 18px;
}

.map-container {
  height: 300px;
  background: #b2dfdb; /* 更深的绿色用于地图区域背景 */
  border-radius: 12px;
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  border: 2px solid #4CAF50; /* 地图区域增加绿色边框 */
}

@media (max-width: 768px) {
  .info-content {
    grid-template-columns: 1fr;
  }
  .map-container {
    height: 220px; /* 移动端上稍微缩小地图区域 */
  }
}



.api-selector {
  margin-top: 20px;
  text-align: center; /* 确保按钮居中 */
  justify-items: center;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); /* 创建响应式的网格布局 */
  gap: 10px; /* 按钮之间的间隔 */
}


</style>
