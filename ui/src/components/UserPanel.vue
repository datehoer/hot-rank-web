<template>
  <div class="user-panel">
    <div class="user-info">
      <div class="avatar">
        <img :src="avatar" alt="avatar" />
      </div>
      <span class="username">{{ username }}</span>
      <div class="login-tip">{{ quoteContent }}</div>
      <div class="action-buttons">
        <setting-two class="action-button" title="设置" theme="outline" size="30" :fill="isDarkMode ? '#E5EAF3' : '#303133'" @click="openSettings"/>
        <record-disc class="action-button" title="唱片" theme="two-tone" size="30" :fill="[isDarkMode ? '#E5EAF3' : '#303133', isDarkMode ? '#242424' : '#ffffff']" @click="openMusicPlayer"/>
        <comments class="action-button" title="反馈" theme="two-tone" size="30" :fill="[isDarkMode ? '#E5EAF3' : '#303133', isDarkMode ? '#242424' : '#ffffff']" @click="openFeedback"/>
        <github class="action-button" theme="two-tone" size="30" :fill="isDarkMode ? '#E5EAF3' : '#303133'" @click="goToGitHub"/>
      </div>
    </div>
    <div class="quote-card">
      <countdown-component />
      <calendar-component />
      <horoscope-component />
    </div>

    <!-- 设置弹窗 -->
    <el-dialog
      title="设置"
      :visible.sync="showSettings"
      width="400px"
      custom-class="settings-dialog"
      :modal="false"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础设置" name="basic">
          <div class="settings-item">
            <span>设置列数：{{localColumnsCount}}</span>
            <el-slider
              v-model="localColumnsCount"
              :min="1"
              :max="4"
              :step="1"
              show-stops
            ></el-slider>
          </div>
          <div class="settings-item">
            <div class="switch-wrapper">
              <span>标题超出隐藏：</span>
              <el-switch
                v-model="localWrapText"
                inline-prompt
              />
            </div>
          </div>
          <div class="settings-item">
            <div class="switch-wrapper">
              <span>深色模式：</span>
              <el-switch
                v-model="isDarkMode"
                @change="handleThemeChange"
                inline-prompt
              />
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="热榜设置" name="hotlist">
          <div class="settings-item">
            <div class="switch-wrapper">
              <el-switch
                v-model="localShowAllSites"
                @change="handleShowAllSitesChange"
                active-text="显示所有站点"
              ></el-switch>
              <el-switch
                v-model="selectAll"
                @change="handleSelectAllChange"
                active-text="全选"
                :disabled="localShowAllSites"
              ></el-switch>
            </div>
            <div class="checkbox-group" :class="{ 'disabled': localShowAllSites }">
              <draggable 
                v-model="availableSites"
                :disabled="!dragEnabled || localShowAllSites"
                handle=".drag-handle"
                @end="handleDragEnd"
              >
                <div v-for="site in availableSites" 
                    :key="site.name" 
                    class="site-item"
                >
                  <i class="el-icon-rank drag-handle"></i>
                  <el-checkbox
                    v-model="selectedSites"
                    :label="site.name"
                    :disabled="localShowAllSites"
                  >
                    {{ site.name }}
                  </el-checkbox>
                </div>
              </draggable>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <span slot="footer" class="dialog-footer">
        <el-button @click="closeSettings">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </span>
    </el-dialog>

    <!-- 反馈弹窗 -->
    <el-dialog
      title="反馈"
      :visible.sync="showFeedback"
      width="30%"
      @close="closeFeedback"
      :modal="false"
    >
      <el-form :model="feedback" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="feedback.username" :placeholder="username" required />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="feedback.email" placeholder="example@gmail.com" required />
        </el-form-item>
        <el-form-item label="反馈内容">
          <el-input
            type="textarea"
            v-model="feedback.content"
            placeholder="我希望增加百度热搜榜单"
            required
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="closeFeedback">取消</el-button>
        <el-button type="primary" @click="submitFeedback">提交</el-button>
      </span>
    </el-dialog>
    <el-dialog
      width="100%"
      :before-close="handleClose"
      :visible.sync="showMusicPlayer"
      :modal="false"
      custom-class="music-player-dialog"
      :fullscreen="isMobile"
      :append-to-body="true"
    >
      <music-player />
    </el-dialog>
  </div>
