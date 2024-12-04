<template>
  <div
    class="app-container"
    v-loading="loading"
    element-loading-text="拼命加载中"
    element-loading-spinner="el-icon-loading"
    element-loading-background="rgba(0, 0, 0, 0.8)"
  >
    <!-- 顶部搜索栏 -->
    <div class="header">
      <div class="header-content">
        <div class="logo-search">
          <!-- 左侧 logo -->
          <div class="logo" title="HotRank">
            <img src="@/assets/logo.png" alt="Logo" class="logo-image"/>
          </div>
          
          <!-- 搜索栏 -->
          <!-- <div class="search-bar">
            <el-input
              placeholder="用来装饰的搜索栏"
              prefix-icon="el-icon-search"
              v-model="searchText"
              class="search-input"
              size="small"
            />
          </div> -->
        </div>

        <!-- 右侧按钮组 -->
        <!-- <div class="header-buttons">
          <el-button type="success" size="small" plain class="login-btn">登录</el-button>
          <el-button type="primary" size="small" class="register-btn">注册</el-button>
        </div> -->
      </div>
    </div>
    <TodayTopNewsWithAI />
    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="16">
        <el-col 
          v-for="section in filteredNewsSections" 
          :key="section.id"
          :span="24 / columnsCount"
        >
          <news-section
            :title="section.name"
            :subtitle="section.subtitle"
            :type="section.type"
            :news-items="section.data"
            :wrap-text="wrapText"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 右侧用户面板 -->
    <el-button
      v-if="isMobile"
      class="mobile-panel-button"
      type="primary"
      circle
      icon="el-icon-setting"
      @click="showMobilePanel = true"
    />
    <user-panel
      v-if="!isMobile"
      @update-columns-count="updateColumnsCount"
      @update-wrap-text="updateWrapText"
      @update-selected-sites="updateSelectedSites"
      :columns-count="columnsCount"
    />
    <el-drawer
      :visible.sync="showMobilePanel"
      direction="rtl"
      size="80%"
      :with-header="false"
      custom-class="mobile-drawer"
    >
      <user-panel
        @update-columns-count="updateColumnsCount"
        @update-wrap-text="updateWrapText"
        @update-selected-sites="updateSelectedSites"
        @update-sites-order="updateSitesOrder"
        @update-show-all-sites="updateShowAllSites"
        :columns-count="columnsCount"
        :show-all-sites="showAllSites"
      />
    </el-drawer>
  </div>
</template>

