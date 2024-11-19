<template>
  <div class="horoscope-info">
    <!-- 切换开关按钮 -->
    <div class="toggle-switch">
      <label class="switch">
        <input type="checkbox" v-model="showMore">
        <span class="slider round"></span>
      </label>
      <span class="toggle-label">{{ showMore ? '显示更多' : '显示基本' }}</span>
    </div>

    <!-- 基础信息部分 -->
    <div class="base-info">
      <!-- 中心备注 -->
      <div class="info-row">
        <img :src="yellowCalendar.center_note.img" alt="备注" class="info-icon" />
        <span class="info-value">{{ yellowCalendar.center_note.text }}</span>
      </div>

      <!-- 日期选择器 -->
      <div class="info-row">
        <span class="info-label">日期：</span>
        <span class="info-value">{{ yellowCalendar.center_datepicker }}</span>
      </div>

      <!-- 农历日期 -->
      <div class="info-row">
        <span class="info-label">农历日期：</span>
        <span class="info-value">{{ yellowCalendar.center_lunar_date }}</span>
      </div>
      
      <!-- 今日星座 -->
      <div class="info-row">
        <span class="info-label">今日星座：</span>
        <span class="info-value">{{ yellowCalendar.center_today_constellation.constellation }}</span>
      </div>
      
      <!-- 今日宜 -->
      <div class="info-row">
        <span class="info-label">今日宜：</span>
        <span class="info-value">{{ yellowCalendar.left_yi_ji.join('、') }}</span>
      </div>
      
      <!-- 今日忌 -->
      <div class="info-row">
        <span class="info-label">今日忌：</span>
        <span class="info-value">{{ yellowCalendar.right_yi_ji.join('、') }}</span>
      </div>
    </div>
    
    <!-- 更多信息部分 -->
    <div v-if="showMore" class="more-info">
      <!-- 左侧星座数据 -->
      <div class="info-section">
        <h3 class="section-title">星座信息</h3>
        <div class="info-row" v-for="item in yellowCalendar.left_horoscopes" :key="item.hit">
          <span class="info-label">{{ item.hit }}：</span>
          <span class="info-value">{{ item.gz }} {{ item.zodiac }} {{ item.nayin }}</span>
        </div>
      </div>
      
      <!-- 左侧宜忌 -->
      <div class="info-section">
        <h3 class="section-title">宜忌</h3>
        <div class="info-row">
          <span class="info-label">吉神宜趋：</span>
          <span class="info-value">{{ yellowCalendar.left_shen_sha.content }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">凶煞宜忌：</span>
          <span class="info-value">{{ yellowCalendar.right_shen_sha.content }}</span>
        </div>
      </div>
      
      <!-- 左侧彭祖百忌 -->
      <div class="info-section">
        <h3 class="section-title">彭祖百忌</h3>
        <div class="info-row">
          <span class="info-label">彭祖百忌：</span>
          <span class="info-value">{{ yellowCalendar.left_pz_chong["彭祖百忌"] }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">相冲：</span>
          <span class="info-value">{{ yellowCalendar.left_pz_chong.xiang_chong }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">本月胎神：</span>
          <span class="info-value">{{ yellowCalendar.right_pz_chong["本月胎神"] }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">今日胎神：</span>
          <span class="info-value">{{ yellowCalendar.right_pz_chong["今日胎神"] }}</span>
        </div>
      </div>
      
      <!-- 左侧物候信息 -->
      <div class="info-section">
        <h3 class="section-title">物候信息</h3>
        <div class="info-row" v-for="item in yellowCalendar.left_yz_wh_yx" :key="item.title">
          <span class="info-label">{{ item.title }}：</span>
          <span class="info-value">{{ item.text }}</span>
        </div>
      </div>
      
      <!-- 底部财神信息 -->
      <div class="info-section">
        <h3 class="section-title">财神信息</h3>
        <div class="info-row" v-for="item in yellowCalendar.bottom_caishen" :key="item.title">
          <span class="info-label">{{ item.title }}：</span>
          <a :href="item.link" class="info-value">{{ item.text }}</a>
        </div>
      </div>
      
      <!-- 底部阴阳贵神信息 -->
      <div class="info-section">
        <h3 class="section-title">阴阳贵神</h3>
        <div class="info-row" v-for="item in yellowCalendar.bottom_yinyang_guishen" :key="item.title">
          <span class="info-label">{{ item.title }}：</span>
          <span class="info-value">{{ item.text }}</span>
        </div>
      </div>
      
      <!-- 底部空亡梓信息 -->
      <div class="info-section">
        <h3 class="section-title">空亡梓</h3>
        <div class="info-row" v-for="item in yellowCalendar.bottom_kongwang_souzhi" :key="item.title">
          <span class="info-label">{{ item.title }}：</span>
          <span class="info-value">{{ item.text }}</span>
        </div>
      </div>
      
      <!-- 底部九宫飞星信息 -->
      <div class="info-section">
        <h3 class="section-title">九宫飞星</h3>
        <div class="info-row" v-for="(item, index) in yellowCalendar.bottom_jiugong_feixing" :key="index">
          <span class="info-label">飞星{{ index + 1 }}：</span>
          <span class="info-value">{{ item }}</span>
        </div>
      </div>
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
        left_horoscopes: [],
        left_yi_ji: [],
        left_shen_sha: {},
        left_pz_chong: {},
        left_yz_wh_yx: [],
        right_horoscopes: [],
        right_yi_ji: [],
        right_shen_sha: {},
        right_pz_chong: {},
        right_yz_wh_yx: [],
        center_note: {},
        center_lunar_date: '',
        center_today_constellation: {},
        center_datepicker: '',
        bottom_caishen: [],
        bottom_yinyang_guishen: [],
        bottom_kongwang_souzhi: [],
        bottom_jiugong_feixing: []
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
