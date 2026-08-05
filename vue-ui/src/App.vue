<script setup>
import { ref, computed, onMounted } from 'vue'
import { getHotRank, getYellowCalendar, getTodayTopNews, refresh } from '@/api/hotRank'
import CalendarModal from '@/components/CalendarModal.vue'
import MusicPlayerModal from '@/components/MusicPlayerModal.vue'
import RssMenu from '@/components/RssMenu.vue'
import SortSettingsModal from '@/components/SortSettingsModal.vue'
import TodayNewsModal from '@/components/TodayNewsModal.vue'
import {
  AdjustmentsHorizontalIcon,
  CalendarDaysIcon,
  BellIcon,
  ChatBubbleOvalLeftEllipsisIcon,
  LanguageIcon,
  MusicalNoteIcon,
  RocketLaunchIcon,
  Bars3BottomLeftIcon,
  EyeIcon,
  EyeSlashIcon,
  MoonIcon,
  SunIcon
} from '@heroicons/vue/16/solid'
import { useI18n } from 'vue-i18n'
import MarkdownIt from 'markdown-it'
import { useHead } from '@vueuse/head';


const { t, tm, locale } = useI18n()
const md = new MarkdownIt();
useHead({
  script: [
    {
      src: 'https://cloud.umami.is/script.js',
      defer: true,
      'data-website-id': '24595aed-c7d3-4407-9ce1-e3d54b58bf00',
    }
  ],
  meta: [
    { name: 'description', content: t('app.description') }
  ]
});
// 弹窗状态
const showSortModal = ref(false)
const showCalendarModal = ref(false)
const showMusicPlayer = ref(false)
const showNewsModal = ref(false)
const newsLoading = ref(false)
const newsError = ref(null)
const todayNews = ref([])


const showColPopover = ref(false)
const inputCols      = ref(3)
const isWrap = ref(false)

const isDark = ref(false)


// 日历相关状态
const currentDate = ref(new Date())
const selectedMonth = ref(new Date())

// 手动排序的板块顺序
const manualSectionOrder = ref([])

// 布局相关状态
const layout = ref(3)

// 响应式数据
const data = ref([])
const loading = ref(false)
const error = ref(null)

// 黄历数据
const yellowCalendarData = ref(null)
const yellowCalendarLoading = ref(false)
const yellowCalendarError = ref(null)

// 日历
const daysUntilWeekend = computed(() => {
  const today = new Date()
  const day = today.getDay()
  const daysToSaturday = (6 - day) % 7
  return daysToSaturday - 1
})

// 本地存储的键名
const STORAGE_KEY = 'hotrank-section-order'
const STORAGE_KEY_LAYOUT = 'hotrank-layout-type'
const STORAGE_KEY_THEME = 'hotrank-theme'
const STORAGE_KEY_WRAP = 'hotrank-wrap'

// 日历相关函数
const weekDays = computed(() => {
  const days = tm('app.weekDays')
  return Array.isArray(days) ? days : ['日', '一', '二', '三', '四', '五', '六']
})
const monthNames = computed(() => {
  const months = tm('app.monthNames')
  return Array.isArray(months)
    ? months
    : [
        '一月',
        '二月',
        '三月',
        '四月',
        '五月',
        '六月',
        '七月',
        '八月',
        '九月',
        '十月',
        '十一月',
        '十二月',
      ]
})

// 获取当月的所有日期
const calendarDays = computed(() => {
  const year = selectedMonth.value.getFullYear()
  const month = selectedMonth.value.getMonth()

  // 获取当月第一天
  const firstDay = new Date(year, month, 1)
  // 获取当月最后一天
  const lastDay = new Date(year, month + 1, 0)

  // 获取第一天是周几 (0-6, 周日为0)
  const firstDayOfWeek = firstDay.getDay()

  const days = []

  // 添加上个月的日期填充
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month - 1, new Date(year, month, 0).getDate() - i)
    days.push({
      date: date.getDate(),
      isCurrentMonth: false,
      isToday: false,
      fullDate: date,
    })
  }

  // 添加当月的日期
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day)
    const isToday =
      date.getFullYear() === currentDate.value.getFullYear() &&
      date.getMonth() === currentDate.value.getMonth() &&
      date.getDate() === currentDate.value.getDate()

    days.push({
      date: day,
      isCurrentMonth: true,
      isToday,
      fullDate: date,
    })
  }

  // 添加下个月的日期填充 (确保总共6行42天)
  const remainingDays = 42 - days.length
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(year, month + 1, day)
    days.push({
      date: day,
      isCurrentMonth: false,
      isToday: false,
      fullDate: date,
    })
  }

  return days
})

// 打开日历模态框
const openCalendarModal = () => {
  showCalendarModal.value = true
  selectedMonth.value = new Date()
  fetchYellowCalendar()
}

