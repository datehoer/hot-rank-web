<template>
  <div class="horoscope-info">
      <div class="info-row">
        <span class="info-label">日期：</span>
        <span class="info-value">{{ yellowCalendar.gregorian_calendar }}</span>
      </div>

      <div class="info-row">
        <span class="info-label">农历日期：</span>
        <span class="info-value">{{ yellowCalendar.lunar_calendar }}</span>
      </div>

      
      <div class="info-row">
        <span class="info-label">今日宜：</span>
        <span class="info-value">{{ yellowCalendar.good_actions.join('、') }}</span>
      </div>
      
      <div class="info-row">
        <span class="info-label">今日忌：</span>
        <span class="info-value">{{ yellowCalendar.bad_actions.join('、') }}</span>
      </div>
  </div>
</template>

<script>
import { getYellowCalendar } from "@/api/rank.js";

export default {
  name: 'HoroscopeComponent',
  data() {
    return {
      yellowCalendar: {
        gregorian_calendar: "",
        lunar_calendar: "",
        good_actions: [],
        bad_actions: [],
      },
      showMore: false // 默认关闭
    };
  },
  created() {
    this.fetchYellowCalendar();
  },
  methods: {
    fetchYellowCalendar() {
      getYellowCalendar().then(response => {
        if (response.data) {
          this.yellowCalendar = response.data;
        }
      }).catch(error => {
        console.error("获取黄历数据失败:", error);
      });
    }
  }
};
</script>

<style scoped>
.horoscope-info {
  position: relative;
  padding: 16px;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-size: 14px;
  border-radius: 8px;
  max-width: 800px;
  margin: 0 auto;
}

.toggle-switch {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  margin-right: 8px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #1abc9c;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}

.toggle-label {
  font-size: 14px;
  color: var(--text-color);
}

.base-info, .more-info {
  margin-top: 40px; /* 给开关按钮留出空间 */
}

.info-section {
  margin-bottom: 12px;
  padding: 12px;
  background-color: var(--bg-color);
  border-radius: 6px;
}

.section-title {
  margin-bottom: 8px;
  font-size: 16px;
  color: #1abc9c;
  border-bottom: 1px solid #1abc9c;
  padding-bottom: 4px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.info-label {
  width: 120px;
  font-weight: bold;
  color: #3498db;
}

.info-value {
  flex: 1;
}

.info-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}

a.info-value {
  color: #1abc9c;
  text-decoration: none;
}

a.info-value:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .info-label {
    width: 100px;
    font-size: 13px;
  }
  
  .toggle-switch {
    flex-direction: column;
    align-items: flex-end;
  }
  
  .toggle-label {
    font-size: 12px;
  }
}
</style>
