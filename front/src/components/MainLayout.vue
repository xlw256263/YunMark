// front/src/components/MainLayout.vue
<template>
  <div class="main-layout">
    <nav class="navbar">
      <div class="nav-left">
        <slot name="nav-left">
          <h2>云藏·智能收藏夹</h2>
        </slot>
      </div>
      <div class="nav-right">
        <span class="welcome">欢迎, {{ username }}</span>
        <el-avatar
          :size="36"
          :src="userAvatar || undefined"
          class="nav-avatar"
          @click="$router.push('/profile')"
        >
          {{ username?.charAt(0)?.toUpperCase() }}
        </el-avatar>
        <button class="btn btn-outline" @click="handleLogout">退出登录</button>
      </div>
    </nav>

    <div class="main-content">
      <aside class="sidebar">
        <div
          v-for="item in menuItems"
          :key="item.path || item.id"
          class="menu-item"
          :class="{ active: isActive(item) }"
          @click="handleMenuClick(item)"
        >
          <span class="icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </div>

        <slot name="sidebar"></slot>
      </aside>

      <main class="content">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useBookmarkStore } from '@/stores/bookmark.js'
import { ElAvatar } from 'element-plus'

const props = defineProps({
  menuItems: {
    type: Array,
    default: () => []
  },
  showDefaultMenu: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['logout'])

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const bookmarkStore = useBookmarkStore()

const username = computed(() => userStore.username)
const categories = computed(() => bookmarkStore.categories)

const userAvatar = computed(() => {
  try {
    const avatar = userStore.userInfo?.avatar

    if (!avatar) {
      return ''
    }

    if (avatar.startsWith('http')) {
      return avatar
    }

    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

    if (avatar.startsWith('/uploads')) {
      const apiBaseUrl = baseUrl.replace('/api/v1', '')
      return `${apiBaseUrl}${avatar}`
    }

    return `${baseUrl}${avatar}`
  } catch (error) {
    console.error('[MainLayout] Avatar URL error:', error)
    return ''
  }
})

const defaultMenuItems = computed(() => {
  const items = [
    { path: '/dashboard', label: '首页', icon: '🏠' },
    ...categories.value.map(cat => ({
      id: cat.id,
      label: cat.name,
      icon: '📁',
      action: () => router.push(`/favorites?category=${cat.id}`)
    })),
    { path: '/favorites', label: '全部收藏', icon: '❤️' },
    { path: '/profile', label: '个人中心', icon: '👤' }
  ]
  return items
})

const displayMenuItems = computed(() => {
  if (props.showDefaultMenu) {
    return props.menuItems.length > 0 ? props.menuItems : defaultMenuItems.value
  }
  return props.menuItems
})

const isActive = (item) => {
  if (item.path) {
    return route.path === item.path
  }
  return false
}

const handleMenuClick = (item) => {
  if (item.action) {
    item.action()
  } else if (item.path) {
    router.push(item.path)
  }
}

const handleLogout = () => {
  userStore.logout()
  bookmarkStore.resetState()
  emit('logout')
  router.push('/')
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left h2 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome {
  color: #666;
  font-size: 14px;
}

.nav-avatar {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e5e7eb;
}

.nav-avatar:hover {
  transform: scale(1.1);
  border-color: #667eea;
}

.main-content {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #eee;
  height: calc(100vh - 60px);
  position: fixed;
  top: 60px;
  left: 0;
  overflow-y: auto;
}

.menu-item {
  padding: 12px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #666;
  transition: all 0.3s;
  padding: 8px 12px;
  border-radius: 5px;
}

.menu-item:hover {
  background: #f5f7fa;
  color: #4a90e2;
}

.menu-item.active {
  background: #4a90e2;
  color: white;
}

.icon {
  margin-right: 8px;
}

.content {
  flex: 1;
  margin-left: 220px;
  padding: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-outline {
  background: transparent;
  border: 1px solid #ddd;
  color: #666;
}

.btn-outline:hover {
  background: #f5f7fa;
  border-color: #4a90e2;
  color: #4a90e2;
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .menu-item span:last-child {
    display: none;
  }

  .content {
    margin-left: 60px;
  }
}
</style>
