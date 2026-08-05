<script setup>
import { XMarkIcon } from '@heroicons/vue/16/solid'
import { useI18n } from 'vue-i18n'

defineProps({
  show: {
    type: Boolean,
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
  newsItems: {
    type: Array,
    required: true,
  },
  expandedItems: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['close', 'retry', 'toggle'])
const { t } = useI18n()
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="emit('close')"
  >
    <div
      class="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-3xl w-full mx-4 font-mono max-h-[90vh] overflow-y-auto dark:text-white"
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">> {{ t('app.todayNews') }}</h3>
        <button
          class="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded"
          @click="emit('close')"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <div
        v-if="loading"
        class="text-center py-8 text-gray-600 dark:text-gray-400"
      >
        {{ t('app.loading') }}
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
      <div v-else-if="newsItems.length > 0" class="space-y-6">
        <div
          v-for="(news, index) in newsItems"
          :key="news.hot_label"
          class="border-b dark:border-gray-700 pb-4"
        >
          <div
            class="flex items-center gap-2 mb-1 whitespace-nowrap overflow-hidden justify-between"
          >
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
              class="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded"
            >
              {{ news.hot_tag }}
            </span>
          </div>
          <div class="text-sm text-gray-700 dark:text-gray-300 mb-2">
            {{ news.hot_content }}
          </div>
          <button
            class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
            @click="emit('toggle', index)"
          >
            {{
              expandedItems.includes(index)
                ? t('app.collapseFullText')
                : t('app.expandFullText')
            }}
          </button>
          <div
            v-if="expandedItems.includes(index)"
            class="mt-2 whitespace-pre-line text-xs text-gray-800 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-2 rounded"
          >
            <div v-html="news.content"></div>
          </div>
        </div>
      </div>
      <div
        v-else
        class="text-center py-8 text-gray-500 dark:text-gray-400"
      >
        {{ t('app.noTodayNews') }}
      </div>
    </div>
  </div>
</template>
