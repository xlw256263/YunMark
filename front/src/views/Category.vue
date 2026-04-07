<template>
  <div class="category-page">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/dashboard" class="back-btn">
          <i class="icon-back">←</i>
          返回
        </router-link>
        <h2>{{ categoryName }}分类</h2>
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
        <div class="menu-item" :class="{ active: currentCategory === 'tech' }">
          <router-link to="/category/tech">
            <i class="icon-category"></i>
            技术
          </router-link>
        </div>
        <div class="menu-item" :class="{ active: currentCategory === 'design' }">
          <router-link to="/category/design">
            <i class="icon-category"></i>
            设计
          </router-link>
        </div>
        <div class="menu-item" :class="{ active: currentCategory === 'life' }">
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
        <div class="category-header">
          <h3>{{ categoryName }}类精选网站</h3>
          <div class="filters">
            <select v-model="sortBy" class="filter-select">
              <option value="popular">最热门</option>
              <option value="newest">最新</option>
              <option value="alphabetical">按名称</option>
            </select>
          </div>
        </div>

        <div class="category-grid">
          <div
            v-for="item in filteredItems"
            :key="item.id"
            class="category-card"
            @click="goToWebsite(item.url)"
          >
            <div class="card-image">
              <img :src="item.image" :alt="item.title" />
            </div>
            <div class="card-content">
              <h4>{{ item.title }}</h4>
              <p class="description">{{ item.description }}</p>
              <div class="stats">
                <span class="rating">
                  ⭐ {{ item.rating }}
                </span>
                <span class="views">
                  👁️ {{ item.views }} 次访问
                </span>
              </div>
              <div class="actions">
                <button class="btn btn-small btn-outline" @click.stop="addToFavorites(item)">
                  {{ item.isFavorite ? '已收藏' : '收藏' }}
                </button>
                <button class="btn btn-small btn-outline" @click.stop="shareItem(item)">
                  分享
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="filteredItems.length === 0" class="empty-state">
          <p>该分类下暂无推荐网站</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentCategory = computed(() => route.params.id)
const username = computed(() => userStore.username)

const sortBy = ref('popular')

// 分类名称映射
const categoryNames = {
  tech: '技术',
  design: '设计',
  life: '生活'
}

const categoryName = computed(() => categoryNames[currentCategory.value] || '未知')

// 示例分类数据
const categoryData = {
  tech: [
    {
      id: 1,
      title: 'GitHub',
      description: '全球最大的代码托管平台，开发者必备工具',
      image: 'https://via.placeholder.com/300x200/4a90e2/ffffff?text=GitHub',
      url: 'https://github.com',
      rating: 4.9,
      views: 1234,
      isFavorite: false,
      tags: ['编程', '开源', '协作']
    },
    {
      id: 2,
      title: 'Stack Overflow',
      description: '程序员问答社区，解决技术难题的好地方',
      image: 'https://via.placeholder.com/300x200/f5a623/ffffff?text=Stack+Overflow',
      url: 'https://stackoverflow.com',
      rating: 4.8,
      views: 987,
      isFavorite: true,
      tags: ['编程', '问答', '技术']
    },
    {
      id: 3,
      title: 'MDN Web Docs',
      description: 'Web开发权威文档，学习HTML、CSS、JavaScript',
      image: 'https://via.placeholder.com/300x200/000000/ffffff?text=MDN',
      url: 'https://developer.mozilla.org',
      rating: 4.9,
      views: 856,
      isFavorite: false,
      tags: ['前端', '文档', '学习']
    },
    {
      id: 4,
      title: 'Dev.to',
      description: '开发者社区，分享技术文章和经验',
      image: 'https://via.placeholder.com/300x200/0a0a0a/ffffff?text=DEV',
      url: 'https://dev.to',
      rating: 4.6,
      views: 723,
      isFavorite: false,
      tags: ['博客', '社区', '分享']
    }
  ],
  design: [
    {
      id: 5,
      title: 'Dribbble',
      description: '设计师作品展示平台，寻找设计灵感',
      image: 'https://via.placeholder.com/300x200/d0021b/ffffff?text=Dribbble',
      url: 'https://dribbble.com',
      rating: 4.7,
      views: 756,
      isFavorite: false,
      tags: ['设计', '灵感', '创意']
    },
    {
      id: 6,
      title: 'Behance',
      description: 'Adobe旗下的设计师作品展示平台',
      image: 'https://via.placeholder.com/300x200/1769ff/ffffff?text=Behance',
      url: 'https://www.behance.net',
      rating: 4.6,
      views: 634,
      isFavorite: true,
      tags: ['设计', '作品', '创意']
    },
    {
      id: 7,
      title: 'Awwwards',
      description: '网页设计奖项，欣赏优秀网站设计',
      image: 'https://via.placeholder.com/300x200/ff6b35/ffffff?text=Awwwards',
      url: 'https://www.awwwards.com',
      rating: 4.8,
      views: 589,
      isFavorite: false,
      tags: ['设计', '灵感', '网页']
    }
  ],
  life: [
    {
      id: 8,
      title: 'Medium',
      description: '高质量文章分享平台，学习各种知识',
      image: 'https://via.placeholder.com/300x200/000000/ffffff?text=Medium',
      url: 'https://medium.com',
      rating: 4.5,
      views: 892,
      isFavorite: false,
      tags: ['写作', '学习', '知识']
    },
    {
      id: 9,
      title: 'TED Talks',
      description: '启发性演讲，拓展视野和思维',
      image: 'https://via.placeholder.com/300x200/e62b1e/ffffff?text=TED',
      url: 'https://www.ted.com',
      rating: 4.9,
      views: 1203,
      isFavorite: true,
      tags: ['演讲', '知识', '启发']
    },
    {
      id: 10,
      title: 'Coursera',
      description: '在线课程平台，学习各种技能',
      image: 'https://via.placeholder.com/300x200/0056d3/ffffff?text=Coursera',
      url: 'https://www.coursera.org',
      rating: 4.7,
      views: 678,
      isFavorite: false,
      tags: ['学习', '课程', '教育']
    }
  ]
}

const items = computed(() => categoryData[currentCategory.value] || [])

const filteredItems = computed(() => {
  let result = [...items.value]

  // 排序
  switch(sortBy.value) {
    case 'popular':
      result.sort((a, b) => b.views - a.views)
      break
    case 'newest':
      result.sort((a, b) => b.id - a.id)
      break
    case 'alphabetical':
      result.sort((a, b) => a.title.localeCompare(b.title))
      break
  }

  return result
})

const logout = () => {
  userStore.logout()
  router.push('/')
}

const goToWebsite = (url) => {
  window.open(url, '_blank')
}

const addToFavorites = (item) => {
  item.isFavorite = !item.isFavorite
  if (item.isFavorite) {
    alert(`已收藏 ${item.title}`)
  } else {
    alert(`已取消收藏 ${item.title}`)
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

// 监听路由变化
watch(currentCategory, (newCategory) => {
  if (!categoryNames[newCategory]) {
    router.push('/dashboard')
  }
})
</script>

<style scoped>
.category-page {
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

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-header h3 {
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

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.category-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.category-card:hover {
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

.card-content h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
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
  margin-bottom: 10px;
  font-size: 12px;
  color: #666;
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
  flex: 1;
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

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
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

  .category-grid {
    grid-template-columns: 1fr;
  }

  .category-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>