<script setup>
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/16/solid'
import { useI18n } from 'vue-i18n'

defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  sections: {
    type: Array,
    required: true,
  },
  draggedIndex: {
    type: Number,
    required: true,
  },
})

const emit = defineEmits([
  'close',
  'reset',
  'remove',
  'drag-start',
  'drag-over',
  'drop',
  'drag-end',
  'drag-enter',
  'drag-leave',
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
      class="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-2xl w-full mx-4 font-mono max-h-[80vh] overflow-y-auto dark:text-white"
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">> {{ t('app.sort') }}</h3>
        <button
          class="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded"
          @click="emit('close')"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <div class="space-y-4">
        <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ t('app.sortDescription') }}
        </div>

        <div class="flex flex-wrap gap-3">
          <div
            v-for="(section, index) in sections"
            :key="section.name"
            :draggable="true"
            class="flex items-center px-2 py-1.5 border border-black dark:border-gray-400 bg-white dark:bg-gray-700 cursor-move hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 select-none text-xs"
            :class="{
              'opacity-50 transform scale-95': draggedIndex === index,
              'shadow-md': draggedIndex !== index,
            }"
            @dragstart="emit('drag-start', $event, index)"
            @dragover="emit('drag-over', $event)"
            @drop="emit('drop', $event, index)"
            @dragend="emit('drag-end')"
            @dragenter="emit('drag-enter', $event)"
            @dragleave="emit('drag-leave', $event)"
          >
            <Bars3Icon
              class="h-3 w-3 text-gray-400 mr-1.5 flex-shrink-0"
            />
            <div class="flex items-center gap-1.5">
              <span class="font-medium">{{ section.name }}</span>
              <span
                class="text-xs text-gray-500 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded-full leading-none"
              >
                {{ section.data?.length || 0 }}
              </span>
            </div>
            <button
              class="ml-1.5 p-0.5 hover:text-red-600 focus:outline-none"
              title="隐藏该板块"
              @click.stop="emit('remove', index)"
            >
              <XMarkIcon class="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>

      <div class="mt-6 flex justify-end space-x-2">
        <button
          class="px-4 py-2 text-sm border hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
          @click="emit('reset')"
        >
          {{ t('app.reset') }}
        </button>
        <button
          class="px-4 py-2 text-sm bg-black text-white hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600"
          @click="emit('close')"
        >
          {{ t('app.confirm') }}
        </button>
      </div>
    </div>
  </div>
</template>
