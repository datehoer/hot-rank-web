<script setup>
import { ref, computed, onMounted } from 'vue'
import { getHotRank, getYellowCalendar, getTodayTopNews, refresh } from '@/api/hotRank'
import MusicPlayer from '@/components/MusicPlayer.vue'
import {
  AdjustmentsHorizontalIcon,
  XMarkIcon,
  Bars3Icon,
  CalendarDaysIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  BellIcon,
  ChatBubbleOvalLeftEllipsisIcon,
  LanguageIcon,
  MusicalNoteIcon,
  RocketLaunchIcon
} from '@heroicons/vue/16/solid'
import { useI18n } from 'vue-i18n'
import MarkdownIt from 'markdown-it'
import { useHead } from '@vueuse/head';


const itemColumns = ref(1)
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

// 日历相关状态
const currentDate = ref(new Date())
const selectedMonth = ref(new Date())

// 手动排序的板块顺序
const manualSectionOrder = ref([])

// 响应式数据
const data = ref([])
const loading = ref(false)
const error = ref(null)

// 黄历数据
const yellowCalendarData = ref(null)
const yellowCalendarLoading = ref(false)
const yellowCalendarError = ref(null)

// 本地存储的键名
const STORAGE_KEY = 'hotrank-section-order'

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

// 打开今日要闻弹窗
const openNewsModal = async () => {
  showNewsModal.value = true
  newsLoading.value = true
  newsError.value = null
  try {
    const res = await getTodayTopNews()
    if (res.code === 200 && Array.isArray(res.data)) {
      todayNews.value = res.data
      todayNews.value.forEach(item => {
        item.content = md.render(item.content)
      })
    } else {
      newsError.value = res.msg || '加载失败'
    }
  } catch (e) {
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
  // 获取当前数据中的所有板块名称
  const currentSectionNames = currentData.map((section) => section.name)

  if (!savedOrder || !Array.isArray(savedOrder)) {
    return currentSectionNames
  }

  // 将保存的排序转换为板块名称数组（兼容旧的索引格式和新的名称格式）
  const savedSectionNames = savedOrder
    .map((item) => {
      if (typeof item === 'number') {
        // 兼容旧的索引格式
        return currentData[item]?.name
      }
      return item // 新的名称格式
    })
    .filter(Boolean)

  // 按照保存的顺序排列已存在的板块
  const orderedNames = []
  savedSectionNames.forEach((name) => {
    if (currentSectionNames.includes(name)) {
      orderedNames.push(name)
    }
  })

  // 将新增的板块（不在保存的排序中的）添加到最后
  currentSectionNames.forEach((name) => {
    if (!orderedNames.includes(name)) {
      orderedNames.push(name)
    }
  })

  // 直接返回名称数组
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

      // 从本地存储读取排序，并根据当前数据计算新的排序
      const savedOrder = loadSectionOrder()
      manualSectionOrder.value = calculateSectionOrder(filteredData, savedOrder)

      // 保存更新后的排序（处理新增/删除板块后）
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
  fetchHotRank()
})
</script>

