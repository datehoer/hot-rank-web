<template>
  <div
    class="app-container"
    v-loading="loading"
    element-loading-text="拼命加载中"
    element-loading-spinner="el-icon-loading"
  >
    <!-- 顶部搜索栏 -->
    <div class="header">
      <div class="header-content">
        <div class="logo-search">
          <!-- 左侧 logo -->
          <div class="logo" title="HotRank">
            <!-- <img src="@/assets/logo.png" alt="Logo" class="logo-image"/> -->
            <robot
              theme="two-tone"
              size="30"
              :fill="['#e23333', '#db882c']"
              :strokeWidth="3"
              @click="dialogVisible = true"
              title="AI Summary"
            />
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
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 栅格布局 -->
      <template v-if="layoutMode === 'grid'">
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
              @update="handleUpdate"
            />
          </el-col>
        </el-row>
      </template>

      <!-- 标签页布局 -->
      <template v-else>
        <el-tabs v-model="activeTab" class="news-tabs">
          <el-tab-pane
            v-for="section in filteredNewsSections"
            :key="section.id"
            :label="section.name"
            :name="section.name"
          >
            <div class="tab-header">
              <span class="tab-subtitle">{{ section.subtitle }}</span>
              <el-tag :type="section.type" size="small" effect="plain">
                {{ section.type === 'primary' ? '最新' : section.type === 'danger' ? '热门' : '常规' }}
              </el-tag>
            </div>
            <news-section
              :title="section.name"
              :subtitle="section.subtitle"
              :type="section.type"
              :news-items="section.data"
              :wrap-text="wrapText"
              @update="handleUpdate"
              class="tab-news-section"
            />
          </el-tab-pane>
        </el-tabs>
      </template>
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
      @update-layout-mode="updateLayoutMode"
      @update-sites-order="updateSitesOrder"
      @update-show-all-sites="updateShowAllSites"
      :columns-count="columnsCount"
      :layout-mode="layoutMode"
      :show-all-sites="showAllSites"
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
    <el-dialog
      class="news-summary-dialog"
      title=""
      :visible.sync="dialogVisible"
      width="70%"
      style="margin-top: -6vh"
      :before-close="handleClose"
      custom-class="news-dialog"
    >
      <template slot="title">
        <div class="dialog-title">
          <i class="el-icon-info"></i>
          <span>今日热点总结|每小时更新</span>
        </div>
      </template>

      <div
        class="dialog-content"
        v-loading="isLoading"
        element-loading-text="星链查询中"
        element-loading-spinner="el-icon-loading"
      >
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
            :class="{ active: activeIndex === index }"
            @click="scrollToNews(index)"
          >
            {{ item.hot_tag }}
          </div>
        </div>
      </div>

      <template slot="footer">
        <div class="dialog-footer">
          <el-button type="info" @click="handleCheckboxChange" size="small"
            >今日不再提示</el-button
          >
          <el-button type="primary" @click="dialogVisible = false" size="small"
            >关 闭</el-button
          >
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import NewsSection from "@/components/NewsSection.vue";
import UserPanel from "@/components/UserPanel.vue";
import { getRankList, getAiSummarizes } from "@/api/rank.js";
import moment from "moment";
import { Robot } from "@icon-park/vue";
import { set } from 'vue';
export default {
  name: "App",
  components: {
    NewsSection,
    UserPanel,
    Robot,
  },
  data() {
    return {
      searchText: "",
      // 设置每行显示的列数（1-4）
      columnsCount: 3,
      newsSections: [],
      selectedSites: [],
      loading: false,
      showMobilePanel: false,
      isMobile: false,
      wrapText: true,
      showAllSites: true,
      dialogVisible: true,
      aiSummarizes: [],
      activeIndex: 0,
      observer: null,
      isLoading: false,
      isTabLayout: false,
      layoutMode: 'tabs',
      activeTab: '',
    };
  },
  computed: {
    // 计算最大列数
    maxColumns() {
      return Math.min(this.newsSections.length, 4);
    },
    filteredNewsSections() {
      if (this.selectedSites.includes("*")) {
        return this.newsSections;
      } else {
        return this.newsSections.filter((section) =>
          this.selectedSites.includes(section.name)
        );
      }
    },
  },
  created() {
    const savedOrder = this.$localStorage.get("sitesOrder", null);
    this.showAllSites = this.$localStorage.get("showAllSites", true);
    this.selectedSites = this.$localStorage.get("selectedSites", []);
    this.fetchRankList(savedOrder);
    this.columnsCount = this.$localStorage.get("columnsCount", 3);
    this.wrapText = this.$localStorage.get("wrapText", true);
    this.checkMobile();
    window.addEventListener("resize", this.checkMobile);
    const lastDateChecked = localStorage.getItem("dontShowToday");
    const today = new Date().toDateString();
    if (lastDateChecked === today) {
      this.dialogVisible = false;
    } else {
      this.list();
    }
    this.layoutMode = this.$localStorage.get('layoutMode', 'tabs');
    // 初始化激活的标签页
    if (this.filteredNewsSections.length > 0) {
      this.activeTab = this.filteredNewsSections[0].name;
    }
  },
  destroyed() {
    window.removeEventListener("resize", this.checkMobile);
  },
  beforeDestroy() {
    if (this.observer) {
      this.observer.disconnect();
    }
  },
  watch: {
    // 监听 filteredNewsSections 的变化
    filteredNewsSections: {
      immediate: true,
      handler(newSections) {
        if (newSections.length > 0 && !this.activeTab) {
          this.activeTab = newSections[0].name;
        }
      }
    },
    // 监听布局模式变化
    layoutMode: {
      immediate: true,
      handler(newMode) {
        if (newMode === 'tabs' && this.filteredNewsSections.length > 0) {
          this.activeTab = this.filteredNewsSections[0].name;
        }
      }
    }
  },
  methods: {
    list() {
      this.isLoading = true;
      getAiSummarizes()
        .then((response) => {
          this.aiSummarizes = response.data;
          this.$message({
            message: "恭喜，星链链接成功今日热点总结已加载",
            type: "success",
          });
          this.$nextTick(() => {
            this.setupIntersectionObserver();
          });
        })
        .catch((error) => {
          console.error("获取AI摘要失败:", error);
          this.$message.error("太惨了，星链链接失败今日热点总结未加载");
          this.aiSummarizes = [];
        })
        .finally(() => {
          this.isLoading = false;
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
        element.scrollIntoView({ behavior: "smooth" });
      }
    },
    updateLayout(value) {
      this.isTabLayout = value;
      this.$localStorage.set('isTabLayout', value);
    },
    updateLayoutMode(mode) {
      this.layoutMode = mode;
      this.$localStorage.set('layoutMode', mode);
      // 如果切换到标签页布局，确保有一个激活的标签
      if (mode === 'tabs' && this.filteredNewsSections.length > 0) {
        this.activeTab = this.filteredNewsSections[0].name;
      }
    },
    setupIntersectionObserver() {
      // 清除旧的观察者
      if (this.observer) {
        this.observer.disconnect();
      }

      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const index = Number(entry.target.id.split("-")[1]);
              this.activeIndex = index;
            }
          });
        },
        {
          root: this.$refs.newsContainer,
          threshold: 0.5,
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
        window.open(url, "_blank");
      }
    },
    checkMobile() {
      this.isMobile = window.innerWidth <= 1400;
    },
    updateSelectedSites(sites) {
      this.selectedSites = sites;
      this.$localStorage.set("selectedSites", sites);
    },
    updateSitesOrder(orderedSites) {
      // 根据排序后的站点名称重新排序 newsSections
      this.newsSections.sort((a, b) => {
        const indexA = orderedSites.indexOf(a.name);
        const indexB = orderedSites.indexOf(b.name);
        return indexA - indexB;
      });
      // 保存排序到本地存储
      this.$localStorage.set("sitesOrder", orderedSites);
    },
    updateColumnsCount(newColumnsCount) {
      this.columnsCount = newColumnsCount;
      this.$localStorage.set("columnsCount", this.columnsCount);
    },
    updateWrapText(newWrapText) {
      this.wrapText = newWrapText;
      this.$localStorage.set("wrapText", this.wrapText);
    },
    fetchRankList(savedOrder = null) {
      this.loading = true;
      getRankList().then((response) => {
        this.newsSections = response.data.map((item) => {
          const insertTime = moment(item.insert_time, "YYYY-MM-DD HH:mm:ss");
          const subtitle = insertTime.fromNow();
          const now = moment();
          const diffHours = now.diff(insertTime, "hours");
          const type =
            diffHours <= 1 ? "primary" : diffHours <= 4 ? "danger" : "warning";
          return {
            ...item,
            subtitle,
            type,
          };
        });

        const allSiteNames = this.newsSections.map((section) => section.name);
        if (savedOrder) {
          const cleanedOrder = savedOrder.filter((site) =>
            allSiteNames.includes(site)
          );
          const newSites = allSiteNames.filter(
            (site) => !cleanedOrder.includes(site)
          );
          const updatedOrder = [...cleanedOrder, ...newSites];

          this.$localStorage.set("sitesOrder", updatedOrder);

          this.newsSections.sort((a, b) => {
            const indexA = updatedOrder.indexOf(a.name);
            const indexB = updatedOrder.indexOf(b.name);
            return indexA - indexB;
          });
        } else {
          this.$localStorage.set("sitesOrder", allSiteNames);
        }

        if (this.showAllSites) {
          this.selectedSites = allSiteNames;
        } else {
          const savedSelectedSites = this.$localStorage.get(
            "selectedSites",
            []
          );
          this.selectedSites = savedSelectedSites.filter((site) =>
            allSiteNames.includes(site)
          );
          if (this.selectedSites.length === 0) {
            this.selectedSites = allSiteNames;
            this.showAllSites = true;
          }
        }

        this.$localStorage.set("selectedSites", this.selectedSites);
        this.$localStorage.set("showAllSites", this.showAllSites);
        this.loading = false;
        if (this.layoutMode === 'tabs' && this.filteredNewsSections.length > 0) {
          this.activeTab = this.filteredNewsSections[0].name;
        }
      });
    },
    updateShowAllSites(value) {
      this.showAllSites = value;
      this.$localStorage.set("showAllSites", value);
      if (value) {
        this.selectedSites = this.newsSections.map((section) => section.name);
        this.$localStorage.set("selectedSites", this.selectedSites);
      }
    },
    handleUpdate() {
      this.fetchRankList();
    },
  },
};
</script>

