<template>
  <div class="favorites-page">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/dashboard" class="back-btn">
          <i class="icon-back">←</i>
          返回
        </router-link>
        <h2>我的收藏</h2>
      </div>
      <div class="nav-right">
        <span class="welcome">欢迎, {{ username }}</span>
        <button class="btn btn-outline" @click="logout">退出登录</button>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="menu-item" :class="{ active: $route.name === 'Dashboard' }">
          <router-link to="/dashboard">
            <i class="icon-home"></i>
            首页
          </router-link>
        </div>
        <div class="menu-item">
          <router-link to="/category/tech">
            <i class="icon-category"></i>
            技术
          </router-link>
        </div>
        <div class="menu-item">
          <router-link to="/category/design">
            <i class="icon-category"></i>
            设计
          </router-link>
        </div>
        <div class="menu-item">
          <router-link to="/category/life">
            <i class="icon-category"></i>
            生活
          </router-link>
        </div>
        <div class="menu-item" :class="{ active: $route.name === 'Favorites' }">
          <router-link to="/favorites">
            <i class="icon-favorite"></i>
            收藏
          </router-link>
        </div>
        <div class="menu-item" :class="{ active: $route.name === 'Profile' }">
          <router-link to="/profile">
            <i class="icon-user"></i>
            个人中心
          </router-link>
        </div>
      </aside>

      <!-- 内容区 -->
      <main class="content">
        <div class="favorites-header">
          <h3>我的收藏夹 ({{ favorites.length }})</h3>
          <div class="filters">
            <select v-model="sortBy" class="filter-select">
              <option value="recent">最近收藏</option>
              <option value="popular">最受欢迎</option>
              <option value="alphabetical">按名称排序</option>
            </select>
          </div>
        </div>

        <div v-if="favorites.length > 0" class="favorites-grid">
          <div
            v-for="item in sortedFavorites"
            :key="item.id"
            class="favorite-card"
            @click="goToWebsite(item.url)"
          >
            <div class="card-image">
              <img :src="item.image" :alt="item.title" />
            </div>
            <div class="card-content">
              <div class="card-header">
                <h4>{{ item.title }}</h4>
                <button
                  class="remove-btn"
                  @click.stop="removeFromFavorites(item)"
                  title="移除收藏"
                >
                  ×
                </button>
              </div>
              <p class="description">{{ item.description }}</p>
              <div class="stats">
                <span class="category-tag">
                  {{ getCategoryName(item.category) }}
                </span>
                <span class="views">
                  👁️ {{ item.views }} 次访问
                </span>
              </div>
              <div class="tags">
                <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
              <div class="actions">
                <button class="btn btn-small btn-outline" @click.stop="shareItem(item)">
                  分享
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">❤️</div>
          <h3>暂无收藏</h3>
          <p>您还没有收藏任何网站，快去看看首页推荐吧！</p>
          <router-link to="/dashboard" class="btn btn-primary">
            去首页浏览
          </router-link>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = computed(() => userStore.username)
const sortBy = ref('recent')

// 示例收藏数据 - 在实际应用中应该从API获取
const favorites = ref([
  {
    id: 2,
    title: 'Stack Overflow',
    description: '程序员问答社区，解决技术难题的好地方',
    image: 'https://via.placeholder.com/300x200/f5a623/ffffff?text=Stack+Overflow',
    url: 'https://stackoverflow.com',
    category: 'tech',
    views: 987,
    tags: ['编程', '问答', '技术'],
    createdAt: new Date('2024-01-15')
  },
  {
    id: 5,
    title: 'Dribbble',
    description: '设计师作品展示平台，寻找设计灵感',
    image: 'https://via.placeholder.com/300x200/d0021b/ffffff?text=Dribbble',
    url: 'https://dribbble.com',
    category: 'design',
    views: 756,
    tags: ['设计', '灵感', '创意'],
    createdAt: new Date('2024-01-10')
  },
  {
    id: 9,
    title: 'TED Talks',
    description: '启发性演讲，拓展视野和思维',
    image: 'https://via.placeholder.com/300x200/e62b1e/ffffff?text=TED',
    url: 'https://www.ted.com',
    category: 'life',
    views: 1203,
    tags: ['演讲', '知识', '启发'],
    createdAt: new Date('2024-01-05')
  }
])

// 分类名称映射
const categoryNames = {
  tech: '技术',
  design: '设计',
  life: '生活'
}

const getCategoryName = (category) => {
  return categoryNames[category] || '其他'
}

const sortedFavorites = computed(() => {
  const sorted = [...favorites.value]

  switch(sortBy.value) {
    case 'recent':
      return sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    case 'popular':
      return sorted.sort((a, b) => b.views - a.views)
    case 'alphabetical':
      return sorted.sort((a, b) => a.title.localeCompare(b.title))
    default:
      return sorted
  }
})

const logout = () => {
  userStore.logout()
  router.push('/')
}

const goToWebsite = (url) => {
  window.open(url, '_blank')
}

const removeFromFavorites = (item) => {
  if (confirm(`确定要取消收藏 "${item.title}" 吗？`)) {
    const index = favorites.value.findIndex(fav => fav.id === item.id)
    if (index !== -1) {
      favorites.value.splice(index, 1)
      alert(`已取消收藏 ${item.title}`)
    }
  }
}

const shareItem = (item) => {
  if (navigator.share) {
    navigator.share({
      title: item.title,
      text: item.description,
      url: item.url
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(item.url).then(() => {
      alert('链接已复制到剪贴板')
    })
  }
}
</script>

<style scoped>
.favorites-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-left h2 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.back-btn {
  text-decoration: none;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 5px;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #f5f7fa;
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
}

.menu-item a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #666;
  transition: all 0.3s;
  padding: 8px 12px;
  border-radius: 5px;
}

.menu-item a:hover {
  background: #f5f7fa;
  color: #4a90e2;
}

.menu-item.active a {
  background: #4a90e2;
  color: white;
}

.icon-home::before {
  content: '🏠';
  margin-right: 8px;
}

.icon-category::before {
  content: '📁';
  margin-right: 8px;
}

.icon-favorite::before {
  content: '❤️';
  margin-right: 8px;
}

.icon-user::before {
  content: '👤';
  margin-right: 8px;
}

.content {
  flex: 1;
  margin-left: 220px;
  padding: 20px;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.favorites-header h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
  color: #333;
  font-size: 14px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.favorite-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
}

.favorite-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-image img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.card-content {
  padding: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.card-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  flex: 1;
  margin-right: 10px;
}

.remove-btn {
  background: #ff4757;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.remove-btn:hover {
  opacity: 0.8;
}

.description {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  margin: 0 0 10px 0;
}

.stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
}

.category-tag {
  background: #f0f2f5;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.tags {
  margin-bottom: 10px;
}

.tag {
  display: inline-block;
  background: #f0f2f5;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  margin-right: 5px;
  margin-bottom: 5px;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
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

.btn-primary {
  background: #4a90e2;
  color: white;
  text-decoration: none;
  display: inline-block;
  padding: 10px 20px;
  margin-top: 10px;
}

.btn-primary:hover {
  background: #357abd;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 20px;
}

.empty-state p {
  margin: 0 0 20px 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .menu-item a span {
    display: none;
  }

  .content {
    margin-left: 60px;
  }

  .favorites-grid {
    grid-template-columns: 1fr;
  }

  .favorites-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>