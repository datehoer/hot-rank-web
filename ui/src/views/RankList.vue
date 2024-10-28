<template>
  <div class="app-container">
    <!-- 顶部搜索栏 -->
    <div class="header">
      <div class="header-content">
        <div class="logo-search">
          <!-- 左侧 logo -->
          <div class="logo">
            <img src="@/assets/logo.png" alt="Logo" class="logo-image"/>
          </div>
          
          <!-- 搜索栏 -->
          <div class="search-bar">
            <el-input
              placeholder="搜索"
              prefix-icon="el-icon-search"
              v-model="searchText"
              class="search-input"
              size="small"
            />
          </div>
        </div>

        <!-- 右侧按钮组 -->
        <!-- <div class="header-buttons">
          <el-button type="success" size="small" plain class="login-btn">登录</el-button>
          <el-button type="primary" size="small" class="register-btn">注册</el-button>
        </div> -->
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="16">
        <el-col 
          v-for="section in newsSections" 
          :key="section.id"
          :span="24 / columnsCount"
        >
          <news-section
            :title="section.name"
            :subtitle="section.subtitle"
            :type="section.type"
            :news-items="section.data"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 右侧用户面板 -->
    <user-panel/>
  </div>
</template>

<script>
import NewsSection from '@/components/NewsSection.vue'
import UserPanel from '@/components/UserPanel.vue'
import {getRankList} from "@/api/rank.js"
import moment from 'moment'
export default {
  name: 'App',
  components: {
    NewsSection,
    UserPanel
  },
  data() {
    return {
      searchText: '',
      // 设置每行显示的列数（1-4）
      columnsCount: 3,
      newsSections: [],
    }
  },
  computed: {
    // 计算最大列数
    maxColumns() {
      return Math.min(this.newsSections.length, 4)
    }
  },
  created() {
    this.fetchRankList()
  },
  watch: {
    // 监听 columnsCount 确保不超过最大值
    columnsCount(newVal) {
      if (newVal > this.maxColumns) {
        this.columnsCount = this.maxColumns
      }
      if (newVal < 1) {
        this.columnsCount = 1
      }
    }
  },
  methods: {
    fetchRankList() {
      getRankList().then(response => {
        this.newsSections = response.data.map(item => {
          const subtitle = moment(item.insert_time, "YYYY-MM-DD HH:mm:ss").fromNow()
          const type = item.hot_type === '1' ? 'primary' : item.hot_type === '2' ? 'danger' : item.hot_type === '3' ? 'success' : 'warning'
          return {
            ...item,
            subtitle,
            type
          }
        })
      })
    }
  }
}
</script>

<style>
body {
  margin: 0;
  background-color: #1a1a1a;
  color: #E5EAF3;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.app-container {
  min-height: 100vh;
  padding: 16px;
  padding-right: 340px;
}

.header {
  height: 50px;
  background-color: #242424;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  height: 100%;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-search {
  display: flex;
  align-items: center;
  gap: 16px; /* Logo 和搜索栏之间的间距 */
}

.logo {
  color: #409EFF;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-image {
  height: 40px; /* 根据需要调整 */
  width: auto;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 16px;
}

.search-input {
  width: 300px;
}

.search-input :deep(.el-input__inner) {
  height: 36px; /* 增加高度 */
  line-height: 36px;
  background-color: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 18px; /* 更圆润的边框 */
  color: #fff;
  font-size: 14px;
  padding-left: 12px; /* 内部左侧填充 */
}


.search-input :deep(.el-input__prefix) {
  left: 12px; /* 调整图标位置 */
}

.search-input :deep(.el-input__icon) {
  line-height: 32px;
  color: #909399;
}

.header-buttons {
  display: flex;
  gap: 8px;
}

.login-btn {
  border: 1px solid #67c23a;
  color: #67c23a;
  background: transparent;
}

.login-btn:hover {
  color: #fff;
  border-color: #67c23a;
  background-color: #67c23a;
}

.register-btn {
  background-color: #409EFF;
  border-color: #409EFF;
}

:deep(.el-button--small) {
  padding: 8px 15px;
  font-size: 13px;
}

.main-content {
  margin-top: 66px;
  padding: 0 16px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

:deep(.el-button--small) {
  padding: 8px 15px;
}

/* 响应式布局样式 */
@media (max-width: 768px) {
  .search-bar {
    max-width: 200px;
  }
  
  .header-content {
    padding: 0 8px;
  }
}

@media (max-width: 1400px) {
  .app-container {
    padding-right: 16px;
  }
  
  .user-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  [class*="el-col-"] {
    width: 100% !important;
  }
}
@media (max-width: 1200px) {
  .search-input {
    width: 250px;
  }
}

@media (max-width: 992px) {
  .search-input {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .search-input {
    width: 150px;
  }
}

@media (max-width: 576px) {
  .search-input {
    width: 120px;
  }
}
@media (max-width: 768px) {
  .logo-search {
    gap: 12px;
  }

  .search-input {
    width: 150px;
  }

  .header-content {
    padding: 0 12px;
  }

  .header-buttons {
    gap: 8px;
  }
}

@media (max-width: 576px) {
  .header {
    height: 50px;
  }

  .search-input {
    width: 120px;
  }

  :deep(.el-button--small) {
    padding: 6px 12px;
    font-size: 12px;
  }

  .main-content {
    padding: 0 12px;
    margin-top: 70px;
  }
}
</style>