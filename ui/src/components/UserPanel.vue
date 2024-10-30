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
        <div class="settings-item">
          <label>设置列数：{{localColumnsCount}}</label>
          <el-slider
            v-model="localColumnsCount"
            :min="1"
            :max="4"
            :step="1"
            show-stops
          ></el-slider>
        </div>
        <!-- <label>
          颜色:
          <input type="color" v-model="settings.color" />
        </label>
        <label>
          用户名:
          <input type="text" v-model="settings.username" />
        </label> -->
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
  </div>
</template>

<script>
import { getCopyWriting, getAvatar, getUsername, postFeedback } from "@/api/rank.js";
import CalendarComponent from '@/components/CalendarComponent.vue';
import HoroscopeComponent from '@/components/HoroscopeComponent.vue';
import CountdownComponent from '@/components/CountdownComponent.vue';

export default {
  name: 'UserPanel',
  components: {
    CalendarComponent,
    HoroscopeComponent,
    CountdownComponent
  },
  props: {
    columnsCount: {
      type: Number,
      default: 3
    }
  },
  data() {
    return {
      tip: "今天也要加油哦！",
      quoteContent: '',
      avatar: '',
      username: '',
      // 状态控制
      showSettings: false,
      showFeedback: false,
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
    }
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
      this.settings.username = response.data; // 初始化设置中的用户名
    });
  },
  methods: {
    openSettings() {
      this.showSettings = true;
    },
    closeSettings() {
      this.showSettings = false;
    },
    saveSettings() {
      this.$emit('update-columns-count', this.localColumnsCount);
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
  width: 300px;
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
  width: 30px;
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
  background: #333;
  padding: 20px;
  border-radius: 5px;
  width: 300px;
}

.modal h3 {
  margin-top: 0;
}

.modal label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
}

.modal input,
.modal textarea {
  width: 100%;
  padding: 6px;
  margin-top: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-actions button:first-child {
  background-color: #4CAF50;
  color: white;
}

.modal-actions button:last-child {
  background-color: #f44336;
  color: white;
}
</style>
