<!-- front/src/layouts/AdminLayout.vue -->
<template>
  <div class="admin-layout">
    <el-container class="admin-container">
      <!-- 左侧菜单栏 -->
      <el-aside width="200px" class="admin-aside">
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/admin/tag-categories">
            <el-icon><FolderOpened /></el-icon>
            <span>标签分类</span>
          </el-menu-item>
          <el-menu-item index="/admin/tags">
            <el-icon><PriceTag /></el-icon>
            <span>标签管理</span>
          </el-menu-item>
          <!-- 预留其他管理模块入口 -->
          <!--
          <el-menu-item index="/admin/audit" disabled>
            <el-icon><DocumentChecked /></el-icon>
            <span>审核管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/blacklist" disabled>
            <el-icon><CircleClose /></el-icon>
            <span>黑名单管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/stats" disabled>
            <el-icon><DataAnalysis /></el-icon>
            <span>系统统计</span>
          </el-menu-item>
          -->
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FolderOpened, PriceTag } from '@element-plus/icons-vue'

const route = useRoute()

// 计算属性
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.admin-layout {
  height: calc(100vh - 73px);
  display: flex;
}

.admin-container {
  height: 100%;
  width: 100%;
}

.admin-aside {
  background-color: #304156;
  height: 100%;
  overflow-y: auto;
  flex-shrink: 0;
}

.admin-aside .el-menu {
  border-right: none;
}

.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  flex: 1;
}
</style>
