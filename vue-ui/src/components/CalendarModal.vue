<script setup>
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  XMarkIcon,
} from '@heroicons/vue/16/solid'
import { useI18n } from 'vue-i18n'

defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  selectedMonth: {
    type: Date,
    required: true,
  },
  monthNames: {
    type: Array,
    required: true,
  },
  weekDays: {
    type: Array,
    required: true,
  },
  calendarDays: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  error: {
    type: String,
    default: null,
  },
  calendarData: {
    type: Object,
    default: null,
  },
  daysUntilWeekend: {
    type: Number,
    required: true,
  },
})

const emit = defineEmits([
  'close',
  'previous-month',
  'next-month',
  'today',
  'retry',
])
const { t } = useI18n()
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-4xl w-full mx-4 font-mono max-h-[90vh] overflow-y-auto dark:text-white"
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">> {{ t('app.calendarAndAlmanac') }}</h3>
        <button
          class="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded"
          @click="emit('close')"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="border-r border-gray-200 dark:border-gray-700 pr-6">
          <h4 class="text-base font-bold mb-4">> {{ t('app.calendar') }}</h4>

          <div class="flex justify-between items-center mb-4">
            <button
              class="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded"
              @click="emit('previous-month')"
            >
              <ChevronLeftIcon class="h-5 w-5" />
            </button>
            <h4 class="text-base font-semibold">
              {{ selectedMonth.getFullYear() }}{{ t('app.year') }}
              {{ monthNames[selectedMonth.getMonth()] }}
            </h4>
            <button
              class="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded"
              @click="emit('next-month')"
            >
              <ChevronRightIcon class="h-5 w-5" />
            </button>
          </div>

          <div class="w-full">
            <div class="grid grid-cols-7 gap-1 mb-2">
              <div
                v-for="day in weekDays"
                :key="day"
                class="text-center text-xs font-semibold text-gray-600 dark:text-gray-400 py-2"
              >
                {{ day }}
              </div>
            </div>
            <div class="grid grid-cols-7 gap-1">
              <button
                v-for="day in calendarDays"
                :key="`${day.fullDate.getTime()}`"
                class="aspect-square flex items-center justify-center text-sm relative hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                :class="{
                  'text-gray-400 dark:text-gray-500': !day.isCurrentMonth,
                  'text-black dark:text-white':
                    day.isCurrentMonth && !day.isToday,
                  'bg-black dark:bg-gray-700 text-white font-bold': day.isToday,
                  'hover:bg-gray-800 dark:hover:bg-gray-600': day.isToday,
                }"
              >
                {{ day.date }}
                <div
                  v-if="day.isToday"
                  class="absolute inset-0 border-2 border-black dark:border-white rounded pointer-events-none"
                  :class="{ 'border-white dark:border-gray-300': day.isToday }"
                ></div>
              </button>
            </div>
          </div>

          <div class="mt-4">
            <button
              class="px-4 py-2 text-sm border hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700 w-full"
              @click="emit('today')"
            >
              {{ t('app.backToday') }}
            </button>
          </div>
        </div>

        <div class="pl-0 lg:pl-6">
          <h4 class="text-base font-bold mb-4">> {{ t('app.almanac') }}</h4>

          <div v-if="loading" class="text-center py-8">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ t('app.loadingAlmanac') }}
            </div>
          </div>
          <div v-else-if="error" class="text-center py-8">
            <div class="text-red-600 text-sm mb-2">{{ error }}</div>
            <button
              class="border px-3 py-1 text-sm hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
              @click="emit('retry')"
            >
              {{ t('app.retryLoad') }}
            </button>
          </div>
          <div v-else-if="calendarData" class="space-y-4">
            <div class="space-y-2">
              <div class="text-sm">
                <span class="font-medium">
                  {{ t('app.gregorianCalendar') }}:
                </span>
                {{ calendarData.gregorian_calendar }}
              </div>
              <div class="text-sm">
                <span class="font-medium">
                  {{ t('app.lunarCalendar') }}:
                </span>
                {{ calendarData.lunar_calendar }}
              </div>
              <div class="text-sm">
                <span class="font-medium">
                  {{ t('app.daysUntilWeekend') }}:
                </span>
                {{
                  daysUntilWeekend === -1 || daysUntilWeekend === 5
                    ? t('app.todayIsWeekend')
                    : daysUntilWeekend
                }}
                {{ t('app.days') }}
              </div>
            </div>

            <div>
              <h5
                class="text-sm font-bold text-green-700 dark:text-green-500 mb-2"
              >
                {{ t('app.goodActions') }}：
              </h5>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="action in calendarData.good_actions"
                  :key="action"
                  class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 rounded border dark:border-green-700"
                >
                  {{ action }}
                </span>
              </div>
            </div>

            <div>
              <h5
                class="text-sm font-bold text-red-700 dark:text-red-500 mb-2"
              >
                {{ t('app.badActions') }}：
              </h5>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="action in calendarData.bad_actions"
                  :key="action"
                  class="inline-block px-2 py-1 text-xs bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300 rounded border dark:border-red-700"
                >
                  {{ action }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <div class="text-sm text-gray-500 dark:text-gray-400">
              {{ t('app.noAlmanacData') }}
            </div>
          </div>
        </div>
      </div>

      <div class="mt-6 flex justify-end">
        <button
          class="px-4 py-2 text-sm bg-black text-white hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600"
          @click="emit('close')"
        >
          {{ t('app.close') }}
        </button>
      </div>
    </div>
  </div>
</template>
