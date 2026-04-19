<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="logo" @click="$router.push('/')">
        <span class="logo-icon">☁</span>
        <span class="logo-text">云藏</span>
      </div>

      <div class="header-actions">
        <el-button text @click="$router.push('/official')">
          官方分享
        </el-button>

        <template v-if="userStore.isLoggedIn">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-menu">
              <el-avatar :size="32" :src="userAvatar" class="avatar">
                {{ getDisplayName(userStore.username) }}
              </el-avatar>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="bookmarks">
                  <el-icon><Collection /></el-icon>
                  我的收藏
                </el-dropdown-item>
                <el-dropdown-item command="stats">
                  <el-icon><DataAnalysis /></el-icon>
                  数据统计
                </el-dropdown-item>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="userStore.isAdmin"
                  divided
                  command="admin"
                >
                  <el-icon><Setting /></el-icon>
                  管理员后台
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <template v-else>
          <el-button type="primary" @click="openLoginDialog">
            登录 / 注册
          </el-button>
        </template>
      </div>
    </header>

    <main class="app-content">
      <router-view />
    </main>

    <LoginDialog ref="loginDialogRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Collection,
  DataAnalysis,
  ArrowDown,
  User,
  SwitchButton,
  Setting,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import LoginDialog from '@/components/LoginDialog.vue'

const router = useRouter()
const userStore = useUserStore()

const loginDialogRef = ref<InstanceType<typeof LoginDialog>>()

// 监听 store 中的登录弹窗触发状态
watch(() => userStore.shouldShowLoginDialog, (shouldShow) => {
  if (shouldShow) {
    loginDialogRef.value?.open()
    userStore.closeLoginDialog()
  }
})

const userAvatar = computed(() => {
  const avatar = userStore.userInfo?.avatar
  if (!avatar) return ''

  if (avatar.startsWith('http')) return avatar

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  const baseWithoutApi = baseUrl.replace('/api/v1', '')
  return `${baseWithoutApi}${avatar}`
})

const getDisplayName = (username: string) => {
  if (!username) return ''
  const chineseMatch = username.match(/[\u4e00-\u9fa5]/)
  if (chineseMatch) {
    return chineseMatch[0]
  }
  return username.charAt(0).toUpperCase()
}

const openLoginDialog = () => {
  loginDialogRef.value?.open()
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'bookmarks':
      router.push('/my/bookmarks')
      break
    case 'stats':
      router.push('/stats')
      break
    case 'profile':
      router.push('/profile')
      break
    case 'admin':
      router.push('/admin/tags')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/')
    })
    .catch(() => {
    })
}

onMounted(() => {
  userStore.restoreFromStorage()
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0f1923;
}

.app-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 40px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 700;
  color: #818cf8;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-icon {
  font-size: 28px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.12);
}

.avatar {
  background: linear-gradient(135deg, #6366f1, #a78bfa);
}

.app-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>

<style>
.el-input__wrapper {
  background: #FFFFFF !important;
  border-radius: 10px;
  padding: 10px 14px;
  transition: all 0.2s ease;
  border: 1px solid #E2E8F0;
  box-shadow: none !important;
}

.el-input__wrapper:hover {
  border-color: #CBD5E1;
}

.el-input__wrapper.is-focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.el-input__wrapper.is-error {
  border-color: #EF4444;
  box-shadow: none !important;
}

.el-input__inner {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 14px;
  color: #1E293B;
  font-weight: 400;
  border: none !important;
  box-shadow: none !important;
}

.el-input__inner::placeholder {
  color: #94A3B8;
  font-weight: 400;
}

.el-input__clear,
.el-input__suffix-inner {
  color: #94A3B8;
}

.el-form-item__error {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 12px;
  color: #EF4444;
  padding-top: 4px;
}

.dark .el-input__wrapper,
.el-input__wrapper {
  background: #FFFFFF !important;
}

.dark .el-input__inner,
.el-input__inner {
  color: #1E293B !important;
}

.dark .el-input__inner::placeholder,
.el-input__inner::placeholder {
  color: #94A3B8 !important;
}
</style>
