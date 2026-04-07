<template>
  <div class="dashboard">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-left">
        <h2>私人精品网页推荐</h2>
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
        <div class="section-title">
          <h3>精选推荐</h3>
        </div>

        <div class="recommendations-grid">
          <div
            v-for="item in recommendations"
            :key="item.id"
            class="recommendation-card"
            @click="goToWebsite(item.url)"
          >
            <div class="card-image">
              <img :src="item.image" :alt="item.title" />
            </div>
            <div class="card-content">
              <h4>{{ item.title }}</h4>
              <p class="description">{{ item.description }}</p>
              <div class="tags">
                <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
              <div class="actions">
                <button class="btn btn-small btn-outline" @click.stop="addToFavorites(item)">
                  {{ item.isFavorite ? '已收藏' : '收藏' }}
                </button>
                <span class="views">{{ item.views }} 次访问</span>
              </div>
            </div>
          </div>
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

// 示例推荐数据
const recommendations = ref([
  {
    id: 1,
    title: 'GitHub',
    description: '全球最大的代码托管平台，开发者必备工具',
    image: 'https://via.placeholder.com/300x200/4a90e2/ffffff?text=GitHub',
    url: 'https://github.com',
    tags: ['编程', '开源', '协作'],
    views: 1234,
    isFavorite: false
  },
  {
    id: 2,
    title: 'Stack Overflow',
    description: '程序员问答社区，解决技术难题的好地方',
    image: 'https://via.placeholder.com/300x200/f5a623/ffffff?text=Stack+Overflow',
    url: 'https://stackoverflow.com',
    tags: ['编程', '问答', '技术'],
    views: 987,
    isFavorite: true
  },
  {
    id: 3,
    title: 'Dribbble',
    description: '设计师作品展示平台，寻找设计灵感',
    image: 'https://via.placeholder.com/300x200/d0021b/ffffff?text=Dribbble',
    url: 'https://dribbble.com',
    tags: ['设计', '灵感', '创意'],
    views: 756,
    isFavorite: false
  },
  {
    id: 4,
    title: 'Product Hunt',
    description: '发现新产品，分享创业想法的社区',
    image: 'https://via.placeholder.com/300x200/4a90e2/ffffff?text=Product+Hunt',
    url: 'https://www.producthunt.com',
    tags: ['产品', '创业', '科技'],
    views: 634,
    isFavorite: false
  },
  {
    id: 5,
    title: 'Behance',
    description: 'Adobe旗下的设计师作品展示平台',
    image: 'https://via.placeholder.com/300x200/1769ff/ffffff?text=Behance',
    url: 'https://www.behance.net',
    tags: ['设计', '作品', '创意'],
    views: 523,
    isFavorite: true
  },
  {
    id: 6,
    title: 'Medium',
    description: '高质量文章分享平台，学习各种知识',
    image: 'https://via.placeholder.com/300x200/000000/ffffff?text=Medium',
    url: 'https://medium.com',
    tags: ['写作', '学习', '知识'],
    views: 892,
    isFavorite: false
  }
])

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
</script>

<style scoped>
.dashboard {
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

.section-title {
  margin-bottom: 20px;
}

.section-title h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.recommendation-card:hover {
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

.tags {
  margin-bottom: 10px;
}

.tag {
  display: inline-block;
  background: #f0f2f5;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-right: 5px;
  margin-bottom: 5px;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.views {
  color: #999;
  font-size: 12px;
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

.btn-small {
  padding: 4px 12px;
  font-size: 12px;
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

  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}
</style>