// 关闭日历模态框
const closeCalendarModal = () => {
  showCalendarModal.value = false
}

// 打开音乐播放器
const openMusicPlayer = () => {
  showMusicPlayer.value = true
}

// 关闭音乐播放器
const closeMusicPlayer = () => {
  showMusicPlayer.value = false
}

function decodeUnicode(str) {
  if (typeof str !== 'string') return str
  try {
    return JSON.parse('"' + str + '"')
  } catch {
    return str
  }
}

// 打开今日要闻弹窗
const openNewsModal = async () => {
  showNewsModal.value = true
  newsLoading.value = true
  newsError.value = null
  try {
    const res = await getTodayTopNews()
    if (res.code === 200 && Array.isArray(res.data)) {
      todayNews.value = res.data.map(item => {
        const newItem = {}
        for (const key in item) {
          const val = item[key]
          if (key === 'content' && typeof val === 'string') {
            newItem[key] = md.render(decodeUnicode(val))
          } else if (typeof val === 'string') {
            newItem[key] = decodeUnicode(val)
          } else {
            newItem[key] = val
          }
          
        }
        return newItem
      })
    } else {
      newsError.value = res.msg || '加载失败'
    }
  } catch (error) {
    console.error('Error fetching news:', error)
    newsError.value = '网络错误'
  } finally {
    newsLoading.value = false
  }
}

const closeNewsModal = () => {
  showNewsModal.value = false
}

const expandedNews = ref([])

const toggleNewsContent = (idx) => {
  if (expandedNews.value.includes(idx)) {
    expandedNews.value = expandedNews.value.filter(i => i !== idx)
  } else {
    expandedNews.value.push(idx)
  }
}

// 切换月份
const previousMonth = () => {
  selectedMonth.value = new Date(
    selectedMonth.value.getFullYear(),
    selectedMonth.value.getMonth() - 1,
    1,
  )
}

// 切换语言
const toggleLang = () => {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('locale', locale.value)
}

const nextMonth = () => {
  selectedMonth.value = new Date(
    selectedMonth.value.getFullYear(),
    selectedMonth.value.getMonth() + 1,
    1,
  )
}

// 跳转到今天
const goToToday = () => {
  selectedMonth.value = new Date()
}

// 跳转到GitHub
const goToGitHub = () => {
  window.open('https://github.com/datehoer/hot-rank-web', '_blank')
}

// 刷新按钮点击
const onRefresh = async () => {
  try {
    await refresh()
    fetchHotRank()
  } catch (e) {
    console.error('Failed to refresh data:', e)
  }
}

// 获取黄历数据
const fetchYellowCalendar = async () => {
  yellowCalendarLoading.value = true
  yellowCalendarError.value = null

  try {
    const response = await getYellowCalendar()
    if (response.code === 200) {
      yellowCalendarData.value = response.data
    } else {
      yellowCalendarError.value = response.msg || t('app.almanacError')
    }
  } catch (err) {
    console.error('Failed to get almanac data:', err)
    yellowCalendarError.value = t('app.networkError')
  } finally {
    yellowCalendarLoading.value = false
  }
}

// 保存排序到本地存储
const saveSectionOrder = () => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(manualSectionOrder.value))
  } catch (err) {
    console.warn('保存排序到本地存储失败:', err)
  }
}

// 从本地存储读取排序
const loadSectionOrder = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : null
  } catch (err) {
    console.warn('从本地存储读取排序失败:', err)
    return null
  }
}

// 根据保存的排序和当前数据计算新的排序
const calculateSectionOrder = (currentData, savedOrder) => {
  const currentSectionNames = currentData.map((section) => section.name)

  if (!savedOrder || !Array.isArray(savedOrder)) {
    return currentSectionNames
  }

  const savedSectionNames = savedOrder
    .map((item) => {
      if (typeof item === 'number') {
        return currentData[item]?.name
      }
      return item
    })
    .filter(Boolean)

  const orderedNames = []
  savedSectionNames.forEach((name) => {
    if (currentSectionNames.includes(name)) {
      orderedNames.push(name)
    }
  })

  currentSectionNames.forEach((name) => {
    if (!orderedNames.includes(name)) {
      orderedNames.push(name)
    }
  })

  return orderedNames
}

// 获取热门排行榜数据
const fetchHotRank = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await getHotRank()
    if (response.code === 200) {
      const filteredData = response.data.filter((item) => item && Array.isArray(item.data))
      data.value = filteredData

      const savedOrder = loadSectionOrder()
      manualSectionOrder.value = calculateSectionOrder(filteredData, savedOrder)

      saveSectionOrder()
    } else {
      error.value = response.msg || t('app.error')
    }
  } catch (err) {
    console.error('Failed to get hot rank data:', err)
    error.value = t('app.networkError')
  } finally {
    loading.value = false
  }
}

