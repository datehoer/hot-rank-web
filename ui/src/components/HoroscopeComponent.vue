<template>
  <div class="horoscope-info">
    <div class="info-section">
      <div class="info-row" v-for="item in yellowCalendar.horoscope_data" :key="item.hit">
        <template v-if="item.hit === '年' || item.hit === '月' || item.hit === '日'">
          <span class="info-label">{{ item.hit }}：</span>
          <span class="info-value">{{ item.gz }} {{ item.zodiac }} {{ item.nayin }}</span>
        </template>
      </div>
    </div>
    
    <div class="info-row" v-if="yellowCalendar.yi_list?.length">
      <span class="info-label">今日宜：</span>
      <span class="info-value">{{ yellowCalendar.yi_list.join('、') }}</span>
    </div>
    <div class="info-row" v-if="yellowCalendar.ji_list?.length">
      <span class="info-label">今日忌：</span>
      <span class="info-value">{{ yellowCalendar.ji_list.join('、') }}</span>
    </div>
    <div class="info-row" v-if="yellowCalendar.jishen?.length">
      <span class="info-label">神煞：</span>
      <span class="info-value">{{ yellowCalendar.jishen.join('、') }}</span>
    </div>
    
    <div class="info-row" v-if="yellowCalendar.pengzu_baiji">
      <span class="info-label">彭祖百忌：</span>
      <span class="info-value">{{ yellowCalendar.pengzu_baiji }}</span>
    </div>
    
    <div class="info-row" v-if="yellowCalendar.xiang_chong">
      <span class="info-label">相冲：</span>
      <span class="info-value">{{ yellowCalendar.xiang_chong }}</span>
    </div>
    
    <div class="info-section">
      <div class="info-row" v-for="item in yellowCalendar.yue_data" :key="item.title">
        <span class="info-label">{{ item.title }}：</span>
        <span class="info-value">{{ item.text }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import {getYellowCalendar} from "@/api/rank.js"

export default {
  name: 'HoroscopeComponent',
  data() {
    return {
      yellowCalendar: {
        horoscope_data: [],
        yi_list: [],
        ji_list: [],
        jishen: [],
        pengzu_baiji: '',
        xiang_chong: '',
        yue_data: []
      }
    }
  },
  created() {
    getYellowCalendar().then(response => {
      this.yellowCalendar = response.data
    })
  }
}
</script>

<style scoped>
.horoscope-info {
  padding: 12px;
  color: #e5eaf3;
  font-size: 14px;
}

.info-section {
  margin-bottom: 3px;
}

.info-row {
  margin-bottom: 3px;
  line-height: 1.5;
}

.info-label {
  color: #409EFF;
  display: inline-block;
  margin-right: 8px;
}

.info-value {
  color: #e5eaf3;
}
</style>