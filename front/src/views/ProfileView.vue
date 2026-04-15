<template>
  <div class="profile-view">
    <h1>👤 个人中心</h1>
    <p>个人信息管理 - 开发中...</p>
    <el-button type="primary" @click="$router.push('/')">
      返回首页
    </el-button>
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 个人中心组件 - 待开发
</script>

<style scoped>
.profile-view {
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
