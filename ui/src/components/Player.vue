<template>
  <div class="music-player">
    <div class="current-player">
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
          </div>
        </div>
        <div v-loading="isLoading" element-loading-text="加载音频中...">
          <audio ref="audioPlayer" @ended="handleTrackEnd"></audio>
        </div>
      </el-card>
    </div>

    <div class="track-list">
      <el-row :gutter="20">
        <el-col 
          :span="6" 
          v-for="(track, index) in tracks" 
          :key="index"
          class="track-item"
        >
          <div 
            :title="currentTrack.title"
            class="album-container"
            :class="{ 'active': currentTrack.id === track.id }"
            @click="selectTrack(track)"
          >
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
    </div>
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
      audio: null
    }
  },
  created() {
    // 确保在组件创建时设置默认曲目
    this.currentTrack = this.tracks[0]
    this.getMusic()
  },
  mounted() {
    this.$nextTick(() => {
      this.audio = this.$refs.audioPlayer
      if (this.audio && this.currentTrack) {
        this.audio.src = this.currentTrack.url
      }
    })
  },
  methods: {
    getMusic() {
      getMusic().then(res => {
        this.tracks = res.data
      })
    },
    async togglePlay() {
      if (!this.audio) return

      try {
        this.isLoading = true
        if (this.isPlaying) {
          await this.audio.pause()
        } else {
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
      if (!this.audio) return
      
      // 如果选择了不��的曲目
      if(this.currentTrack.id !== track.id) {
        this.currentTrack = track
        this.audio.src = track.url
        if (this.isPlaying) {
          this.audio.play()
        }
      }
    },
    handleTrackEnd() {
      this.isPlaying = false
      // Optional: Auto-play next track
      const currentIndex = this.tracks.findIndex(t => t.id === this.currentTrack.id)
      const nextIndex = (currentIndex + 1) % this.tracks.length
      this.selectTrack(this.tracks[nextIndex])
      this.togglePlay()
    }
  }
}
</script>

<style scoped>
.music-player {
  padding: 20px;
  background-color: #2b2b2b;
  min-height: 30vh;
}

.current-player {
  margin-bottom: 40px;
}

.player-card {
  background-color: #333;
  border-radius: 8px;
  width: 300px;
  margin: 0 auto;
  overflow: visible;
  padding-top: 20px;
  border: none;
}

.vinyl-player {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 唱片样式 */
.vinyl {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  background: #000;
  background: repeating-radial-gradient(
    circle at center,
    #000000,
    #000000 2px,
    #171717 3px,
    #171717 4px
  );
  margin: 0 auto;
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
  border: 15px solid #fff;
  box-shadow: 0 0 0 2px #000;
}

/* 唱片指针样式 */
.tonearm-wrapper {
  position: absolute;
  top: -20px;
  right: 20px;
  width: 120px;
  height: 120px;
  z-index: 10;
}

/* 播放列表样式 */
.track-list {
  padding: 20px;
}

.track-item {
  margin-bottom: 20px;
}

.album-container {
  position: relative;
  height: 80px;
  width: 80px;
  cursor: pointer;
  overflow: hidden;
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

.track-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-disc {
  position: absolute;
  top: 10%;
  right: -60%;
  width: 80%;
  height: 80%;
  border-radius: 50%;
  background: #000;
  background: repeating-radial-gradient(
    circle at center,
    #000000,
    #000000 2px,
    #171717 3px,
    #171717 4px
  );
  transition: transform 0.3s ease;
  z-index: 1;
}

.disc-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40%;
  height: 40%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  overflow: hidden;
  border: 8px solid #fff;
}

.disc-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 悬浮效果 */
.album-container:hover .album-disc {
  transform: translateX(-70%);
}

/* 当前选中的唱片 */
.active .album-disc {
  transform: translateX(-70%);
}

.active .album-cover-wrapper {
  box-shadow: 0 0 20px rgba(64, 158, 255, 0.5);
}

/* 播放动画 */
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.vinyl.is-playing {
  animation: rotate 20s linear infinite;
}

/* 控制按钮样式 */
.controls {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
  .el-col {
    width: 100%;
  }
  
  .album-container {
    height: 150px;
  }
}

/* 唱臂包装器 */
.tonearm-wrapper {
  position: absolute;
  top: -20px;
  right: 20px;
  width: 120px;
  height: 120px;
  z-index: 10;
}

/* 唱臂基座 */
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

/* 唱臂主体 */
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

/* 唱臂主体部分 */
.tonearm-body {
  position: relative;
  width: 6px;
  height: 80px;
  background: linear-gradient(90deg, #333, #666);
  border-radius: 3px;
  box-shadow: -1px 2px 3px rgba(0, 0, 0, 0.2);
}

/* 唱针头部 */
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

/* 唱针尖 */
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

/* 优化唱臂基座的金属质感 */
.tonearm-base::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #888;
  border-radius: 50%;
  border: 2px solid #777;
}

</style>