<template>
  <main class="p-10 font-mono text-black bg-white max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">{{ t('app.title') }}</h1>

    <div class="mb-6 space-x-2 flex justify-end">
      <button @click="itemColumns = 1" class="px-2 py-1 text-sm hover:bg-gray-100">|</button>
      <button @click="itemColumns = 2" class="px-2 py-1 text-sm hover:bg-gray-100">||</button>
      <button @click="itemColumns = 3" class="px-2 py-1 text-sm hover:bg-gray-100">|||</button>
      <bell-icon class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer" @click="openNewsModal" />
      <musical-note-icon
        @click="openMusicPlayer"
        class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer"
      />
      <calendar-days-icon
        @click="openCalendarModal"
        class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer"
      />
      <adjustments-horizontal-icon
        @click="openSortModal"
        class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer"
      />
      <chat-bubble-oval-left-ellipsis-icon
        class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer"
        @click="goToGitHub"
      />
      <language-icon
        class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer"
        @click="toggleLang"
      />
      <rocket-launch-icon
        class="px-2 py-1 text-sm hover:bg-gray-100 h-8 w-8 cursor-pointer"
        @click="onRefresh"
      />
    </div>

    <!-- 排序设置弹窗 -->
    <div
      v-if="showSortModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeSortModal"
    >
      <div
        class="bg-white p-6 rounded-lg max-w-2xl w-full mx-4 font-mono max-h-[80vh] overflow-y-auto"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold">> {{ t('app.sort') }}</h3>
          <button @click="closeSortModal" class="hover:bg-gray-100 p-1 rounded">
            <x-mark-icon class="h-5 w-5" />
          </button>
        </div>

        <div class="space-y-4">
          <div class="text-sm text-gray-600 mb-4">{{ t('app.sortDescription') }}</div>

          <!-- 可拖拽的板块标签 -->
          <div class="flex flex-wrap gap-3">
            <div
              v-for="(section, index) in sortedData"
              :key="section.name"
              :draggable="true"
              @dragstart="onDragStart($event, index)"
              @dragover="onDragOver"
              @drop="onDrop($event, index)"
              @dragend="onDragEnd"
              @dragenter="onDragEnter"
              @dragleave="onDragLeave"
              class="flex items-center px-2 py-1.5 border border-black bg-white cursor-move hover:bg-gray-50 transition-all duration-200 select-none text-xs"
              :class="{
                'opacity-50 transform scale-95': draggedIndex === index,
                'shadow-md': draggedIndex !== index,
              }"
            >
              <bars3-icon class="h-3 w-3 text-gray-400 mr-1.5 flex-shrink-0" />
              <div class="flex items-center gap-1.5">
                <span class="font-medium">{{ section.name }}</span>
                <span
                  class="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded-full leading-none"
                >
                  {{ section.data?.length || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="mt-6 flex justify-end space-x-2">
          <button @click="resetSort" class="px-4 py-2 text-sm border hover:bg-gray-100">
            {{ t('app.reset') }}
          </button>
          <button
            @click="closeSortModal"
            class="px-4 py-2 text-sm bg-black text-white hover:bg-gray-800"
          >
            {{ t('app.confirm') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 日历模态框 -->
    <div
      v-if="showCalendarModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeCalendarModal"
    >
      <div
        class="bg-white p-6 rounded-lg max-w-4xl w-full mx-4 font-mono max-h-[90vh] overflow-y-auto"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold">> {{ t('app.calendarAndAlmanac') }}</h3>
          <button @click="closeCalendarModal" class="hover:bg-gray-100 p-1 rounded">
            <x-mark-icon class="h-5 w-5" />
          </button>
        </div>

        <!-- 左右分栏布局 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 左侧：日历 -->
          <div class="border-r border-gray-200 pr-6">
            <h4 class="text-base font-bold mb-4">> {{ t('app.calendar') }}</h4>

            <!-- 月份导航 -->
            <div class="flex justify-between items-center mb-4">
              <button @click="previousMonth" class="hover:bg-gray-100 p-1 rounded">
                <chevron-left-icon class="h-5 w-5" />
              </button>

              <h4 class="text-base font-semibold">
                {{ selectedMonth.getFullYear() }}{{ t('app.year') }}
                {{ monthNames[selectedMonth.getMonth()] }}
              </h4>

              <button @click="nextMonth" class="hover:bg-gray-100 p-1 rounded">
                <chevron-right-icon class="h-5 w-5" />
              </button>
            </div>

            <!-- 日历网格 -->
            <div class="w-full">
              <!-- 星期标题 -->
              <div class="grid grid-cols-7 gap-1 mb-2">
                <div
                  v-for="day in weekDays"
                  :key="day"
                  class="text-center text-xs font-semibold text-gray-600 py-2"
                >
                  {{ day }}
                </div>
              </div>

              <!-- 日期网格 -->
              <div class="grid grid-cols-7 gap-1">
                <button
                  v-for="day in calendarDays"
                  :key="`${day.fullDate.getTime()}`"
                  class="aspect-square flex items-center justify-center text-sm relative hover:bg-gray-100 rounded transition-colors"
                  :class="{
                    'text-gray-400': !day.isCurrentMonth,
                    'text-black': day.isCurrentMonth && !day.isToday,
                    'bg-black text-white font-bold': day.isToday,
                    'hover:bg-gray-800': day.isToday,
                  }"
                >
                  {{ day.date }}
                  <div
                    v-if="day.isToday"
                    class="absolute inset-0 border-2 border-black rounded pointer-events-none"
                    :class="{ 'border-white': day.isToday }"
                  ></div>
                </button>
              </div>
            </div>

            <!-- 日历操作按钮 -->
            <div class="mt-4">
              <button @click="goToToday" class="px-4 py-2 text-sm border hover:bg-gray-100 w-full">
                {{ t('app.backToday') }}
              </button>
            </div>
          </div>

          <!-- 右侧：黄历 -->
          <div class="pl-0 lg:pl-6">
            <h4 class="text-base font-bold mb-4">> {{ t('app.almanac') }}</h4>

            <!-- 黄历加载状态 -->
            <div v-if="yellowCalendarLoading" class="text-center py-8">
              <div class="text-sm text-gray-600">{{ t('app.loadingAlmanac') }}</div>
            </div>

            <!-- 黄历错误状态 -->
            <div v-else-if="yellowCalendarError" class="text-center py-8">
              <div class="text-red-600 text-sm mb-2">{{ yellowCalendarError }}</div>
              <button
                @click="fetchYellowCalendar"
                class="border px-3 py-1 text-sm hover:bg-gray-100"
              >
                {{ t('app.retryLoad') }}
              </button>
            </div>

            <!-- 黄历数据 -->
            <div v-else-if="yellowCalendarData" class="space-y-4">
              <!-- 公历农历信息 -->
              <div class="space-y-2">
                <div class="text-sm">
                  <span class="font-medium">{{ t('app.gregorianCalendar') }}：</span
                  >{{ yellowCalendarData.gregorian_calendar }}
                </div>
                <div class="text-sm">
                  <span class="font-medium">{{ t('app.lunarCalendar') }}：</span
                  >{{ yellowCalendarData.lunar_calendar }}
                </div>
              </div>

              <!-- 宜做事项 -->
              <div>
                <h5 class="text-sm font-bold text-green-700 mb-2">{{ t('app.goodActions') }}：</h5>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="action in yellowCalendarData.good_actions"
                    :key="action"
                    class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded border"
                  >
                    {{ action }}
                  </span>
                </div>
              </div>

              <!-- 忌做事项 -->
              <div>
                <h5 class="text-sm font-bold text-red-700 mb-2">{{ t('app.badActions') }}：</h5>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="action in yellowCalendarData.bad_actions"
                    :key="action"
                    class="inline-block px-2 py-1 text-xs bg-red-100 text-red-800 rounded border"
                  >
                    {{ action }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 黄历暂无数据 -->
            <div v-else class="text-center py-8">
              <div class="text-sm text-gray-500">{{ t('app.noAlmanacData') }}</div>
            </div>
          </div>
        </div>

        <!-- 关闭按钮 -->
        <div class="mt-6 flex justify-end">
          <button
            @click="closeCalendarModal"
            class="px-4 py-2 text-sm bg-black text-white hover:bg-gray-800"
          >
            {{ t('app.close') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 音乐播放器模态框 -->
    <div
      v-if="showMusicPlayer"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeMusicPlayer"
    >
      <div
        class="bg-white p-6 rounded-lg max-w-4xl w-full mx-4 font-mono max-h-[90vh] overflow-y-auto"
      >
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold">> {{ t('app.musicPlayer') }}</h3>
          <button @click="closeMusicPlayer" class="hover:bg-gray-100 p-1 rounded">
            <x-mark-icon class="h-5 w-5" />
          </button>
        </div>

        <MusicPlayer />
      </div>
    </div>

    <!-- 今日要闻弹窗 -->
    <div v-if="showNewsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeNewsModal">
      <div class="bg-white p-6 rounded-lg max-w-3xl w-full mx-4 font-mono max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold">> {{ t('app.todayNews') }}</h3>
          <button @click="closeNewsModal" class="hover:bg-gray-100 p-1 rounded">
            <x-mark-icon class="h-5 w-5" />
          </button>
        </div>
        <div v-if="newsLoading" class="text-center py-8 text-gray-600">{{ t('app.loading') }}</div>
        <div v-else-if="newsError" class="text-center py-8">
          <div class="text-red-600 text-sm mb-2">{{ newsError }}</div>
          <button @click="openNewsModal" class="border px-3 py-1 text-sm hover:bg-gray-100">{{ t('app.retryLoad') }}</button>
        </div>
        <div v-else-if="todayNews.length > 0" class="space-y-6">
          <div v-for="(news, idx) in todayNews" :key="news.hot_label" class="border-b pb-4">
            <div class="flex items-center gap-2 mb-1 whitespace-nowrap overflow-hidden justify-between">
              <a
                :href="news.hot_url"
                target="_blank"
                rel="noopener"
                class="font-bold text-base hover:underline truncate"
                :title="news.hot_label"
              >
                {{ news.hot_label }}
              </a>
              <span
                v-if="news.hot_tag"
                class="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded"
              >
                {{ news.hot_tag }}
              </span>
            </div>
            <div class="text-sm text-gray-700 mb-2">{{ news.hot_content }}</div>
            <div>
              <button @click="toggleNewsContent(idx)" class="text-xs text-blue-600 hover:underline">
                {{ expandedNews.includes(idx) ? t('app.collapseFullText') : t('app.expandFullText') }}
              </button>
            </div>
            <div v-if="expandedNews.includes(idx)" class="mt-2 whitespace-pre-line text-xs text-gray-800 bg-gray-50 p-2 rounded">
              <div v-html="news.content"></div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">{{ t('app.noTodayNews') }}</div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <div class="text-lg">{{ t('app.loading') }}</div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-4">{{ error }}</div>
      <button @click="fetchHotRank" class="border px-4 py-2 hover:bg-gray-100">
        {{ t('app.reload') }}
      </button>
    </div>

    <!-- 数据展示 -->
    <div
      v-else-if="data.length > 0"
      class="grid gap-8 grid-cols-1"
      :class="{
        'sm:grid-cols-2': itemColumns === 2,
        'sm:grid-cols-3': itemColumns === 3,
      }"
    >
      <div v-for="(section, idx) in nonEmptySections" :key="section.name" class="mb-12">
        <h2 class="text-xl border-b border-black pb-1 font-bold">
          {{ section.name }}
        </h2>
        <div v-if="section.insert_time" class="text-sm text-gray-600 mt-1">
          <span class="mr-2"> {{ t('app.updateTime') }}: {{ section.insert_time }} </span>
          <span> {{ t('app.itemCount') }}: {{ section.data.length }} </span>
        </div>

        <ul
          class="mt-4 space-y-2 list-none"
          :class="{
            'overflow-y-auto max-h-80': section.data.length > 10,
          }"
        >
          <li
            v-for="(item, i) in section.data"
            :key="i"
            class="flex justify-between items-center gap-4"
            :title="item.hot_label"
          >
            <div class="truncate max-w-[85%]">
              <span class="font-mono text-sm inline-block w-10 text-left">#{{ i + 1 }}</span>
              <a
                :href="item.hot_url"
                class="border-b border-dashed border-black hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ item.hot_label }}
              </a>
            </div>
            <code class="ml-2 px-1 py-0.5 text-sm">
              {{ item.hot_value }}
            </code>
          </li>
        </ul>
      </div>
    </div>

    <!-- 空数据状态 -->
    <div v-else class="text-center py-8">
      <div class="text-gray-500">{{ t('app.noData') }}</div>
    </div>

    <div class="text-center text-gray-500 mt-16">-----------------------------</div>
  </main>
</template>
