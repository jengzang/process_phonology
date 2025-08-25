<!-- src/components/ApiStatsChart.assets -->
<template>
  <div>
    <h3>API 调用统计</h3>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement, TimeScale } from 'chart.js';
import api from '../../axios.js'; // 引入API请求配置
import 'chartjs-adapter-date-fns'; // 引入时间适配器

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement, TimeScale);

export default {
  components: {
    Line
  },
  data() {
    return {
      chartData: {
        labels: [],  // 时间（横坐标）
        datasets: [
          {
            label: 'API 调用次数',
            data: [], // API调用次数
            borderColor: 'rgba(75,192,192,1)',
            backgroundColor: 'rgba(75,192,192,0.2)',
            fill: false,
            tension: 0.4,
          },
          {
            label: 'API 调用持续时间',
            data: [], // API调用持续时间
            borderColor: 'rgba(255,99,132,1)',
            backgroundColor: 'rgba(255,99,132,0.2)',
            fill: false,
            tension: 0.4,
          },
        ]
      },
      chartOptions: {
        responsive: true,
        scales: {
          x: {
            type: 'time', // 使用时间类型的横坐标
            time: {
              unit: 'day', // 根据你的数据间隔选择合适的单位：'minute', 'hour', 'day'
              tooltipFormat: 'll HH:mm',  // 格式化时间显示
            },
            title: {
              display: true,
              text: '时间',
            },
            min: new Date('2025-08-21T00:00:00Z'), // 手动设置最小时间范围（可以根据你的数据调整）
            max: new Date('2025-08-23T23:59:59Z'), // 手动设置最大时间范围（可以根据你的数据调整）
          },
          y: {
            title: {
              display: true,
              text: '值',
            },
          },
        },
      },
    };
  },
  async mounted() {
    try {
      const response = await api.get(`/api-usage/api-usage`); // 请求后端数据
      const apiLogs = response.data;

      // 格式化数据以适应图表
      let timeLabels = [];
      let apiCallCounts = [];
      let totalDurations = [];

      apiLogs.forEach(log => {
        // 去掉微秒部分，只保留时分秒和毫秒，格式为："2025-08-23 08:59:52.590"
        const cleanedTime = log.called_at.replace(/(\.\d{3})\d+$/, '$1'); // 只保留到毫秒部分
        const calledAt = new Date(cleanedTime); // 创建 Date 对象

        // 如果 calledAt 无效，则跳过该数据
        if (isNaN(calledAt)) {
          console.error('Invalid time format:', log.called_at);
          return;
        }
        timeLabels.push(calledAt); // 时间作为横坐标
        // apiCallCounts.push(log.occurrenceCount); // API调用次数
        totalDurations.push(log.duration); // API调用的持续时间
      });

      // console.log('Time Labels:', timeLabels);
      // console.log('API Call Counts:', apiCallCounts);
      // console.log('Total Durations:', totalDurations);

      // 更新图表数据
      this.chartData.labels = timeLabels;
      // this.chartData.datasets[0].data = apiCallCounts; // 设置 API 调用次数数据
      this.chartData.datasets[0].data = totalDurations; // 设置 API 调用持续时间数据
    } catch (error) {
      console.error('Error fetching API usage data', error);
    }
  },
};
</script>

<style scoped>
/* 添加样式 */
</style>