</template>

<script>
import draggable from 'vuedraggable'
import { getCopyWriting, getAvatar, getUsername, postFeedback, getCards } from "@/api/rank.js";
import CalendarComponent from '@/components/CalendarComponent.vue';
import HoroscopeComponent from '@/components/HoroscopeComponent.vue';
import CountdownComponent from '@/components/CountdownComponent.vue';
import MusicPlayer from '@/components/Player.vue'
import {SettingTwo, RecordDisc, Comments, Github} from '@icon-park/vue';
export default {
  name: 'UserPanel',
  components: {
    CalendarComponent,
    HoroscopeComponent,
    CountdownComponent,
    MusicPlayer,
    draggable,
    SettingTwo,
    RecordDisc,
    Comments,
    Github
  },
  props: {
    columnsCount: {
      type: Number,
      default: 3
    },
    showAllSites: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isSpinning: false,
      rotation: 0,
      intervalId: null,
      activeTab: 'basic',
      availableSites: [],
      selectedSites: [],
      tip: "今天也要加油哦！",
      quoteContent: '',
      avatar: '',
      username: '',
      // 状态控制
      showSettings: false,
      showFeedback: false,
      showMusicPlayer: false,
      // 设置表单
      settings: {
        color: '#FFFFFF',
        username: ''
      },
      // 反馈表单
      feedback: {
        username: '',
        email: '',
        content: ''
      },
      localColumnsCount: this.columnsCount,
      localWrapText: true,
      dragEnabled: true,
      localShowAllSites: this.showAllSites,
      selectAll: false,
      isDarkMode: true,
      isMobile: false,
    }
  },
  watch: {
    showAllSites: {
      immediate: true,
      handler(newVal) {
        this.localShowAllSites = newVal;
      }
    },
    selectedSites: {
      handler(newVal) {
        // 当选中的站点数量等于可用站点数量时，设置全选状态为true
        this.selectAll = newVal.length === this.availableSites.length;
      },
      deep: true
    }
  },
  computed: {
    transformStyle() {
      return {
        transform: `rotate(${this.rotation}deg)`,
      };
    },
  },
  created() {
    getCopyWriting().then(response => {
      this.quoteContent = response.data;
    });
    getAvatar().then(response => {
      this.avatar = response.data;
    });
    getUsername().then(response => {
      this.username = response.data;
      this.settings.username = response.data; // 初始化设中的用户名
    });
    this.selectedSites = this.$localStorage.get('selectedSites', []);
    this.fetchCards();
    const savedShowAllSites = this.$localStorage.get('showAllSites');
    if (savedShowAllSites !== null) {
      this.localShowAllSites = savedShowAllSites;
      this.$emit('update-show-all-sites', savedShowAllSites);
    }
    this.isDarkMode = this.$localStorage.get('isDarkMode', true);
    this.applyTheme(this.isDarkMode);
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile);
  },
  beforeDestroy() {
    // 清除定时器
    window.removeEventListener('resize', this.checkMobile);
    clearInterval(this.intervalId);
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },
    handleSelectAllChange(value) {
      if (value) {
        // 全选
        this.selectedSites = this.availableSites.map(site => site.name);
      } else {
        // 取消全选
        this.selectedSites = [];
      }
    },
    handleDragEnd() {
      const orderedSites = this.availableSites.map(site => {
        if (this.selectedSites.includes(site.name)) {
          return site.name;
        }
      }).filter(site => site !== undefined);
      this.$emit('update-sites-order', orderedSites);
      this.$localStorage.set('sitesOrder', orderedSites);
    },
    openMusicPlayer(){
      this.showMusicPlayer = true;
    },
    handleThemeChange(value) {
      this.isDarkMode = value;
      this.$localStorage.set('isDarkMode', value);
      this.applyTheme(value);
    },
    applyTheme(isDark) {
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    },
    toggleSpin() {
      if (this.isSpinning) {
        // 停止旋转
        clearInterval(this.intervalId);
        this.intervalId = null;
        this.isSpinning = false;
      } else {
        // 开始旋转
        this.isSpinning = true;
        this.intervalId = setInterval(() => {
          this.rotation = (this.rotation + 5) % 360;
        }, 16);
      }
    },
    fetchCards() {
      getCards().then(response => {
        this.availableSites = response.data;
      });
    },
    handleClose(done) {
      this.$confirm('暂时关闭音乐播放器界面？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
        customClass: 'music-player-close-dialog',
        center: true,
        showClose: false
      }).then(() => {
        done();
      }).catch(() => {});
    },
    openSettings() {
      this.showSettings = true;
    },
    closeSettings() {
      this.showSettings = false;
    },
    handleShowAllSitesChange(value) {
      this.localShowAllSites = value;
      this.$emit('update-show-all-sites', value);
      this.$localStorage.set('showAllSites', value);
      if (value) {
        const allSites = this.availableSites.map(site => site.name);
        this.selectedSites = allSites;
        this.$emit('update-selected-sites', allSites);
        this.$localStorage.set('selectedSites', allSites);
      }
    },
    saveSettings() {
      this.$emit('update-columns-count', this.localColumnsCount);
      this.$emit('update-wrap-text', this.localWrapText);
      this.$emit('update-selected-sites', this.selectedSites);
      this.$emit('update-show-all-sites', this.localShowAllSites);
      this.$localStorage.set('selectedSites', this.selectedSites);
      this.handleDragEnd();
      this.closeSettings();
    },
    openFeedback() {
      this.showFeedback = true;
    },
    closeFeedback() {
      this.showFeedback = false;
    },
    submitFeedback() {
      if (!this.feedback.username || !this.feedback.email || !this.feedback.content) {
        alert('请填写所有必填项');
        return;
      }
      this.feedback.subject = `${this.feedback.username}的反馈`;
      this.feedback.content = this.feedback.content.trim() + `\n\n邮箱：${this.feedback.email}`;
      postFeedback(this.feedback).then(response => {
        alert('反馈已提交，谢谢！');
      });
      this.closeFeedback();
      this.feedback = {
        username: '',
        email: '',
        content: ''
      };
    },
    goToGitHub() {
      window.open('https://github.com/datehoer/hot-rank-web', '_blank');
    }
  }
}
</script>

