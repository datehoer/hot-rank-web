<template>
  <div class="countdown-info">
    <div class="info-row">
      <span class="info-label">距离下一个节假日：</span>
      <span class="info-value">{{ nextHolidayText }}</span>
    </div>
    
    <div class="info-row">
      <span class="info-label">距离周末：</span>
      <span class="info-value">{{ weekendCountdown }}</span>
    </div>
    
    <div class="info-row">
      <span class="info-label">距离{{ nextYear }}年：</span>
      <span class="info-value">{{ nextYearCountdown }}</span>
    </div>
  </div>
</template>

<script>
import moment from 'moment'
import { getHolidays } from "@/api/rank.js";

export default {
  name: 'CountdownComponent',
  data() {
    return {
      holidays: [
        { holiday_name: '元旦', date: '2025-01-01' },
        { holiday_name: '劳动节', date: '2025-05-01' },
        { holiday_name: '国庆节', date: '2024-10-01' },
      ],
      timer: null
    }
  },
  computed: {
    nextYear() {
      return moment().year() + 1
    },
    nextHolidayText() {
      const today = moment()
      let nextHoliday = null
      let minDays = Infinity

      this.holidays.forEach(holiday => {
        const holidayDate = moment(holiday.date)
        const days = holidayDate.diff(today, 'days')
        
        if (days >= 0 && days < minDays) {
          minDays = days
          nextHoliday = holiday
        }
      })

      if (!nextHoliday) {
        return '暂无节假日信息'
      }

      return `${nextHoliday.holiday_name}还有${minDays}天`
    },
    weekendCountdown() {
      const today = moment()
      const currentDay = today.day() // 0是周日，6是周六
      
      if (currentDay === 0 || currentDay === 6) {
        return '今天就是周末'
      }
      
      const daysToWeekend = 5 - currentDay
      if (daysToWeekend === 0) {
        return '明天就是周末了，加油！'
      }
      return `还有${daysToWeekend}天`
    },
    nextYearCountdown() {
      const today = moment()
      const nextYear = moment().year(today.year() + 1).startOf('year')
      const days = nextYear.diff(today, 'days')
      return `还有${days}天`
    }
  },
  created() {
    this.listHoliday()
  },
  methods: {
    updateCountdowns() {
      // 强制更新计算属性
      this.$forceUpdate()
    },
    listHoliday(){
      getHolidays().then(response => {
        this.holidays = response.data
      }).catch(error => {
        console.error('获取节假日信息失败', error)
      })
    }
  },
  mounted() {
    // 每分钟更新一次倒计时
    this.timer = setInterval(this.updateCountdowns, 60000)
  },
  beforeDestroy() {
    // 清理定时器
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
  }
}
</script>

<style scoped>
.countdown-info {
  padding: 12px;
  color: #e5eaf3;
  font-size: 14px;
}

.info-row {
  margin-bottom: 8px;
  line-height: 1.5;
}

.info-label {
  color: #409EFF;
  display: inline-block;
  margin-right: 8px;
}

.info-value {
  color: var(--text-color);
}
</style>