// 按手动排序顺序的数据
const sortedData = computed(() => {
  return manualSectionOrder.value
    .map((sectionName) => data.value.find((section) => section.name === sectionName))
    .filter(Boolean)
})

const nonEmptySections = computed(() =>
  (sortedData.value || []).filter(
    (section) => section && Array.isArray(section.data) && section.data.length > 0,
  ),
)

// 打开排序弹窗
const openSortModal = () => {
  showSortModal.value = true
}

// 关闭排序弹窗
const closeSortModal = () => {
  showSortModal.value = false
}

// 重置排序
const resetSort = () => {
  manualSectionOrder.value = data.value.map((section) => section.name)
  saveSectionOrder()
}

// 拖拽相关函数
const draggedIndex = ref(-1)

const onDragStart = (event, index) => {
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', index.toString())
}

const onDragOver = (event) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
}

const onDrop = (event, targetIndex) => {
  event.preventDefault()
  event.stopPropagation()

  const draggedIdx = draggedIndex.value
  if (draggedIdx !== -1 && draggedIdx !== targetIndex) {
    const newOrder = [...manualSectionOrder.value]
    const draggedItem = newOrder[draggedIdx]

    // 移除拖拽的项目
    newOrder.splice(draggedIdx, 1)

    // 在新位置插入
    const insertIndex = draggedIdx < targetIndex ? targetIndex - 1 : targetIndex
    newOrder.splice(insertIndex, 0, draggedItem)

    manualSectionOrder.value = newOrder
    // 保存到本地存储
    saveSectionOrder()
  }

  draggedIndex.value = -1
}

const onDragEnd = () => {
  draggedIndex.value = -1
}

const onDragEnter = (event) => {
  event.preventDefault()
}

const onDragLeave = (event) => {
  event.preventDefault()
}

