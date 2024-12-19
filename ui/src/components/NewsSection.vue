<template>
  <div class="news-section" :class="{ 'tab-layout': isTabLayout }">
    <div v-if="!isTabLayout" class="section-header">
      <div class="title">
        <span :class="['dot', `dot-${type}`]"></span>
        <span class="title-text">{{ title }}</span>
        <span class="subtitle">{{ subtitle }}</span>
      </div>
      <el-button class="refresh-btn" type="text" icon="el-icon-refresh" @click="handleRefreshClick" title="刷新"></el-button>
    </div>
    
    <template v-if="isTabLayout">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane 
          v-for="section in allSections" 
          :key="section.name"
          :label="section.name" 
          :name="section.name"
        >
          <div class="tab-header">
            <span class="subtitle">{{ section.subtitle }}</span>
            <el-button class="refresh-btn" type="text" icon="el-icon-refresh" @click="handleRefreshClick" title="刷新"></el-button>
          </div>
          <div class="news-list">
            <div
              v-for="(item, idx) in section.data"
              :key="idx"
              class="news-item"
            >
              <span class="index" :class="{'hot-index': idx < 3}">{{ idx + 1 }}</span>
              <a v-if="item.hot_url" :href="item.hot_url" target="_blank" class="news-content">
                <span class="news-title" :title="item.hot_label">{{ item.hot_label }}</span>
                <span class="count">🔥 {{ item.hot_value }}</span>
              </a>
              <span v-else class="news-content">
                <span class="news-title" :title="item.hot_label">{{ item.hot_label }}</span>
                <span class="count">🔥 {{ item.hot_value }}</span>
              </span>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>

    <div v-else class="news-list">
      <div
        v-for="(item, index) in newsItems"
        :key="index"
        class="news-item"
      >
        <span class="index" :class="{'hot-index': index < 3}">{{ index + 1 }}</span>
        <a v-if="item.hot_url" :href="item.hot_url" target="_blank" class="news-content">
          <span class="news-title" :title="item.hot_label">{{ item.hot_label }}</span>
          <span class="count">🔥 {{ item.hot_value }}</span>
        </a>
        <span v-else class="news-content">
          <span class="news-title" :title="item.hot_label">{{ item.hot_label }}</span>
          <span class="count">🔥 {{ item.hot_value }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { refresh } from '@/api/rank'

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
    },
    wrapText: {
      type: Boolean,
      default: true
    },
    isTabLayout: {
      type: Boolean,
      default: false
    },
    allSections: {
      type: Array,
      default: () => []
    },
  },
  data() {
    return {
      activeTab: ''
    }
  },
  created() {
    if (this.isTabLayout && this.allSections.length > 0) {
      this.activeTab = this.allSections[0].name
    }
  },
  watch: {
    wrapText: {
      immediate: true,
      handler(val) {
        document.documentElement.style.setProperty(
          '--news-title-white-space',
          val ? 'nowrap' : 'normal'
        );
      }
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
    handleTabClick(tab) {
      this.$emit('tab-change', tab.name);
    },
    refreshNews() {
      refresh().then((response) => {
        let message = response.msg;
        this.$message({
          message: message,
          type: 'success'
        });
        this.$emit("update");
      })
    }
  }
}
</script>

<style scoped>
.news-section {
  background: var(--card-bg);
  color: var(--text-color);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  height: 400px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.news-section.tab-layout {
  height: 600px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 16px;
}

/* Override element-ui tab styles */
:deep(.el-tabs__header) {
  margin-bottom: 16px;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
}

:deep(.el-tabs__item) {
  color: var(--text-color);
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF;
}

:deep(.el-tabs__active-bar) {
  background-color: #409EFF;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.dot-primary { background-color: #409EFF; }
.dot-danger { background-color: #F56C6C; }
.dot-warning { background-color: #E6A23C; }
.dot-success { background-color: #67C23A; }

.title-text {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
}

.subtitle {
  color: var(--text-color);
  font-size: 14px;
}

.refresh-btn {
  color: var(--text-color);
  font-size: 14px;
  padding: 0;
  transition: color 0.3s;
}

.refresh-btn:hover {
  color: var(--text-color);
}

.news-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.news-item {
  display: flex;
  align-items: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  gap: 16px;
  padding: 3px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
  box-sizing: border-box;
}

.news-item:hover {
  background: var(--card-bg);
}

.index {
  min-width: 20px;
  color: var(--text-color);
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

.hot-index {
  color: var(--text-color);
  font-weight: 600;
}

.news-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  min-width: 0;
}

.news-title {
  flex: 7;
  min-width: 0;
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: var(--news-title-white-space);
  padding-right: 12px;
}

.count {
  flex: 3;
  color: var(--text-color);
  font-size: 13px;
  white-space: nowrap;
  text-align: right;
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