<script>
import NewsSection from '@/components/NewsSection.vue'
import UserPanel from '@/components/UserPanel.vue'
import TodayTopNewsWithAI from "@/components/TodayTopNewsWithAI"
import {getRankList} from "@/api/rank.js"
import moment from 'moment'
export default {
  name: 'App',
  components: {
    NewsSection,
    UserPanel,
    TodayTopNewsWithAI
  },
  data() {
    return {
      searchText: '',
      // 设置每行显示的列数（1-4）
      columnsCount: 3,
      newsSections: [],
      selectedSites: [],
      loading: false,
      showMobilePanel: false,
      isMobile: false,
      wrapText: true,
      showAllSites: true,
    }
  },
  computed: {
    // 计算最大列数
    maxColumns() {
      return Math.min(this.newsSections.length, 4)
    },
    filteredNewsSections() {
      if (this.selectedSites.includes("*")){
        return this.newsSections
      }else{
        return this.newsSections.filter(section => 
          this.selectedSites.includes(section.name)
        );
      }
    }
  },
  created() {
    const savedOrder = this.$localStorage.get('sitesOrder', null);
    this.showAllSites = this.$localStorage.get('showAllSites', true);
    this.selectedSites = this.$localStorage.get('selectedSites', []);
    this.fetchRankList(savedOrder);
    this.columnsCount = this.$localStorage.get('columnsCount', 3);
    this.wrapText = this.$localStorage.get('wrapText', true);
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile);
  },
  destroyed() {
    window.removeEventListener('resize', this.checkMobile);
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 1400;
    },
    updateSelectedSites(sites) {
      this.selectedSites = sites;
      this.$localStorage.set('selectedSites', sites);
    },
    updateSitesOrder(orderedSites) {
      // 根据排序后的站点名称重新排序 newsSections
      this.newsSections.sort((a, b) => {
        const indexA = orderedSites.indexOf(a.name);
        const indexB = orderedSites.indexOf(b.name);
        return indexA - indexB;
      });
      // 保存排序到本地存储
      this.$localStorage.set('sitesOrder', orderedSites);
    },
    updateColumnsCount(newColumnsCount) {
      this.columnsCount = newColumnsCount;
      this.$localStorage.set('columnsCount', this.columnsCount);
    },
    updateWrapText(newWrapText) {
      this.wrapText = newWrapText;
      this.$localStorage.set('wrapText', this.wrapText);
    },
    fetchRankList(savedOrder = null) {
    this.loading = true;
    getRankList().then(response => {
      // 1. 先处理新数据
      this.newsSections = response.data.map(item => {
        const insertTime = moment(item.insert_time, "YYYY-MM-DD HH:mm:ss");
        const subtitle = insertTime.fromNow();
        const now = moment();
        const diffHours = now.diff(insertTime, 'hours');
        const type = diffHours <= 1 ? 'primary' : 
                 diffHours <= 4 ? 'danger' : 
                 'warning';
        return {
          ...item,
          subtitle,
          type
        };
      });

      // 2. 处理排序
      const allSiteNames = this.newsSections.map(section => section.name);
      if (savedOrder) {
        // 清理排序数据，只保留存在的站点
        const cleanedOrder = savedOrder.filter(site => allSiteNames.includes(site));
        // 添加新增的站点到排序末尾
        const newSites = allSiteNames.filter(site => !cleanedOrder.includes(site));
        const updatedOrder = [...cleanedOrder, ...newSites];
        
        // 更新排序并保存
        this.$localStorage.set('sitesOrder', updatedOrder);
        
        // 应用排序
        this.newsSections.sort((a, b) => {
          const indexA = updatedOrder.indexOf(a.name);
          const indexB = updatedOrder.indexOf(b.name);
          return indexA - indexB;
        });
      } else {
        // 如果没有保存的排序，创建新的排序并保存
        this.$localStorage.set('sitesOrder', allSiteNames);
      }

      // 3. 处理站点选择
      if (this.showAllSites) {
        this.selectedSites = allSiteNames;
      } else {
        const savedSelectedSites = this.$localStorage.get('selectedSites', []);
        // 清理选中的站点，只保留仍然存在的站点
        this.selectedSites = savedSelectedSites.filter(site => 
          allSiteNames.includes(site)
        );
        // 如果清理后没有选中的站点，则选择所有站点
        if (this.selectedSites.length === 0) {
          this.selectedSites = allSiteNames;
          this.showAllSites = true;
        }
      }
      
      // 保存最终状态
      this.$localStorage.set('selectedSites', this.selectedSites);
      this.$localStorage.set('showAllSites', this.showAllSites);
      this.loading = false;
      });
    },
    updateShowAllSites(value) {
      this.showAllSites = value;
      this.$localStorage.set('showAllSites', value);
      if (value) {
        this.selectedSites = this.newsSections.map(section => section.name);
        this.$localStorage.set('selectedSites', this.selectedSites);
      }
    }
  }
}
</script>

<style>
@import '@/styles/themes.css';

body {
  margin: 0;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.app-container {
  min-height: 100vh;
  padding: 16px;
  padding-right: 340px;
}

.header {
  height: 50px;
  background-color: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
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
.mobile-panel-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.mobile-drawer {
  background-color: #242424;
}

.mobile-drawer :deep(.el-drawer__container) {
  background-color: #242424;
}

/* 确保抽屉内的user-panel样式正确 */
.el-drawer .user-panel {
  position: static;
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}
</style>