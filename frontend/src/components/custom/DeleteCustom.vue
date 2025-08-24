<template>
  <div>
    <h1>刪除用戶 {{ username }} 的數據</h1>

    <p>請確認要刪除的數據，這將無法恢復！</p>

    <!-- 合并后的表格 -->
    <el-table :data="mergedData" style="width: 100%">
      <el-table-column label="簡稱" prop="簡稱"></el-table-column>
      <el-table-column label="音典分區" prop="音典分區"></el-table-column>
      <el-table-column label="經緯度" prop="經緯度"></el-table-column>
      <el-table-column label="特徵" prop="特徵"></el-table-column>
      <el-table-column label="值" prop="值"></el-table-column>
      <el-table-column label="說明" prop="說明">
        <template v-slot="scope">
          <span>{{ scope.row.說明 || '無' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="創建時間" prop="created_at">
        <template v-slot="scope">
          <el-input
              v-if="scope.row.created_at"
              v-model="scope.row.created_at"
              size="small"
              placeholder="請輸入創建時間（格式：YYYY-MM-DD HH:MM:SS.SSSSSS）"
          />
          <span v-else>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template v-slot="scope">
          <el-button
              v-if="scope.row.created_at"
              @click="deleteRow(scope.$index)"
              type="danger"
              size="small"
              color="green"
          >
            取消刪除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-button type="danger" @click="submitDeleteData">批量刪除</el-button>

    <p v-if="deleteData.length === 0" style="color: red; margin-top: 20px;">
      ⚠️ 目前沒有要刪除的數據！請先添加要刪除的行。
    </p>
  </div>
</template>

<script>
import api from "../../axios.js"; // 引入你的 api 實例
import {formatTime} from "../../utils.js"; // 假设你有一个 utils.js 用来处理时间格式化

export default {
  data() {
    return {
      users: [],
      username: '', // 當前的用戶名
      deleteData: [
        { created_at: '' } // 初始的數據行
      ],
    };
  },
  computed: {
    mergedData() {
      // 合并 users 和 deleteData
      const combinedData = [...this.users, ...this.deleteData];

      // 用 Set 去除重复的 created_at
      const seen = new Set();
      return combinedData.filter(item => {
        // 如果该 created_at 已存在，跳过
        if (seen.has(item.created_at)) {
          return false;
        }
        seen.add(item.created_at);
        return true;
      });
    }
  },

  async mounted() {
    const selectedUsers = JSON.parse(localStorage.getItem('selectedUsers'));
    const username = this.$route.query.username;  // 获取用户名

    if (selectedUsers && username) {
      // 构造请求数据
      const requestData = selectedUsers.map(createdAt => ({
        username: username,
        created_at: createdAt.replace('T', ' ')  // 将 'T' 替换为空格
      }));
      this.username = username;

      // 获取用户数据
      await this.fetchSelectedData(requestData);
    } else {
      console.log('没有选中的数据或没有用户名');
    }
  },

  methods: {
    async fetchSelectedData(requestData) {
      try {
        // 发送 POST 请求，传递包含所有 created_at 和 username 的列表
        const response = await api.post('/custom/selected', requestData);

        this.users = response.data;
        // 确保 'T' 被替换为空格
        this.users = this.users.map(user => ({
          ...user,
          created_at: user.created_at.replace('T', ' ') // 统一格式化
        }));
        // 将格式化后的 users 数据赋值给 deleteData，直接使用相同的数据源
        this.deleteData = [...this.users]; // 直接引用 users
      } catch (error) {
        console.error('请求失败:', error);
      }
    },
    formatTime,
    // 添加刪除行

    // 刪除一行
    deleteRow(index) {
      this.deleteData.splice(index, 1);
    },

    // 提交批量刪除數據
    async submitDeleteData() {
      // 校验每一行的创建时间是否已填写
      if (this.deleteData.some(item => !item.created_at)) {
        this.$message.warning("⚠️ 請填寫所有創建時間！");
        return;
      }

      // 组织批量删除的数据，这里保持时间字段与后端一致
      const deleteList = this.deleteData.map(item => ({
        username: this.username, // 保持每条数据的用户名一致
        created_at: item.created_at // 直接传递用户输入的时间
      }));

      const confirmMessage = `你確定要刪除用戶 ${this.username} 的數據嗎？這將無法恢復！🚨`;
      this.$confirm(confirmMessage, '警告', {
        type: 'warning'
      }).then(async () => {
        try {
          // 发送到后端，后端将接收一个包含多个对象的列表
          const res = await api.delete("/custom/delete", {
            data: deleteList, // 批量刪除的數據
          });
          this.$message.success("✅ 批量刪除成功！");
        } catch (error) {
          console.error("刪除失敗", error);
          this.$message.error("❌ 刪除失敗！");
        }
      }).catch(() => {
        this.$message.info("取消刪除操作。😌");
      });
    }
  }
};
</script>

<style scoped>
.el-table {
  margin-bottom: 20px;
}
</style>
