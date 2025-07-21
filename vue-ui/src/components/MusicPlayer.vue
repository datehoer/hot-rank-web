<template>
  <div class="music-player p-5 bg-white text-black relative">
    <!-- Loading Overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-50"
    >
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <!-- ===== Desktop Player ===== -->
    <div v-if="currentTrack && !isMobile" class="mb-10 flex justify-center">
      <div
        class="w-96 bg-white rounded-lg border border-gray-200 shadow-lg hover:shadow-xl transition-shadow duration-300 p-6 relative"
      >
        <div class="vinyl-player flex flex-col items-center pb-6">
          <!-- Tone‑arm -->
          <div class="tonearm-wrapper">
            <div class="tonearm-base"></div>
            <div class="tonearm" :class="{ 'is-playing': isPlaying }">
              <div class="tonearm-body">
                <div class="tonearm-head">
                  <div class="tonearm-needle"></div>
                </div>
              </div>
            </div>
          </div>
          <!-- Vinyl -->
          <div class="vinyl" :class="{ 'animate-spin-slow': isPlaying }">
            <img :src="currentTrack.cover" alt="cover" class="album-cover" />
          </div>

          <!-- Controls -->
          <div class="controls mt-5 flex items-center gap-3 flex-wrap justify-center">
            <button
              @click="togglePlay"
              class="w-10 h-10 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <component :is="isPlaying ? PauseIcon : PlayIcon" class="w-5 h-5" />
            </button>
            <div class="flex items-center gap-2">
              <input
                type="range"
                v-model="volume"
                min="0"
                max="100"
                class="w-28 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <span class="text-xs text-gray-600 min-w-[2rem]">{{ volume }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== Track List (desktop grid) ===== -->
    <div v-if="!isMobile" class="grid grid-cols-4 gap-4">
      <div v-for="track in tracks" :key="track.id" class="flex justify-center">
        <div
          class="album-container cursor-pointer relative"
          :class="{ active: track.id === currentTrack?.id }"
          @click="selectTrack(track)"
        >
          <img :src="track.cover" alt="cover" class="track-cover rounded-lg shadow w-32" />
        </div>
      </div>
    </div>

    <!-- ===== Track List (mobile) ===== -->
    <div v-else class="mobile-track-list space-y-3">
      <div
        v-for="track in tracks"
        :key="track.id"
        class="album-container flex items-center p-3 rounded-lg bg-gray-100 cursor-pointer"
        :class="{ 'ring-2 ring-blue-500': track.id === currentTrack?.id }"
        @click="selectTrack(track)"
      >
        <img
          :src="track.cover"
          alt="cover"
          class="w-14 h-14 rounded-md object-cover flex-shrink-0"
        />
        <div class="ml-3 flex-1 overflow-hidden">
          <p class="track-title whitespace-nowrap overflow-hidden text-ellipsis">
            {{ track.title }}
          </p>
          <p class="text-sm text-gray-600">{{ track.artist }}</p>
        </div>
        <component
          :is="PlayIcon"
          v-if="track.id === currentTrack?.id && isPlaying"
          class="w-5 h-5 text-green-400 flex-shrink-0"
        />
      </div>
    </div>

    <!-- ===== Mobile Controls ===== -->
    <div
      v-if="isMobile && currentTrack"
      class="mobile-controls fixed bottom-0 inset-x-0 bg-white border-t border-gray-200 flex items-center p-3 shadow-lg"
    >
      <div class="flex-1 overflow-hidden mr-3 whitespace-nowrap text-ellipsis">
        {{ currentTrack.title }}
      </div>
      <button
        @click="togglePlay"
        class="w-10 h-10 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        <component :is="isPlaying ? PauseIcon : PlayIcon" class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getMusic } from '@/api/hotRank'
import { PlayIcon, PauseIcon } from '@heroicons/vue/24/solid'

interface Track {
  id: string
  title: string
  artist?: string
  cover: string
  url: string
}

// ===== State =====
const loading = ref(false)
const isPlaying = ref(false)
const volume = ref(50)
const tracks = ref<Track[]>([])
const currentTrack = ref<Track | null>(null)
const isMobile = ref(false)
const columnsCount = computed(() => (isMobile.value ? 1 : 4))

// using programmatic Audio instance keeps DOM clean
const audio = new Audio()

audio.addEventListener('ended', () => handleTrackEnd())

audio.volume = volume.value / 100

// ===== Lifecycle =====
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchTracks()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  audio.pause()
})

// ===== Watchers =====
watch(volume, (v) => {
  audio.volume = v / 100
})

watch(currentTrack, async (newTrack) => {
  if (!newTrack) return
  audio.src = newTrack.url
  if (isPlaying.value) {
    await audio.play()
  }
})

