<template>
  <div>
    <h1>刪除用戶 {{ username }} 的數據</h1>

    <p>請確認要刪除的數據，這將無法恢復！</p>

    <el-table :data="deleteData" style="width: 100%">
      <el-table-column label="創建時間" prop="created_at">
        <template v-slot="scope">
          <el-input v-model="scope.row.created_at" size="small" placeholder="請輸入創建時間（格式：YYYY-MM-DD HH:MM:SS.SSSSSS）" />
        </template>
      </el-table-column>

      <el-table-column label="操作">
        <template v-slot="scope">
          <el-button @click="deleteRow(scope.$index)" type="danger" size="small">刪除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-button type="primary" @click="addRow">添加行</el-button>
    <el-button type="danger" @click="submitDeleteData">批量刪除</el-button>

    <p v-if="deleteData.length === 0" style="color: red; margin-top: 20px;">
      ⚠️ 目前沒有要刪除的數據！請先添加要刪除的行。
    </p>
  </div>
</template>

<script>
import api from "../../axios.js";  // 引入你的 api 實例

export default {
  data() {
    return {
      username: '', // 當前的用戶名
      deleteData: [
        { created_at: '' } // 初始的數據行
      ],
    };
  },
  mounted() {
    // 從路由參數中自動填充用戶名（username）
    const { username } = this.$route.query;
    this.username = username || '';  // 設置用戶名
  },
  methods: {
    // 添加刪除行
    addRow() {
      this.deleteData.push({
        created_at: '', // 每行初始只包含 created_at
      });
    },

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
          console.log("刪除成功", res.data);
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