<style>
@import "@/styles/themes.css";

/* 基础样式 */
body {
  margin: 0;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

/* 容器布局 */
.app-container {
  min-height: 100vh;
  padding: 16px;
  padding-right: 340px;
}

/* 头部样式 */
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
  gap: 16px;
}

.logo {
  color: var(--text-color);
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-image {
  height: 40px;
  width: auto;
}

/* 主要内容区域 */
.main-content {
  margin-top: 66px;
  padding: 0 16px;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* 新闻摘要对话框 */
::v-deep .news-dialog.el-dialog {
  margin-top: 8vh !important;
}

.dialog-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.dialog-title i {
  color: #409eff;
  margin-right: 8px;
  font-size: 18px;
}

/* 新闻内容区域 */
.dialog-content {
  display: flex;
  position: relative;
}

.dialog-content :deep(.el-loading-mask) {
  background-color: var(--modal-bg);
  opacity: 0.95;
}

.dialog-content :deep(.el-loading-spinner) {
  color: var(--text-color);
}

.dialog-content :deep(.el-loading-text) {
  color: var(--text-color);
  font-size: 14px;
}

[class*="el-loading-parent"] {
  position: relative;
}

.news-container {
  flex: 1;
  max-height: 65vh;
  overflow-y: auto;
  padding: 20px;
  padding-right: 10px;
  background-color: var(--bg-color);
}

.news-nav {
  width: 120px;
  padding: 20px 10px;
  background-color: var(--card-bg);
  border-left: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  height: fit-content;
  max-height: 65vh;
  overflow-y: auto;
}

.nav-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--secondary-text);
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

.nav-item:hover,
.nav-item.active {
  color: #409eff;
  background-color: var(--hover-bg);
}

/* 新闻项样式 */
.news-item {
  background-color: var(--card-bg);
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px var(--border-color);
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
  background-color: var(--hover-bg);
  color: #409eff;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.news-title {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-color);
  line-height: 1.4;
}

.news-content {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--secondary-text);
  text-align: justify;
}

