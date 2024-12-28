<template>
  <div class="music-player" v-loading="loading">
    <div class="current-player" v-if="currentTrack">
      <el-card class="player-card" shadow="hover">
        <div class="vinyl-player">
          <!-- 唱片指针结构 -->
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
          <div class="vinyl" ref="vinyl" :class="{ 'is-playing': isPlaying }">
            <img :src="currentTrack.cover" alt="album cover" class="album-cover">
          </div>
          <div class="controls">
            <el-button 
              type="primary"
              :disabled="isPlaying"
              icon="el-icon-video-play"
              @click="togglePlay"
              round
            ></el-button>
            <el-button 
              type="danger"
              :disabled="!isPlaying"
              icon="el-icon-video-pause"
              @click="togglePlay"
              round
            ></el-button>
            <div class="volume-control">
              <i class="microphone" style="color: #909399; margin-right: 5px;">📢</i>
              <el-slider
                v-model="volume"
                :min="0"
                :max="100"
                @input="handleVolumeChange"
                size="small"
              ></el-slider>
              <span class="volume-text">{{ volume }}%</span>
            </div>
          </div>
        </div>
        <div v-loading="isLoading" element-loading-text="加载音频中...">
          <audio ref="audioPlayer" @ended="handleTrackEnd"></audio>
        </div>
      </el-card>
    </div>

    <!-- 音乐列表 -->
    <div class="track-list">
      <!-- PC端列表 -->
      <el-row :gutter="16" v-if="!isMobile">
        <el-col 
          v-for="(track, index) in tracks" 
          :key="index"
          :span="24 / columnsCount"
          class="track-item"
        >
          <div 
            class="album-container"
            :class="{ 'active': currentTrack?.id === track.id }"
            @click="selectTrack(track)"
          >
            <!-- PC端专辑展示 -->
            <div class="album-cover-wrapper">
              <img :src="track.cover" alt="album cover" class="track-cover">
            </div>
            <div class="album-disc">
              <div class="disc-inner">
                <img :src="track.cover" alt="album cover" class="disc-cover">
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 移动端列表 -->
      <div v-else class="mobile-track-list">
        <div 
          v-for="(track, index) in tracks" 
          :key="index"
          class="track-item"
        >
          <div 
            class="album-container"
            :class="{ 'active': currentTrack?.id === track.id }"
            @click="selectTrack(track)"
          >
            <div class="album-cover-wrapper">
              <img :src="track.cover" alt="album cover" class="track-cover">
            </div>
            <div class="track-info">
              <h3 class="track-title">{{ track.title }}</h3>
              <div class="track-artist">{{ track.artist }}</div>
            </div>
            <div v-if="currentTrack?.id === track.id" class="playing-indicator">
              <i class="el-icon-video-play"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端播放控制栏 -->
    <div class="mobile-controls" v-if="isMobile && currentTrack">
      <div class="current-track-info">
        {{ currentTrack.title }}
      </div>
      <el-button 
        type="primary"
        :icon="isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'"
        @click="togglePlay"
        class="play-pause-btn"
        circle
      ></el-button>
    </div>

    <!-- 音频播放器 -->
    <audio ref="audioPlayer" @ended="handleTrackEnd"></audio>
  </div>
</template>

<script>
import { getMusic } from '@/api/rank'
export default {
  name: 'MusicPlayer',
  data() {
    return {
      isPlaying: false,
      isLoading: false,
      currentTrack: null,
      tracks: [],
      audio: null,
      loading: false,
      volume: 50,
      isMobile: false,
      columnsCount: 4,
    }
  },
  created() {
    // 确保在组件创建时设置默认曲目
    this.getMusicList()
    this.checkMobile()
    // 添加窗口大小变化监听
    window.addEventListener('resize', this.checkMobile)
  },
  mounted() {
    this.$nextTick(() => {
      this.audio = this.$refs.audioPlayer
      if (this.audio && this.currentTrack) {
        this.audio.src = this.currentTrack.url
        this.audio.volume = this.volume / 100
      }
    })
  },
  destroyed() {
    // 移除事件监听
    window.removeEventListener('resize', this.checkMobile)
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768
      this.columnsCount = this.isMobile ? 1 : 4
    },
    getMusicList() {
      this.loading = true
      getMusic().then(res => {
        this.tracks = res.data
        if (this.tracks && this.tracks.length > 0) {
          this.currentTrack = this.tracks[0]
        }
      }).finally(() => {
        this.loading = false
      })
    },
    async togglePlay() {
      if (!this.audio) {
        // 确保audio元素存在
        this.audio = this.$refs.audioPlayer
      }
      if (!this.audio || !this.currentTrack) return

      try {
        this.isLoading = true
        if (this.isPlaying) {
          await this.audio.pause()
        } else {
          // 确保设置了音频源
          if (!this.audio.src) {
            this.audio.src = this.currentTrack.url
          }
          await this.audio.load()
          await this.audio.play()
        }
        this.isPlaying = !this.isPlaying
      } catch (error) {
        console.error('播放出错:', error)
        this.$message.error('播放失败，请检查音频源是否有效')
        this.isPlaying = false
      } finally {
        this.isLoading = false
      }
    },
    selectTrack(track) {
      if (!this.audio) {
        // 确保audio元素存在
        this.audio = this.$refs.audioPlayer
      }
      if (!this.audio) return
      
      // 停止当前播放
      if (this.isPlaying) {
        this.audio.pause()
        this.isPlaying = false
      }
      
      if (this.currentTrack?.id !== track.id) {
        this.currentTrack = track
        this.audio.src = track.url
        // // 自动播放新选择的曲目
        // this.togglePlay()
      }
    },
    handleTrackEnd() {
      this.isPlaying = false
      const currentIndex = this.tracks.findIndex(t => t.id === this.currentTrack.id)
      const nextIndex = (currentIndex + 1) % this.tracks.length
      this.selectTrack(this.tracks[nextIndex])
      this.togglePlay()
    },
    handleVolumeChange(value) {
      if (this.audio) {
        this.audio.volume = value / 100
      }
    }
  }
}
</script>

