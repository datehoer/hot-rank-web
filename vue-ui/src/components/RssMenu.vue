<script setup>
import { onUnmounted, ref } from 'vue'
import { RssIcon } from '@heroicons/vue/16/solid'

const showMenu = ref(false)
const hideTimer = ref(null)

function clearHideTimer() {
  if (hideTimer.value) {
    clearTimeout(hideTimer.value)
    hideTimer.value = null
  }
}

function scheduleHide() {
  clearHideTimer()
  hideTimer.value = setTimeout(() => {
    showMenu.value = false
    hideTimer.value = null
  }, 3000)
}

function toggleMenu() {
  if (showMenu.value) {
    showMenu.value = false
    clearHideTimer()
  } else {
    showMenu.value = true
    scheduleHide()
  }
}

onUnmounted(clearHideTimer)
</script>

<template>
  <div class="relative inline-block">
    <RssIcon
      class="px-2 py-1 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 h-8 w-8 cursor-pointer"
      @click="toggleMenu"
    />
    <div
      v-if="showMenu"
      class="absolute right-0 mt-2 bg-white dark:bg-gray-800 text-black dark:text-white rounded border border-gray-200 dark:border-gray-700 shadow-lg px-2 py-2 w-56 z-50"
      @mouseenter="clearHideTimer"
      @mouseleave="scheduleHide"
    >
      <a
        href="https://www.hotday.uk/feed_with_ai"
        target="_blank"
        rel="noopener noreferrer"
        class="block text-xs px-2 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        AI增强RSS
      </a>
      <a
        href="https://www.hotday.uk/feed"
        target="_blank"
        rel="noopener noreferrer"
        class="block text-xs px-2 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        标准RSS
      </a>
    </div>
  </div>
</template>
