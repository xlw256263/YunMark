<template>
  <div class="profile-page">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/dashboard" class="back-btn">
          <i class="icon-back">←</i>
          返回
        </router-link>
        <h2>个人中心</h2>
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
        <div class="profile-container">
          <div class="profile-header">
            <div class="avatar">
              <i class="user-avatar">👤</i>
            </div>
            <div class="user-info">
              <h3>{{ userInfo.username }}</h3>
              <p>{{ userInfo.email }}</p>
              <div class="stats">
                <div class="stat-item">
                  <span class="stat-number">{{ stats.totalWebsites }}</span>
                  <span class="stat-label">浏览网站</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ stats.totalFavorites }}</span>
                  <span class="stat-label">收藏数量</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ stats.joinDays }}</span>
                  <span class="stat-label">加入天数</span>
                </div>
              </div>
            </div>
          </div>

          <div class="profile-tabs">
            <div class="tab" :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">
              个人信息
            </div>
            <div class="tab" :class="{ active: activeTab === 'security' }" @click="activeTab = 'security'">
              安全设置
            </div>
            <div class="tab" :class="{ active: activeTab === 'preferences' }" @click="activeTab = 'preferences'">
              偏好设置
            </div>
          </div>

          <div class="tab-content">
            <!-- 个人信息标签页 -->
            <div v-if="activeTab === 'info'" class="tab-pane">
              <div class="form-group">
                <label>用户名</label>
                <input v-model="userInfo.username" type="text" class="form-control" disabled />
              </div>
              <div class="form-group">
                <label>邮箱地址</label>
                <input v-model="userInfo.email" type="email" class="form-control" disabled />
              </div>
              <div class="form-group">
                <label>简介</label>
                <textarea v-model="userInfo.bio" class="form-control" rows="3" placeholder="介绍一下自己..."></textarea>
              </div>
              <div class="form-group">
                <label>网站</label>
                <input v-model="userInfo.website" type="url" class="form-control" placeholder="https://your-website.com" />
              </div>
              <button class="btn btn-primary" @click="saveInfo">保存信息</button>
            </div>

            <!-- 安全设置标签页 -->
            <div v-if="activeTab === 'security'" class="tab-pane">
              <div class="form-group">
                <label>当前密码</label>
                <input type="password" class="form-control" placeholder="输入当前密码" />
              </div>
              <div class="form-group">
                <label>新密码</label>
                <input type="password" class="form-control" placeholder="输入新密码" />
              </div>
              <div class="form-group">
                <label>确认新密码</label>
                <input type="password" class="form-control" placeholder="再次输入新密码" />
              </div>
              <button class="btn btn-primary" @click="changePassword">更改密码</button>
            </div>

            <!-- 偏好设置标签页 -->
            <div v-if="activeTab === 'preferences'" class="tab-pane">
              <div class="form-group">
                <label>主题偏好</label>
                <select v-model="preferences.theme" class="form-control">
                  <option value="light">明亮模式</option>
                  <option value="dark">暗黑模式</option>
                  <option value="auto">跟随系统</option>
                </select>
              </div>
              <div class="form-group">
                <label>通知设置</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input v-model="preferences.notifications.email" type="checkbox" />
                    邮件通知
                  </label>
                  <label class="checkbox-label">
                    <input v-model="preferences.notifications.push" type="checkbox" />
                    应用推送
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label>隐私设置</label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input v-model="preferences.privacy.publicProfile" type="checkbox" />
                    公开个人资料
                  </label>
                  <label class="checkbox-label">
                    <input v-model="preferences.privacy.showActivity" type="checkbox" />
                    显示活动记录
                  </label>
                </div>
              </div>
              <button class="btn btn-primary" @click="savePreferences">保存设置</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = computed(() => userStore.username)
const activeTab = ref('info')

// 用户信息
const userInfo = reactive({
  username: userStore.username,
  email: userStore.email,
  bio: '热爱互联网，喜欢探索新网站',
  website: ''
})

// 统计信息
const stats = reactive({
  totalWebsites: 42,
  totalFavorites: 12,
  joinDays: 15
})

// 偏好设置
const preferences = reactive({
  theme: 'light',
  notifications: {
    email: true,
    push: false
  },
  privacy: {
    publicProfile: false,
    showActivity: true
  }
})

const logout = () => {
  userStore.logout()
  router.push('/')
}

const saveInfo = () => {
  alert('个人信息已保存')
}

const changePassword = () => {
  alert('密码更改功能将在后续版本中实现')
}

const savePreferences = () => {
  alert('偏好设置已保存')
}
</script>

<style scoped>
.profile-page {
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

.profile-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  font-size: 32px;
}

.user-info h3 {
  margin: 0 0 5px 0;
  font-size: 24px;
}

.user-info p {
  margin: 0 0 15px 0;
  opacity: 0.9;
}

.stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
}

.profile-tabs {
  display: flex;
  border-bottom: 1px solid #eee;
}

.tab {
  padding: 15px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab:hover {
  background: #f5f7fa;
}

.tab.active {
  border-bottom: 2px solid #4a90e2;
  color: #4a90e2;
  background: #f5f7fa;
}

.tab-content {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #4a90e2;
}

.form-control[disabled] {
  background: #f5f7fa;
  cursor: not-allowed;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #4a90e2;
  color: white;
}

.btn-primary:hover {
  background: #357abd;
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

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 15px;
    padding: 30px 20px;
  }

  .stats {
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
  }

  .profile-tabs {
    overflow-x: auto;
  }
}
</style>