<template>
  <div class="user-panel">
    <div class="user-info">
      <div class="avatar">
        <span class="avatar-text">无名</span>
      </div>
      <div class="login-tip">{{tip}}</div>
      <div class="online-count">在线人数人数: {{ onlineCount }}</div>
    </div>
    <div class="quote-card">
      <div class="quote-content">
        {{ quoteContent }}
      </div>
      <div class="quote-source">
        {{ quoteSource }}
      </div>
      <countdown-component />
      <calendar-component />
      <horoscope-component />
    </div>
  </div>
</template>

<script>
import {getCopyWriting} from "@/api/rank.js"
import CalendarComponent from '@/components/CalendarComponent.vue';
import HoroscopeComponent from '@/components/HoroscopeComponent.vue';
import CountdownComponent from '@/components/CountdownComponent.vue'

export default {
  name: 'UserPanel',
  components: {
    CalendarComponent,
    HoroscopeComponent,
    CountdownComponent
  },
  data() {
    return {
      tip: "今天也要加油哦！",
      onlineCount: '1082',
      quoteSource: '',
      quoteContent: '',
    }
  },
  created() {
    getCopyWriting().then(response => {
      this.quoteContent = response.data
    }),
    getYellowCalendar().then(response => {
      this.yellowCalendar = response.data
    })
  },
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
  width: 60px;
  height: 60px;
  background-color: #6B9EFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.avatar-text {
  color: #fff;
  font-size: 16px;
}

.login-tip {
  color: #909399;
  font-size: 12px;
  margin-bottom: 8px;
}

.online-count {
  color: #909399;
  font-size: 12px;
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
</style>
