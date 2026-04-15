<!-- src/views/error/NotFound.vue -->
<template>
  <div class="error-page">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">
      返回首页
    </el-button>
  </div>
</template>

<script setup lang="ts">
// 404 错误页面
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

h1 {
  font-size: 72px;
  color: #f59e0b;
  margin: 0;
}

p {
  font-size: 18px;
  color: #94a3b8;
}
</style>
