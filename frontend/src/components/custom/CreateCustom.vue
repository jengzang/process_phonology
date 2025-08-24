<template>
  <div>
    <h1>為用戶  <strong style="color: mediumblue">{{ username }}</strong>  批量創建數據</h1>


    <el-table :data="formData":allow-drag-last-column highlight-current-row border resizable >
      <el-table-column label="簡稱" prop="簡稱" style="flex: 1.5;">
        <template v-slot="scope">
          <el-input v-model="scope.row.簡稱" size="small" placeholder="請輸入簡稱"></el-input>
        </template>
      </el-table-column>

      <el-table-column label="音典分區" prop="音典分區" style="flex: 1.5;">
        <template v-slot="scope">
          <el-input v-model="scope.row.音典分區" size="small" placeholder="請輸入音典分區"></el-input>
        </template>
      </el-table-column>

      <el-table-column label="經緯度" prop="經緯度" style="flex: 2;">
        <template v-slot="scope">
          <el-input v-model="scope.row.經緯度" size="small" placeholder="請輸入經緯度"></el-input>
        </template>
      </el-table-column>

      <el-table-column label="特徵" prop="特徵" style="flex: 1;">
        <template v-slot="scope">
          <el-input v-model="scope.row.特徵" size="small" placeholder="請輸入特徵"></el-input>
        </template>
      </el-table-column>

      <el-table-column label="值" prop="值" style="flex: 1;">
        <template v-slot="scope">
          <el-input v-model="scope.row.值" size="small" placeholder="請輸入值"></el-input>
        </template>
      </el-table-column>

      <el-table-column label="說明" prop="說明" style="flex: 2;">
        <template v-slot="scope">
          <el-input v-model="scope.row.說明" size="small" placeholder="請輸入說明"></el-input>
        </template>
      </el-table-column>

      <el-table-column label="操作" style="flex: 1;">
        <template v-slot="scope">
          <el-button @click="deleteRow(scope.$index)" type="danger" size="small">刪除行</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="justify-content: center;display: flex">
      <el-button type="primary" @click="addRow">添加行</el-button>
      <!-- 勾選框，用戶選擇是否複製上一行數據 -->
      <el-checkbox v-model="copyPreviousRow">默認複製上一行的數據</el-checkbox>
    </div>
    <div style="justify-content: center;display: flex">
      <el-button type="primary" @click="submitData" style="display: flex;justify-content: center" >批量提交</el-button>
    </div>


    <p v-if="submissionMessage" style="margin-top: 20px; color: green;">
      {{ submissionMessage }}
    </p>
  </div>
</template>

<script>
import api from "../../axios.js"; // 引入你的 api 實例

export default {
  data() {
    return {
      username: '',  // 當前的用戶名
      formData: [  // 表格數據
        {
          簡稱: '',
          音典分區: '',
          經緯度: '',
          特徵: '',
          值: '',
          說明: '',
          username: '' // 用戶名將在 mounted 中填充
        }
      ],
      submissionMessage: '', // 存放提交后提示消息
      copyPreviousRow: false, // 是否勾選"默認複製上一行的數據"
    };
  },
  mounted() {
    // 從路由參數中獲取用戶名
    const { username } = this.$route.query;
    this.username = username || '';  // 設置用戶名
    // 自動填充表格中的所有行的 username
    this.formData.forEach(row => {
      row.username = this.username;
    });
  },
  methods: {
    // 添加表格行
    addRow() {
      let newRow = {
        簡稱: '',
        音典分區: '',
        經緯度: '',
        特徵: '',
        值: '',
        說明: '',
        username: this.username
      };

      // 如果勾選了"默認複製上一行的數據"，複製上一行的數據
      if (this.copyPreviousRow && this.formData.length > 0) {
        const lastRow = this.formData[this.formData.length - 1];
        newRow = { ...lastRow };  // 複製上一行的數據
      }

      // 添加新行
      this.formData.push(newRow);
    },

    // 刪除表格行
    deleteRow(index) {
      this.formData.splice(index, 1);
    },

    // 提交數據
    async submitData() {
      try {
        // 在提交前，檢查是否有其他字段為空（除了“說明”）
        for (let row of this.formData) {
          if (!row.簡稱 || !row.音典分區 || !row.經緯度 || !row.特徵 || !row.值) {
            this.$message.warning("⚠️ 所有字段（除了'說明'）都必須填寫！");
            return; // 如果有空字段，停止提交
          }
        }
        const res = await api.post("/custom/create", this.formData);
        // 提交后清空表单数据
        this.formData = [];
        // 提示用户提交了多少份数据
        const dataCount = res.data.length || this.formData.length;
        this.submissionMessage = `✅ 已成功提交 ${dataCount} 份數據！`;
        // 显示成功提示
        this.$message.success(`批量提交成功！提交了 ${dataCount} 份數據`);
      } catch (error) {
        console.error("提交失敗", error);
        this.$message.error("❌ 提交失敗！");
      }
    }
  }
};
</script>

<style scoped>
.el-table {
  margin-bottom: 20px;
  width: 100%;
  margin-left: auto;
  margin-right: auto; /* 表格居中 */
}

.el-table th, .el-table td {
  white-space: nowrap; /* 防止单元格内容换行 */
}

.el-table-column {
  text-align: center; /* 使表格内容居中对齐 */
}

.el-table .el-input {
  width: 100%; /* 输入框宽度填满单元格 */
}

/* 让按钮和复选框排列整齐 */
.el-button {
  margin-right: 10px; /* 按钮之间的右边距 */
}

.el-checkbox {
  margin-left: 10px; /* 复选框和按钮之间的左边距 */
}

/* 使按钮和复选框水平居中 */
.el-button, .el-checkbox {
  display: inline-block;
  vertical-align: middle; /* 保证按钮和复选框对齐 */
}

/* 控制按钮和复选框之间的间距 */
.el-button + .el-checkbox {
  margin-top: 10px; /* 让复选框距离上方的按钮有适当间距 */
}

/* 添加按钮和复选框区域的上下间距 */
.el-button, .el-checkbox {
  margin-bottom: 20px; /* 按钮和复选框与下方内容的间距 */
}

.el-button:hover, .el-checkbox:hover {
  cursor: pointer;
}
</style>