<style scoped>
/* 基础布局 */
.user-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  width: 350px;
}

/* 用户信息区域 */
.user-info {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 20px;
  text-align: center;
  margin-bottom: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  background-color: var(--card-bg);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  position: relative;
  overflow: hidden;
  box-shadow: 0px 4px 8px var(--border-color);
  border: 2px solid var(--border-color);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.username {
  font-size: 16px;
  text-align: center;
}

.login-tip {
  color: var(--secondary-text);
  font-size: 12px;
  margin-top: 8px;
  margin-bottom: 8px;
}

/* 动作按钮 */
.action-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
  color: var(--text-color);
}

.action-button {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  outline: none;
  transition: transform 0.3s;
  fill: var(--text-color) !important;
}

.action-button:hover {
  transform: scale(1.2);
}

/* 引用卡片 */
.quote-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
  overflow-y: auto;
  padding-right: 8px;
  height: 500px;
}

/* 通用滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-color);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-thumb);
  border-radius: 3px;
  transition: background-color 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background-color: var(--secondary-text);
}

/* 设置对话框样式 */
.settings-dialog {
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.settings-item {
  margin-bottom: 20px;
}

.settings-item span {
  display: block;
  margin-bottom: 8px;
  color: var(--text-color);
}

.switch-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 8px 0;
}

.checkbox-group.disabled {
  opacity: 0.6;
  pointer-events: none;
}

/* 站点项样式 */
.site-item {
  display: flex;
  align-items: center;
  padding: 8px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  margin-bottom: 8px;
}

.site-item:hover {
  background: var(--hover-bg);
}