// ===== Methods =====
async function fetchTracks() {
  loading.value = true
  try {
    const response = await getMusic()

    if (!response || !response.data || !Array.isArray(response.data)) {
      console.error('Invalid API response:', response)
      return
    }

    const { data } = response

    // Convert MusicData array to Track array format
    const trackList: Track[] = data.map((item, index) => ({
      id: item.id ? item.id.toString() : (Date.now() + index).toString(),
      title: item.title || 'Unknown Title',
      artist: 'Unknown Artist', // Default value since API doesn't provide artist
      cover: item.cover || '',
      url: item.url || '',
    }))

    // Filter out tracks without valid URLs
    const validTracks = trackList.filter((track) => {
      if (!track.url) {
        console.warn(`Track "${track.title}" has no valid URL, skipping...`)
        return false
      }
      return true
    })

    if (validTracks.length === 0) {
      console.error('No valid tracks found')
      return
    }

    tracks.value = validTracks
    currentTrack.value = validTracks[0] // Set first track as current
  } catch (error) {
    console.error('Error fetching tracks:', error)
  } finally {
    loading.value = false
  }
}

async function togglePlay() {
  if (!currentTrack.value) return
  if (isPlaying.value) {
    audio.pause()
    isPlaying.value = false
  } else {
    if (!audio.src) audio.src = currentTrack.value.url
    await audio.play()
    isPlaying.value = true
  }
}

function selectTrack(track: Track) {
  if (track.id === currentTrack.value?.id) return
  currentTrack.value = track
  isPlaying.value && togglePlay()
}

function handleTrackEnd() {
  const idx = tracks.value.findIndex((t) => t.id === currentTrack.value?.id)
  const next = tracks.value[(idx + 1) % tracks.value.length]
  selectTrack(next)
  togglePlay()
}
</script>

<style scoped>
.music-player {
  /* fallback if Tailwind not loaded */
  background-color: #ffffff;
}

/* Vinyl */
.vinyl {
  position: relative;
  width: 12rem;
  height: 12rem;
  border-radius: 50%;
  background: repeating-radial-gradient(circle at center, #000, #000 2px, #171717 3px, #171717 4px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.album-cover {
  width: 40%;
  height: 40%;
  border-radius: 50%;
  object-fit: cover;
  border: 0.75rem solid #0f0f0f;
}

@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.animate-spin-slow {
  animation: spin-slow 8s linear infinite;
}

/* Tonearm (improved positioning and animation) */
/* 唱臂样式 */
.tonearm-wrapper {
  position: absolute;
  top: 10px;
  right: 60px;
  width: 120px;
  height: 120px;
  z-index: 10;
}

.tonearm-base {
  position: absolute;
  top: -7px;
  right: 50%;
  width: 30px;
  height: 30px;
  background: #444;
  border-radius: 50%;
  border: 4px solid #666;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transform: translateX(50%);
  z-index: 1;
}

.tonearm-base::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #444;
  border-radius: 50%;
  border: 2px solid #666;
}

.tonearm {
  position: absolute;
  top: 10px;
  right: 50%;
  width: 6px;
  height: 100px;
  transform-origin: top center;
  transform: translateX(50%) rotate(-45deg);
  transition: transform 0.5s ease;
  z-index: 2;
}

.tonearm.is-playing {
  transform: translateX(50%) rotate(-10deg);
}

.tonearm-body {
  position: relative;
  width: 6px;
  height: 80px;
  background: linear-gradient(90deg, #333, #666);
  border-radius: 3px;
  box-shadow: -1px 2px 3px rgba(0, 0, 0, 0.2);
}

.tonearm-head {
  position: absolute;
  bottom: -15px;
  left: -7px;
  width: 20px;
  height: 15px;
  background: #333;
  border-radius: 4px;
  box-shadow: -1px 2px 3px rgba(0, 0, 0, 0.2);
}

.tonearm-needle {
  position: absolute;
  bottom: -8px;
  left: 9px;
  width: 2px;
  height: 15px;
  background: #666;
  transform: rotate(30deg);
  transform-origin: top center;
}


/* Desktop album hover */
.album-container.active .track-cover {
  outline: 3px solid #3b82f6;
}
.track-title {
  font-size: 0.9375rem;
}

/* Custom slider styles */
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.slider::-webkit-slider-track {
  width: 100%;
  height: 8px;
  cursor: pointer;
  background: #e5e7eb;
  border-radius: 4px;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.slider::-moz-range-track {
  width: 100%;
  height: 8px;
  cursor: pointer;
  background: #e5e7eb;
  border-radius: 4px;
}
</style>
