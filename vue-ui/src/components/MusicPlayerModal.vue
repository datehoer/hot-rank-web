<script setup>
import { XMarkIcon } from '@heroicons/vue/16/solid'
import { useI18n } from 'vue-i18n'

import MusicPlayer from '@/components/MusicPlayer.vue'

defineProps({
  show: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['close'])
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
        <h3 class="text-lg font-bold">> {{ t('app.musicPlayer') }}</h3>
        <button
          class="hover:bg-gray-100 dark:hover:bg-gray-700 p-1 rounded"
          @click="emit('close')"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>

      <MusicPlayer />
    </div>
  </div>
</template>