.news-link {
  padding: 4px 0;
  color: #409eff;
  font-size: 13px;
}

.news-link i {
  margin-right: 4px;
}

.news-link:hover {
  color: #66b1ff;
}

/* 移动端样式 */
.mobile-panel-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.mobile-drawer {
  background-color: var(--card-bg) !important;
}

.mobile-drawer :deep(.el-drawer__container) {
  background-color: var(--card-bg) !important;
}

.el-drawer .user-panel {
  position: static;
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}

/* Element UI 组件样式覆盖 */
:deep(.el-dialog__body) {
  padding: 0 !important;
  color: var(--text-color);
}

:deep(.el-dialog__header) {
  padding: 15px 20px !important;
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-dialog__footer) {
  border-top: 1px solid var(--border-color);
  padding: 10px 20px !important;
}

:deep(.el-loading-spinner) {
  color: var(--text-color);
}

:deep(.el-loading-text) {
  color: var(--text-color);
  font-size: 14px;
}

:deep(.el-button--small) {
  padding: 8px 15px;
  font-size: 13px;
}

/* 统一滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--secondary-text);
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .app-container {
    padding-right: 16px;
  }
}

@media (max-width: 768px) {
  [class*="el-col-"] {
    width: 100% !important;
  }

  .logo-search {
    gap: 12px;
  }

  .header-content {
    padding: 0 12px;
  }
}

@media (max-width: 576px) {
  .header {
    height: 50px;
  }

  .main-content {
    padding: 0 12px;
    margin-top: 70px;
  }

  :deep(.el-button--small) {
    padding: 6px 12px;
    font-size: 12px;
  }
}
@media (max-width: 768px) {
  /* 对话框宽度调整 */
  ::v-deep .news-dialog.el-dialog {
    width: 92% !important;
    margin-top: 5vh !important;
  }

  /* 新闻内容和导航布局调整 */
  .dialog-content {
    flex-direction: column;
  }

  .news-container {
    max-height: 50vh;
    padding: 12px;
  }

  .news-nav {
    position: relative;
    width: 100%;
    max-height: 60px;
    padding: 8px;
    border-left: none;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    overflow-x: auto;
    overflow-y: hidden;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
  }

  .nav-item {
    display: inline-block;
    margin: 0 6px;
    padding: 6px 12px;
    background-color: var(--hover-bg);
    border-radius: 16px;
    font-size: 12px;
    flex-shrink: 0;
  }

  /* 新闻项样式优化 */
  .news-item {
    padding: 12px;
    margin-bottom: 8px;
  }

  .news-header {
    flex-direction: column;
    gap: 8px;
  }

  .news-title-group {
    width: 100%;
  }

  .news-title {
    font-size: 14px;
    line-height: 1.4;
  }

  .news-content {
    font-size: 13px;
    line-height: 1.5;
  }

  .news-tag {
    font-size: 11px;
    padding: 1px 6px;
  }
}