.drag-handle {
  cursor: move;
  color: var(--secondary-text);
  margin-right: 12px;
  font-size: 16px;
}

.drag-handle:hover {
  color: var(--text-color);
}

/* 拖拽状态 */
.sortable-ghost {
  opacity: 0.5;
  background: var(--hover-bg) !important;
}

.sortable-drag {
  background: var(--card-bg) !important;
}

/* Element UI 组件样式覆盖 */
:deep(.el-dialog) {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 20px;
}

:deep(.el-dialog__body) {
  padding: 20px;
  color: var(--text-color);
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
  border-top: 1px solid var(--border-color);
}

:deep(.el-dialog__title) {
  color: var(--text-color);
  font-size: 18px;
  line-height: 24px;
}

/* 表单元素样式 */
:deep(.el-form-item__label) {
  color: var(--text-color);
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-input__inner:hover),
:deep(.el-textarea__inner:hover),
:deep(.el-input__inner:focus),
:deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
}

:deep(.el-input__inner:focus),
:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

:deep(.el-input__inner::placeholder),
:deep(.el-textarea__inner::placeholder) {
  color: var(--secondary-text);
}

/* 禁用状态 */
:deep(.el-input.is-disabled .el-input__inner) {
  background-color: var(--hover-bg);
  border-color: var(--border-color);
  color: var(--secondary-text);
}

/* 标签页样式 */
:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-color);
}

:deep(.el-tabs__item) {
  color: var(--secondary-text);
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF !important;
}

/* 开关和复选框 */
:deep(.el-switch__core) {
  background-color: var(--border-color) !important;
}

:deep(.el-switch.is-checked .el-switch__core) {
  background-color: #409EFF !important;
}

:deep(.el-checkbox) {
  color: var(--text-color);
  margin-right: 0;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #409EFF;
}

/* 按钮样式 */
:deep(.el-button) {
  background-color: var(--card-bg);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-button:hover) {
  background-color: var(--hover-bg);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.el-button--primary) {
  background-color: #409EFF;
  border-color: #409EFF;
  color: #ffffff;
}

:deep(.el-button--primary:hover) {
  background-color: #66b1ff;
  border-color: #66b1ff;
  color: #ffffff;
}

/* 动画 */
.spinning {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media screen and (max-width: 768px) {
  :deep(.music-player-dialog) {
    width: 100% !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0;
  }
  
  :deep(.music-player-dialog .el-dialog__header) {
    padding: 10px;
  }
  
  :deep(.music-player-dialog .el-dialog__body) {
    height: calc(100vh - 96px); /* 减去header和footer的高度 */
    overflow-y: auto;
  }
}

:deep(.music-player-dialog .el-dialog__header) {
  padding: 10px;
  position: relative;
}

/* 关闭按钮样式 */
:deep(.music-player-dialog .el-dialog__headerbtn) {
  position: absolute;
  right: 10px;
  top: 10px;
  z-index: 100;
  width: 24px;
  height: 24px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.music-player-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: #fff;
  font-weight: bold;
}

:deep(.music-player-dialog .el-dialog__headerbtn:hover) {
  background: rgba(0, 0, 0, 0.5);
}

/* 确认关闭对话框样式 */
:deep(.music-player-close-dialog) {
  background: var(--card-bg);
  border-radius: 8px;
  max-width: 300px;
}

:deep(.music-player-close-dialog .el-message-box__header) {
  padding: 15px;
  background: transparent;
}

:deep(.music-player-close-dialog .el-message-box__title) {
  color: var(--text-color);
  font-size: 16px;
}

:deep(.music-player-close-dialog .el-message-box__content) {
  padding: 15px;
  color: var(--text-color);
  font-size: 14px;
}

:deep(.music-player-close-dialog .el-message-box__btns) {
  padding: 10px 15px;
}

:deep(.music-player-close-dialog .el-button) {
  font-size: 13px;
  padding: 8px 16px;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  :deep(.music-player-dialog .el-dialog__headerbtn) {
    right: 15px;
    top: 15px;
  }

  :deep(.music-player-close-dialog) {
    width: 90% !important;
  }
}
</style>
