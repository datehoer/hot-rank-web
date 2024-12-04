<template>
  <div class="modal">
    <el-dialog
      title="今日热门总结"
      :visible.sync="dialogVisible"
      width="70%"
      :before-close="handleClose"
      class="news-dialog"
    >
      <div class="news-container">
        <div v-for="(item, index) in aiSummarizes" :key="index" class="news-item">
          <div class="news-header">
            <h3 class="news-title">{{ item.hot_lable }}</h3>
            <span class="news-tag">{{ item.hot_tag }}</span>
          </div>
          <p class="news-content">{{ item.hot_content }}</p>
        </div>
      </div>
      <template slot="title">
        <div class="dialog-title">
          <i class="el-icon-info"></i>
          <span>今日热门总结</span>
        </div>
      </template>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">确 定</el-button>
        <el-button type="primary" @click="handleCheckboxChange">今日不再显示</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getAiSummarizes } from "@/api/rank.js";

export default {
  name: "TodayTopNewsWithAI",
  data() {
    return {
      dialogVisible: true,
      aiSummarizes: [],
    };
  },
  methods: {
    list() {
      getAiSummarizes().then((response) => {
        this.aiSummarizes = response.data;
      });
    },
    handleCheckboxChange() {
      localStorage.removeItem("dontShowToday");
      const today = new Date().toDateString();
      localStorage.setItem("dontShowToday", today);
      this.dialogVisible = false;
    },
    handleClose(done) {
      this.$confirm("确认关闭？")
        .then((_) => {
          done();
        })
        .catch((_) => {});
    },
  },
  created() {
    const lastDateChecked = localStorage.getItem("dontShowToday");
    const today = new Date().toDateString();
    if (lastDateChecked === today) {
      this.dialogVisible = false;
    } else {
      this.list();
    }
  },
};
</script>

<style scoped>
.news-dialog /deep/ .el-dialog__body {
  padding: 0;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
}

.dialog-title i {
  color: #409EFF;
  font-size: 20px;
}

.news-container {
  max-height: 70vh;
  overflow-y: auto;
  padding: 20px;
}

.news-container::-webkit-scrollbar {
  width: 6px;
}

.news-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.news-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.news-container::-webkit-scrollbar-thumb:hover {
  background: #666;
}

.news-item {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  transition: background-color 0.3s ease;
}

.news-item:hover {
  background-color: #f3f4f6;
}

.news-item:last-child {
  margin-bottom: 0;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 16px;
}

.news-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  flex: 1;
}

.news-tag {
  padding: 4px 12px;
  background-color: #ecf5ff;
  color: #409EFF;
  border-radius: 20px;
  font-size: 12px;
  white-space: nowrap;
}

.news-content {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  white-space: pre-line;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  text-align: right;
}
</style>