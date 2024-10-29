<template>
  <div class="news-section">
    <div class="section-header">
      <div class="title">
        <span :class="['dot', `dot-${type}`]"></span>
        <span class="title-text">{{ title }}</span>
        <span class="subtitle">{{ subtitle }}</span>
      </div>
      <el-button class="refresh-btn" type="text" icon="el-icon-refresh" @click="handleRefreshClick" title="刷新"></el-button>
    </div>
    <div class="news-list">
      <div
        v-for="(item, index) in newsItems"
        :key="index"
        class="news-item"
      >
        <span class="index" :class="{'hot-index': index < 3}">{{ index + 1 }}</span>
        <a :href="item.hot_url" target="_blank" class="news-content">
          <span class="news-title" :title="item.hot_label">{{ item.hot_label }}</span>
          <span class="count">🔥 {{ item.hot_value }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NewsSection',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'primary'
    },
    newsItems: {
      type: Array,
      required: true
    }
  },
  methods: {
    handleRefreshClick() {
      const button = this.$el.querySelector('.refresh-btn');
      button.classList.add('spin');
      setTimeout(() => {
        button.classList.remove('spin');
      }, 600);
      this.refreshNews();
    },
    refreshNews() {
      console.log("something");
    }
  }
}
</script>

<style scoped>
.news-section {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px; /* 增加圆角 */
  padding: 20px; /* 增加内边距 */
  margin-bottom: 20px; /* 增加外边距 */
  height: 400px; /* 设置最大高度 */
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影 */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px; /* 增加间距 */
}

.title {
  display: flex;
  align-items: center;
  gap: 10px; /* 增加间距 */
}

.dot {
  width: 8px; /* 增大点的尺寸 */
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.dot-primary { background-color: #409EFF; }
.dot-danger { background-color: #F56C6C; }
.dot-warning { background-color: #E6A23C; }
.dot-success { background-color: #67C23A; }

.title-text {
  color: #ffffff;
  font-size: 16px; /* 增大字体 */
  font-weight: 600;
}

.subtitle {
  color: #bfbfbf; /* 更柔和的颜色 */
  font-size: 14px;
}

.refresh-btn {
  color: #bfbfbf;
  font-size: 14px;
  padding: 0;
  transition: color 0.3s;
}

.refresh-btn:hover {
  color: #ffffff;
}

.news-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.news-item {
  display: flex;
  align-items: center; /* 垂直居中 */
  gap: 16px; /* 增加间距 */
  padding: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.news-item:hover {
  background-color: rgba(255, 255, 255, 0.1); /* 更明显的悬停效果 */
}

.index {
  min-width: 20px; /* 增大宽度 */
  color: #bfbfbf;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

.hot-index {
  color: #F56C6C;
  font-weight: 600;
}

.news-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center; /* 垂直居中 */
  gap: 12px;
}

.news-title {
  color: #e5eaf3;
  font-size: 14px;
  line-height: 1.6;
  flex: 1;
  margin-right: 12px; /* 增加右边距 */
}

.count {
  color: #bfbfbf;
  font-size: 13px;
  white-space: nowrap;
}

/* 自定义滚动条样式 */
.news-list::-webkit-scrollbar {
  width: 8px;
}

.news-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.news-list::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  transition: background-color 0.3s;
}

.news-list::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}


a {
    position: relative;
    text-decoration: none;
    color: #ffffff;
}
a:after {
    content: "";
    position: absolute;
    bottom: -2px;
    left: 50%;
    width: 0;
    height: 2px;
    transition: width 0.3s ease-in-out, left 0.3s ease-in-out;
    background-color: #ffffff;
}
a:hover:after {
    width: 100%;
    left: 0;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.refresh-btn.spin {
  animation: spin 0.6s linear;
}
</style>
