<template>
  <div class="user-panel">
    <div class="user-info">
      <div class="avatar">
        <img :src="avatar" alt="avatar" />
      </div>
      <span class="username">{{ username }}</span>
      <div class="login-tip">{{ quoteContent }}</div>
      <div class="action-buttons">
        <button class="action-button" @click="openSettings">
          <i class="icon-settings"></i>
          <span class="tooltip">设置</span>
        </button>
        <div
          class="record"
          @click="openMusicPlayer"
          title="唱片"
        ></div>
        <button class="action-button" @click="openFeedback">
          <i class="icon-feedback"></i>
          <span class="tooltip">反馈</span>
        </button>
        <button class="action-button" @click="goToGitHub">
          <i class="icon-github"></i>
          <span class="tooltip">GitHub</span>
        </button>
      </div>
    </div>
    <div class="quote-card">
      <countdown-component />
      <calendar-component />
      <horoscope-component />
    </div>

    <!-- 设置弹窗 -->
    <div v-if="showSettings" class="modal-overlay" @click.self="closeSettings">
      <div class="modal">
        <h3>设置</h3>
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
                  :active-text="'换行'"
                  :inactive-text="'不换行'"
                />
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="热榜设置" name="hotlist">
            <div class="settings-item">
              <div class="checkbox-group">
                <el-checkbox
                  v-for="site in availableSites"
                  :key="site.name"
                  v-model="selectedSites"
                  :label="site.name"
                >
                  {{ site.name }}
                </el-checkbox>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        <div class="modal-actions">
          <button @click="saveSettings">保存</button>
          <button @click="closeSettings">取消</button>
        </div>
      </div>
    </div>

    <!-- 反馈弹窗 -->
    <div v-if="showFeedback" class="modal-overlay" @click.self="closeFeedback">
      <div class="modal">
        <h3>反馈</h3>
        <label>
          用户名:
          <input type="text" v-model="feedback.username" :placeholder="username" required/>
        </label>
        <label>
          邮箱:
          <input type="email" v-model="feedback.email" placeholder="example@gmail.com" required/>
        </label>
        <label>
          反馈内容:
          <textarea v-model="feedback.content" placeholder="我希望增加百度热搜榜单" required></textarea>
        </label>
        <div class="modal-actions">
          <button @click="submitFeedback">提交</button>
          <button @click="closeFeedback">取消</button>
        </div>
      </div>
    </div>
    <el-dialog
      width="35%"
      :before-close="handleClose"
      :visible.sync="showMusicPlayer"
      :modal="false"
      custom-class="music-player-dialog"
    >
      <music-player />
    </el-dialog>
  </div>
</template>

<script>
import { getCopyWriting, getAvatar, getUsername, postFeedback, getCards } from "@/api/rank.js";
import CalendarComponent from '@/components/CalendarComponent.vue';
import HoroscopeComponent from '@/components/HoroscopeComponent.vue';
import CountdownComponent from '@/components/CountdownComponent.vue';
import MusicPlayer from '@/components/Player.vue'

