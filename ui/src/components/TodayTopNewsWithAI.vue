<template>
  <div class="modal">
    <el-dialog
      title=""
      :visible.sync="dialogVisible"
      width="70%"
      :before-close="handleClose"
      custom-class="news-dialog"
      v-loading="isLoading"
    >
      <template slot="title">
        <div class="dialog-title">
          <i class="el-icon-info"></i>
          <span>今日热点总结|每小时更新</span>
        </div>
      </template>
      
      <div class="dialog-content">
        <div class="news-container" ref="newsContainer">
          <div 
            v-for="(item, index) in aiSummarizes" 
            :key="index" 
            class="news-item"
            :id="`news-${index}`"
          >
            <div class="news-header">
              <div class="news-title-group">
                <span class="news-tag">{{ item.hot_tag }}</span>
                <h3 class="news-title">{{ item.hot_label }}</h3>
              </div>
              <el-button 
                type="text"
                size="small"
                class="news-link"
                @click="goToNews(item.hot_url)"
              >
                <i class="el-icon-link"></i>
                查看原文
              </el-button>
            </div>
            <p class="news-content">{{ item.hot_content }}</p>
          </div>
        </div>

        <!-- 右侧导航栏 -->
        <div class="news-nav">
          <div 
            v-for="(item, index) in aiSummarizes" 
            :key="index"
            class="nav-item"
            :class="{ 'active': activeIndex === index }"
            @click="scrollToNews(index)"
          >
            {{ item.hot_tag }}
          </div>
        </div>
      </div>

      <template slot="footer">
        <div class="dialog-footer">
          <el-button type="info" @click="handleCheckboxChange" size="small">今日不再提示</el-button>
          <el-button type="primary" @click="dialogVisible = false" size="small">关 闭</el-button>
        </div>
      </template>
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
      activeIndex: 0,
      observer: null,
      isLoading: false,
    };
  },
  methods: {
    list() {
      this.isLoading=true;
      getAiSummarizes().then((response) => {
        this.aiSummarizes = response.data;
        this.$nextTick(() => {
          this.setupIntersectionObserver();
        });
        this.isLoading=false;
      });
    },
    handleCheckboxChange() {
      localStorage.removeItem("dontShowToday");
      const today = new Date().toDateString();
      localStorage.setItem("dontShowToday", today);
      this.dialogVisible = false;
    },
    handleClose(done) {
      done();
    },
    scrollToNews(index) {
      const element = document.getElementById(`news-${index}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    },
    setupIntersectionObserver() {
      // 清除旧的观察者
      if (this.observer) {
        this.observer.disconnect();
      }

      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const index = Number(entry.target.id.split('-')[1]);
              this.activeIndex = index;
            }
          });
        },
        {
          root: this.$refs.newsContainer,
          threshold: 0.5
        }
      );

      // 观察所有新闻项
      this.aiSummarizes.forEach((_, index) => {
        const element = document.getElementById(`news-${index}`);
        if (element) {
          this.observer.observe(element);
        }
      });
    },
    goToNews(url) {
      if (url) {
        window.open(url, '_blank');
      }
    }
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
  beforeDestroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
};
</script>

<style scoped>
/* 对话框样式 */
.news-dialog .el-dialog__body {
  padding: 0 !important;
}

.news-dialog .el-dialog__header {
  padding: 15px 20px !important;
  border-bottom: 1px solid #ebeef5;
}

.news-dialog .el-dialog__footer {
  border-top: 1px solid #ebeef5;
  padding: 10px 20px !important;
}
::v-deep .news-dialog {
  margin-top: 8vh !important;
}

/* 标题样式 */
.dialog-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.dialog-title i {
  color: #409EFF;
  margin-right: 8px;
  font-size: 18px;
}

/* 内容区域布局 */
.dialog-content {
  display: flex;
  position: relative;
}

/* 左侧新闻列表 */
.news-container {
  flex: 1;
  max-height: 65vh;
  overflow-y: auto;
  padding: 20px;
  padding-right: 10px;
  background-color: #f5f7fa;
}

.news-container::-webkit-scrollbar {
  width: 4px;
}

.news-container::-webkit-scrollbar-track {
  background: transparent;
}

.news-container::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 2px;
}

.news-container::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* 右侧导航栏 */
.news-nav {
  width: 120px;
  padding: 20px 10px;
  background-color: #ffffff;
  border-left: 1px solid #ebeef5;
  position: sticky;
  top: 0;
  height: fit-content;
  max-height: 65vh;
  overflow-y: auto;
}

.news-nav::-webkit-scrollbar {
  width: 4px;
}

.news-nav::-webkit-scrollbar-track {
  background: transparent;
}

.news-nav::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 2px;
}

.news-nav::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

.nav-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.3s;
  border-radius: 4px;
  line-height: 1.4;
}

.nav-item:last-child {
  margin-bottom: 0;
}

.nav-item:hover {
  color: #409EFF;
  background-color: #ecf5ff;
}

.nav-item.active {
  color: #409EFF;
  background-color: #ecf5ff;
  font-weight: 500;
}

/* 新闻项样式 */
.news-item {
  background-color: #ffffff;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.news-item:last-child {
  margin-bottom: 0;
}

.news-header {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.news-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.news-tag {
  background-color: #ecf5ff;
  color: #409EFF;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.news-title {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  line-height: 1.4;
}

.news-content {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  text-align: justify;
}

.news-link {
  padding: 4px 0;
  color: #409EFF;
  font-size: 13px;
}

.news-link i {
  margin-right: 4px;
}

.news-link:hover {
  color: #66b1ff;
}
</style>