/* 小屏幕设备额外优化 */
@media (max-width: 576px) {
  .app-container {
    padding: 12px;
  }

  .main-content {
    margin-top: 60px;
    padding: 0 8px;
  }

  /* 头部样式调整 */
  .header-content {
    padding: 0 8px;
  }

  .logo {
    font-size: 20px;
  }

  /* 新闻导航进一步优化 */
  .news-nav {
    max-height: 50px;
    padding: 6px;
  }

  .nav-item {
    padding: 4px 10px;
    margin: 0 4px;
    font-size: 11px;
  }

  /* 对话框内容调整 */
  .dialog-title {
    font-size: 14px;
  }

  .dialog-title i {
    font-size: 16px;
  }

  /* 滚动条优化 */
  .news-container::-webkit-scrollbar,
  .news-nav::-webkit-scrollbar {
    width: 4px;
    height: 4px;
  }
}

/* 暗色模式下的额外优化 */
@media (prefers-color-scheme: dark) {
  @media (max-width: 768px) {
    .nav-item {
      background-color: rgba(255, 255, 255, 0.05);
    }

    .news-item {
      background-color: rgba(255, 255, 255, 0.03);
    }
  }
}
.news-tabs {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tab-subtitle {
  color: var(--secondary-text);
  font-size: 14px;
}

.tab-news-section {
  height: auto !important;
  background: transparent !important;
  padding: 0 !important;
  box-shadow: none !important;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-tabs__item) {
  color: var(--text-color);
  height: 40px;
  line-height: 40px;
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF;
}

:deep(.el-tabs__active-bar) {
  background-color: #409EFF;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .news-tabs {
    padding: 12px;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 12px;
  }
}
.tab-news-section {
  transition: opacity 0.3s ease;
}
</style>