export default {
  name: 'UserPanel',
  components: {
    CalendarComponent,
    HoroscopeComponent,
    CountdownComponent,
    MusicPlayer
  },
  props: {
    columnsCount: {
      type: Number,
      default: 3
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
    this.selectedSites = this.$localStorage.get('selectedSites', ['*']);
    this.fetchCards();
  },
  beforeDestroy() {
    // 清除定时器
    clearInterval(this.intervalId);
  },
  methods: {
    openMusicPlayer(){
      this.showMusicPlayer = true;
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
      this.$confirm('确认关闭音乐播放器？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'music-player-close-dialog',
        center: true
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
    saveSettings() {
      this.$emit('update-columns-count', this.localColumnsCount);
      this.$emit('update-wrap-text', this.localWrapText);
      this.$emit('update-selected-sites', this.selectedSites);
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
.user-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  width: 350px;
}

.user-info {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 20px;
  text-align: center;
  margin-bottom: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  background-color: #6B9EFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  position: relative;
  overflow: hidden;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid #fff;
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
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
  margin-bottom: 8px;
}

.action-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
}

.action-button {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  outline: none;
  transition: transform 0.3s;
}

.action-button:hover {
  transform: scale(1.2);
}

.tooltip {
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #333;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
  width: 40px;
  text-align: center;
}

.action-button:hover .tooltip {
  opacity: 1;
}

.icon-settings::before {
  content: '⚙️';
  font-size: 20px;
}

.icon-feedback::before {
  content: '💬';
  font-size: 20px;
}

.icon-github::before {
  content: '🐱';
  font-size: 20px;
}

.quote-card {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 16px;
  overflow-y: auto;
  padding-right: 8px;
  height: 500px;
}

/* 自定义滚动条样式 */
.quote-card::-webkit-scrollbar {
  width: 8px;
}

.quote-card::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.quote-card::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  transition: background-color 0.3s;
}

.quote-card::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.quote-content {
  color: #E5EAF3;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.quote-source {
  color: #909399;
  font-size: 12px;
  text-align: right;
}

/* 模态弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #2b2b2b;
  padding: 24px;
  border-radius: 8px;
  width: 400px;
  height: 500px;
  color: #E5EAF3;
  display: flex;
  flex-direction: column;
}

.modal h3 {
  margin: 0 0 20px 0;
  color: #E5EAF3;
  font-size: 18px;
  flex-shrink: 0;
}

:deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  height: 300px;
}

:deep(.el-tabs__content)::-webkit-scrollbar {
  width: 6px;
}

:deep(.el-tabs__content)::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

:deep(.el-tabs__content)::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

:deep(.el-tabs__content)::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.settings-item {
  margin-bottom: 20px;
}

.settings-item span {
  display: block;
  margin-bottom: 8px;
  color: #E5EAF3;
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

/* Element Plus 件样式覆盖 */
:deep(.el-tabs__item) {
  color: #909399 !important;
  font-size: 14px;
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF !important;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.05);
}

:deep(.el-checkbox) {
  color: #E5EAF3;
  margin-right: 0;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #409EFF;
}

:deep(.el-slider__runway) {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-slider__bar) {
  background-color: #409EFF;
}

:deep(.el-slider__button) {
  border-color: #409EFF;
}

.modal-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

.modal-actions button {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.modal-actions button:first-child {
  background-color: #409EFF;
  color: white;
}

.modal-actions button:first-child:hover {
  background-color: #66b1ff;
}

.modal-actions button:last-child {
  background-color: #909399;
  color: white;
}

.modal-actions button:last-child:hover {
  background-color: #a6a9ad;
}

:deep(.el-switch__core) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-switch.is-checked .el-switch__core) {
  background-color: #409EFF !important;
}

:deep(.el-tabs__header) {
  flex-shrink: 0;
  margin-bottom: 16px;
}

.record {
  width: 40px;
  height: 40px;
  background-image: url('https://oss.datehoer.com/default-images/cartoondisc_1.png'); /* 请替换为您的唱片图片路径 */
  background-size: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.1s linear;
}

.spinning {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 添加音乐播放器弹窗样式 */
:deep(.music-player-dialog) {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: none;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

:deep(.music-player-dialog .el-dialog__header) {
  padding: 0;
}

:deep(.music-player-dialog .el-dialog__body) {
  padding: 0;
  background: transparent;
  color: #E5EAF3;
}

:deep(.music-player-dialog .el-dialog__headerbtn) {
  top: 8px;
  right: 8px;
}

:deep(.music-player-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: #909399;
}

:deep(.music-player-dialog .el-dialog__headerbtn:hover .el-dialog__close) {
  color: #E5EAF3;
}

/* 音乐播放器关闭确认框样式 */
:deep(.music-player-close-dialog) {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: none;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

:deep(.music-player-close-dialog .el-message-box__header) {
  padding: 20px 20px 10px;
  background: transparent;
}

:deep(.music-player-close-dialog .el-message-box__title) {
  color: #E5EAF3;
  font-size: 16px;
}

:deep(.music-player-close-dialog .el-message-box__content) {
  padding: 10px 20px;
  background: transparent;
  color: #909399;
}

:deep(.music-player-close-dialog .el-message-box__btns) {
  padding: 10px 20px 20px;
  background: transparent;
}

:deep(.music-player-close-dialog .el-message-box__btns button) {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

:deep(.music-player-close-dialog .el-message-box__btns button:first-child) {
  background-color: #909399;
  color: white;
  margin-right: 10px;
}

:deep(.music-player-close-dialog .el-message-box__btns button:first-child:hover) {
  background-color: #a6a9ad;
}

:deep(.music-player-close-dialog .el-message-box__btns button:last-child) {
  background-color: #409EFF;
  color: white;
}

:deep(.music-player-close-dialog .el-message-box__btns button:last-child:hover) {
  background-color: #66b1ff;
}

:deep(.music-player-close-dialog .el-message-box__status) {
  color: #E6A23C;
  font-size: 20px;
}

:deep(.music-player-close-dialog .el-message-box__close) {
  color: #909399;
  font-size: 16px;
  top: 15px;
  right: 15px;
}

:deep(.music-player-close-dialog .el-message-box__close:hover) {
  color: #E5EAF3;
}
</style>