// 组件挂载时获取数据
onMounted(() => {
  const savedLayout = localStorage.getItem(STORAGE_KEY_LAYOUT)
  if (savedLayout) {
    layout.value = savedLayout
  }

  const savedIsDark = localStorage.getItem(STORAGE_KEY_THEME)
  if (savedIsDark) {
    isDark.value = savedIsDark === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  const savedIsWrap = localStorage.getItem(STORAGE_KEY_WRAP)
  if (savedIsWrap) {
    isWrap.value = savedIsWrap === 'true'
  } else {
    isWrap.value = false
  }
  applyTheme()
  fetchHotRank()
})

function toggleTheme () {
  isDark.value = !isDark.value
  applyTheme()
}

const toggleWrap = () => {
  isWrap.value = !isWrap.value
  localStorage.setItem(STORAGE_KEY_WRAP, isWrap.value.toString())
}

function applyTheme () {
  const cls = document.documentElement.classList
  if (isDark.value) {
    cls.add('dark')
    localStorage.setItem(STORAGE_KEY_THEME, 'dark')
  } else {
    cls.remove('dark')
    localStorage.setItem(STORAGE_KEY_THEME, 'light')
  }
}

function toggleColPopover () {
  inputCols.value = layout.value
  showColPopover.value = !showColPopover.value
}

function saveCols () {
  const n = Number(inputCols.value)
  if (!Number.isInteger(n) || n < 1 || n > 6) {
    alert('请输入 1~6 的整数')
    return
  }
  layout.value = n
  localStorage.setItem(STORAGE_KEY_LAYOUT, n.toString())
  showColPopover.value = false
}

const containerMaxW = computed(() =>
  layout.value > 3 ? 'max-w-8xl' : 'max-w-6xl'
)

// 删除指定下标的板块
const removeSection = (idx) => {
  if (idx < 0 || idx >= manualSectionOrder.value.length) return
  manualSectionOrder.value.splice(idx, 1)
  saveSectionOrder()
}

</script>

<template>
  <main class="p-10 font-mono text-black bg-white dark:bg-gray-900 dark:text-white mx-auto" :class="containerMaxW">
    <h1 class="text-2xl font-bold mb-8">{{ t('app.title') }}</h1>

    <div class="mb-6 space-x-2 flex justify-end">
      <div class="relative inline-block">
        <!-- 触发按钮 -->
         <Bars3BottomLeftIcon
            @click="toggleColPopover"
            class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
          />

        <!-- Popover 气泡 -->
        <div
          v-if="showColPopover"
          class="absolute left-1/2 -translate-x-1/2 -top-3 -translate-y-full
                bg-black text-white rounded px-3 py-2 w-48 z-50"
        >
          <div class="text-xs mb-1">{{ t('app.colCount') }} (1-6):</div>
          <input
            v-model="inputCols"
            type="number"
            min="1"
            max="6"
            class="w-full mb-2 text-center text-black border rounded"
          />
          <button
            @click="saveCols"
            class="w-full text-xs bg-white text-black py-1 rounded hover:bg-gray-100"
          >
            {{ t('app.save') }}
          </button>

          <!-- 箭头 -->
          <div
            class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full
                  w-3 h-3 bg-black rotate-45"
          ></div>
        </div>
      </div>
      <!-- 换行 / 不换行切换 -->
      <button
        @click="toggleWrap"
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
      >
        <EyeIcon v-if="!isWrap"  class="h-full w-full" />
        <EyeSlashIcon v-else class="h-full w-full" />
      </button>
      <bell-icon class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer" @click="openNewsModal" />
      <musical-note-icon
        @click="openMusicPlayer"
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
      />
      <calendar-days-icon
        @click="openCalendarModal"
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
      />
      <adjustments-horizontal-icon
        @click="openSortModal"
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
      />
      <chat-bubble-oval-left-ellipsis-icon
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
        @click="goToGitHub"
      />
      <language-icon
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
        @click="toggleLang"
      />
      <RssMenu />
      <rocket-launch-icon
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
        @click="onRefresh"
      />
      <button
        @click="toggleTheme"
        class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800
              h-8 w-8 cursor-pointer rounded"
      >
        <MoonIcon v-if="!isDark" class="h-full w-full" />
        <SunIcon  v-else      class="h-full w-full" />
      </button>
    </div>
    
    <SortSettingsModal
      :show="showSortModal"
      :sections="sortedData"
      :dragged-index="draggedIndex"
      @close="closeSortModal"
      @reset="resetSort"
      @remove="removeSection"
      @drag-start="onDragStart"
      @drag-over="onDragOver"
      @drop="onDrop"
      @drag-end="onDragEnd"
      @drag-enter="onDragEnter"
      @drag-leave="onDragLeave"
    />

    <CalendarModal
      :show="showCalendarModal"
      :selected-month="selectedMonth"
      :month-names="monthNames"
      :week-days="weekDays"
      :calendar-days="calendarDays"
      :loading="yellowCalendarLoading"
      :error="yellowCalendarError"
      :calendar-data="yellowCalendarData"
      :days-until-weekend="daysUntilWeekend"
      @close="closeCalendarModal"
      @previous-month="previousMonth"
      @next-month="nextMonth"
      @today="goToToday"
      @retry="fetchYellowCalendar"
    />

    <MusicPlayerModal :show="showMusicPlayer" @close="closeMusicPlayer" />

    <TodayNewsModal
      :show="showNewsModal"
      :loading="newsLoading"
      :error="newsError"
      :news-items="todayNews"
      :expanded-items="expandedNews"
      @close="closeNewsModal"
      @retry="openNewsModal"
      @toggle="toggleNewsContent"
    />

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <div class="text-lg">{{ t('app.loading') }}</div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-4">{{ error }}</div>
      <button @click="fetchHotRank" class="border px-4 py-2 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700">
        {{ t('app.reload') }}
      </button>
    </div>

    <!-- 数据展示 -->
    <div
      v-else-if="data.length > 0"
      class="grid gap-8 grid-cols-1"
      :style="{ gridTemplateColumns: `repeat(${layout}, minmax(0,1fr))` }"
    >
      <div v-for="section in nonEmptySections" :key="section.name" class="mb-12">
        <h2 class="text-xl border-b border-black dark:border-gray-400 pb-1 font-bold">
          {{ section.name }}
        </h2>
        <div v-if="section.insert_time" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          <span class="mr-2"> {{ t('app.updateTime') }}: {{ section.insert_time }} </span>
          <span> {{ t('app.itemCount') }}: {{ section.data.length }} </span>
        </div>

        <ul
          class="mt-4 space-y-2 list-none overflow-y-auto max-h-80"
        >
          <li
            v-for="(item, i) in section.data"
            :key="i"
            class="flex justify-between items-center gap-4"
            :title="item.hot_label"
          >
            <div
              :class="[
                'max-w-[95%]',
                isWrap ? 'whitespace-normal' : 'truncate'
              ]"
            >
              <span class="font-mono text-sm inline-block w-10 text-left">#{{ i + 1 }}</span>
              <a
                :href="item.hot_url"
                class="border-b border-dashed border-black dark:border-gray-400 hover:underline"
                target="_blank"
                rel="noopener noreferrer" 
              >
                {{ item.hot_label }}
              </a>
            </div>
            <!-- <code class="ml-2 px-1 py-0.5 text-sm">
              {{ item.hot_value }}
            </code> -->
          </li>
        </ul>
      </div>
    </div>

    <!-- 空数据状态 -->
    <div v-else class="text-center py-8">
      <div class="text-gray-500 dark:text-gray-400">{{ t('app.noData') }}</div>
    </div>

    <div class="text-center text-gray-500 dark:text-gray-400 mt-16">-----------------------------</div>
  </main>
</template>
