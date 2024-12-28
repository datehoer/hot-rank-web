<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>

export default {
  name: "App",
  metaInfo: {
    script: [
      {
        src: 'https://cloud.umami.is/script.js',
        defer: true,
        'data-website-id': '24595aed-c7d3-4407-9ce1-e3d54b58bf00'
      }
    ],
    meta: [
      { name: 'description', content: '全网热门信息聚合，每小时自动更新' }
    ]
  }
};
</script>
<style scoped>
#app .theme-picker {
  display: none;
}
</style>
