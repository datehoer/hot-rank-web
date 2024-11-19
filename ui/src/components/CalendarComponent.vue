<template>
  <div class="calendar-container">
    <!-- 日历头部 -->
    <div class="calendar-header">
      <el-button
        type="text"
        icon="el-icon-arrow-left"
        @click="prevMonth"
        class="nav-button"
      ></el-button>
      <div class="calendar-title">{{ currentYear }}年{{ currentMonth }}月</div>
      <el-button
        type="text"
        icon="el-icon-arrow-right"
        @click="nextMonth"
        class="nav-button"
      ></el-button>
    </div>

    <!-- 星期标题 -->
    <div class="calendar-weekdays">
      <div
        v-for="(day, index) in weekDays"
        :key="index"
        class="weekday"
      >
        {{ day }}
      </div>
    </div>

    <!-- 日期格子 -->
    <div class="calendar-dates">
      <div
        v-for="(day, index) in calendar"
        :key="index"
        :class="[
          'calendar-cell',
          { 'not-current-month': !day.isCurrentMonth },
          { today: day.isToday },
          { selected: day.isSelected }
        ]"
        @click="selectDate(day)"
      >
        <span v-if="day.date" class="date-text">{{ day.date }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CalendarComponent',
  data() {
    return {
      currentDate: new Date(),
      weekDays: ['日', '一', '二', '三', '四', '五', '六'],
      calendar: []
    };
  },
  computed: {
    currentYear() {
      return this.currentDate.getFullYear();
    },
    currentMonth() {
      return this.currentDate.getMonth() + 1;
    },
  },
  methods: {
    generateCalendar() {
      const year = this.currentDate.getFullYear();
      const month = this.currentDate.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      const startDay = firstDay.getDay();
      const totalDays = lastDay.getDate();
      
      let weeks = [];
      
      // 获取上个月的最后几天
      const prevMonthLastDay = new Date(year, month, 0).getDate();
      for (let i = startDay - 1; i >= 0; i--) {
        weeks.push({
          date: prevMonthLastDay - i,
          isCurrentMonth: false,
          isToday: false,
          isSelected: false
        });
      }

      // 填充当前月的日期
      for (let day = 1; day <= totalDays; day++) {
        const dateObj = new Date(year, month, day);
        const today = new Date();
        const isToday = dateObj.toDateString() === today.toDateString();
        const isSelected = this.selectedDate && 
                          dateObj.toDateString() === this.selectedDate.toDateString();
        weeks.push({
          date: day,
          isCurrentMonth: true,
          isToday,
          isSelected
        });
      }

      // 计算需要补充的下个月天数
      const totalCells = Math.ceil((startDay + totalDays) / 7) * 7;
      const remainingDays = totalCells - weeks.length;
      
      // 填充下个月的天数
      for (let i = 1; i <= remainingDays; i++) {
        weeks.push({
          date: i,
          isCurrentMonth: false,
          isToday: false,
          isSelected: false
        });
      }

      this.calendar = weeks;
    },
    prevMonth() {
      this.currentDate = new Date(
        this.currentDate.getFullYear(),
        this.currentDate.getMonth() - 1,
        1
      );
      this.generateCalendar();
    },
    nextMonth() {
      this.currentDate = new Date(
        this.currentDate.getFullYear(),
        this.currentDate.getMonth() + 1,
        1
      );
      this.generateCalendar();
    },
    selectDate(day) {
      if (!day.isCurrentMonth || !day.date) return;
      this.selectedDate = new Date(
        this.currentYear,
        this.currentMonth - 1,
        day.date
      );
      this.generateCalendar();
    }
  },
  mounted() {
    this.generateCalendar();
  },
  watch: {
    selectedDate() {
      this.generateCalendar();
    }
  }
};
</script>

<style scoped>
.calendar-container {
  background: var(--bg-color);
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  height: 26px;
}

.calendar-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.nav-button {
  font-size: 16px;
  color: #409EFF;
}

.calendar-weekdays {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.weekday {
  width: calc(100% / 7);
  text-align: center;
  font-weight: 500;
  color: #409EFF;
  font-size: 14px;
}

.calendar-dates {
  display: flex;
  flex-wrap: wrap;
}

.calendar-cell {
  width: calc(100% / 7);
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s, color 0.3s, transform 0.2s;
  position: relative;
}

.date-text {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.calendar-cell:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.not-current-month {
  color: #909399;
  cursor: default;
}

.today .date-text {
  border: 2px solid #67c23a;
}

.selected .date-text {
  background-color: #409EFF;
  color: #ffffff;
}

.selected-date {
  margin-top: 12px;
  font-size: 14px;
  color: #e5eaf3;
}
</style>