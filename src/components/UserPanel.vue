<template>
  <div class="user-panel">
    <div class="user-info">
      <div class="avatar">
        <span class="avatar-text">无名</span>
      </div>
      <div class="login-tip">{{tip}}</div>
      <div class="online-count">在线人数人数: {{ onlineCount }}</div>
    </div>
    <div class="quote-card">
      <div class="quote-content">
        {{ quoteContent }}
      </div>
      <div class="quote-source">
        {{ quoteSource }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserPanel',
  data() {
    return {
      tip: "今天也要加油哦！",
      onlineCount: '1082',
      quoteContent: '摸鱼诗篇：今天是10月28日，周一的中午工作时刻，一定不要忘记偷偷咪咪的摸鱼哦，午饭后溜达走一走，永不悔，去廊桥走走，飞起，看看外面的世界，但生命是自己的。',
      quoteSource: '《致每位鱼友的一封信》   《驱动石单文》'
    }
  }
}
</script>

<style scoped>
.user-panel {
  position: fixed;
  right: 20px;
  top: 80px;
  width: 300px;
}

.user-info {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 20px;
  text-align: center;
  margin-bottom: 16px;
}

.avatar {
  width: 60px;
  height: 60px;
  background-color: #6B9EFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.avatar-text {
  color: #fff;
  font-size: 16px;
}

.login-tip {
  color: #909399;
  font-size: 12px;
  margin-bottom: 8px;
}

.online-count {
  color: #909399;
  font-size: 12px;
}

.quote-card {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 16px;
}

.quote-content {
  color: #E5EAF3;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.quote-source {
  color: #909399;
  font-size: 12px;
  text-align: right;
}
</style>
