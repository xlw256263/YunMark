<template>
  <div class="official-view">
    <h1>🌟 官方分享</h1>
    <p>官方精选内容 - 开发中...</p>
    <el-button type="primary" @click="$router.push('/')">
      返回首页
    </el-button>
  </div>
</template>

<script setup lang="ts">
// 官方分享页组件 - 待开发
</script>

<style scoped>
.official-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

h1 {
  font-size: 36px;
  color: #818cf8;
}

p {
  font-size: 18px;
  color: #94a3b8;
}
</style>