<style scoped>
/* 基础布局 */
.music-player {
  padding: 20px;
  background-color: var(--bg-color);
  min-height: 30vh;
}

/* 当前播放器 */
.current-player {
  margin-bottom: 40px;
}

.player-card {
  background-color: var(--card-bg) !important;
  border-radius: 8px;
  width: 400px;
  margin: 0 auto;
  overflow: visible;
  padding-top: 20px;
  border: 1px solid var(--border-color) !important;
}

/* 唱片播放器 */
.vinyl-player {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 20px;
}

/* 唱片样式 */
.vinyl {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  background: repeating-radial-gradient(
    circle at center,
    #000000,
    #000000 2px,
    #171717 3px, #171717 4px
  );
  margin: 0 auto;
  transition: transform 0.3s ease;
}

.album-cover {
  width: 40%;
  height: 40%;
  object-fit: cover;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 15px solid var(--bg-color);
  box-shadow: 0 0 0 2px var(--border-color);
}

/* 唱臂样式 */
.tonearm-wrapper {
  position: absolute;
  top: -20px;
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

.controls {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.volume-control {
  display: flex;
  align-items: center;
  background-color: var(--hover-bg);
  padding: 5px 10px;
  border-radius: 20px;
  margin-left: 15px;
}

.volume-control .el-slider {
  width: 80px;
  margin: 0 8px;
}

.volume-text {
  color: var(--secondary-text);
  font-size: 12px;
  min-width: 35px;
}

.track-list {
  padding: 20px;
  color: var(--text-color);
}

.track-item {
  margin-bottom: 20px;
}

.album-container {
  position: relative;
  height: 80px;
  width: 80px;
  cursor: pointer;
  overflow: visible;
  margin: 0 auto;
  perspective: 1000px;
}

.album-container.active .album-disc {
  opacity: 1;
  transform: translateX(50%);
}

.album-container.active .album-cover-wrapper {
  transform: translateX(20px);
}
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.album-container.active .album-disc {
  animation: rotate 8s linear infinite;
}

.album-cover-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  z-index: 2;
  transition: transform 0.3s ease;
}

.album-disc {
  position: absolute;
  top: 0;
  left: -40%;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 50%;
  transform: translateX(0);
  transition: transform 0.3s ease;
  z-index: 1;
  opacity: 0;
}

.disc-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 30%;
  height: 30%;
  transform: translate(-50%, -50%);
  background: #fff;
  border-radius: 50%;
  overflow: hidden;
}

.disc-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.track-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media screen and (max-width: 768px) {
  .vinyl-player,
  .vinyl,
  .tonearm-wrapper,
  .player-card {
    display: none;
  }

  .music-player {
    padding: 12px;
    min-height: 100vh;
  }

  .track-list {
    padding: 10px;
  }

  .track-item {
    margin-bottom: 12px;
  }

  .album-container {
    display: flex;
    align-items: center;
    padding: 12px;
    background: #333;
    border-radius: 8px;
    cursor: pointer;
    height: auto;
    width: auto;
    transition: background-color 0.3s;
    width: 100%;
    box-sizing: border-box;
    overflow: visible;
    position: relative;
  }
  .album-container.active .album-cover-wrapper {
    transform: none;
  }
  .album-container.active {
    background: #404040;
  }

  .album-cover-wrapper {
    position: relative;
    width: 56px;
    height: 56px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
  }

  .track-cover {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .track-info {
    flex: 1;
    margin-left: 12px;
    overflow: hidden;
  }

  .track-title {
    color: #fff;
    font-size: 15px;
    margin: 0 0 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .track-artist {
    color: #999;
    font-size: 13px;
  }

  .mobile-controls {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #1a1a1a;
    padding: 12px 16px;
    align-items: center;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
    z-index: 100;
  }


  .current-track-info {
    flex: 1;
    margin-right: 12px;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .play-pause-btn {
    padding: 8px;
    margin-left: 8px;
  }

  .volume-control {
    display: none;
  }
  :deep(.el-dialog) {
    width: 100% !important;
    margin: 0 !important;
    position: fixed;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    height: 100vh;
    margin: 0 !important;
    border-radius: 0;
  }

  :deep(.el-dialog__body) {
    height: calc(100vh - 108px);
    padding: 0 !important;
    overflow-y: auto;
  }

  .music-player {
    padding: 0;
    height: 100%;
  }

  .mobile-track-list {
    padding: 12px;
  }

  .track-item {
    margin-bottom: 12px;
  }
}

@media screen and (max-width: 480px) {
  :deep(.el-dialog) {
    width: 100% !important;
  }
}
</style>